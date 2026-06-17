"""
upload_to_drive.py
------------------
Upload a local file to Google Drive using the Google Drive API v3 (Python).

Based on: https://developers.google.com/workspace/drive/api/guides/manage-uploads

Prerequisites
-------------
1. Enable the Google Drive API in the Google Cloud Console.
2. Create OAuth 2.0 Client ID credentials and download them as `credentials.json`
   and place it in the same directory as this script.
3. Install required libraries:
       pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Usage
-----
    # Basic upload (uploads to My Drive root):
    python upload_to_drive.py path/to/your/file.pdf

    # Upload to a specific folder:
    python upload_to_drive.py path/to/your/file.pdf --folder-id <FOLDER_ID>

    # Upload a CSV and convert it to a Google Sheet:
    python upload_to_drive.py report.csv --convert

    # Specify a custom display name in Drive:
    python upload_to_drive.py report.csv --name "Q4 Report" --convert
"""

import argparse
import mimetypes
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Scope required to create/upload files.
# Use 'drive.file' for minimal permissions (only files created by this app).
# Use 'drive' for full access.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Path to the OAuth2 credentials file downloaded from Google Cloud Console.
CREDENTIALS_FILE = "credentials.json"

# Path where the access/refresh token will be cached after first login.
TOKEN_FILE = "token.json"

# Map common extensions to Google Workspace MIME types for conversion.
CONVERSION_MIME_MAP = {
    ".csv": "application/vnd.google-apps.spreadsheet",
    ".xlsx": "application/vnd.google-apps.spreadsheet",
    ".xls": "application/vnd.google-apps.spreadsheet",
    ".docx": "application/vnd.google-apps.document",
    ".doc": "application/vnd.google-apps.document",
    ".pptx": "application/vnd.google-apps.presentation",
    ".ppt": "application/vnd.google-apps.presentation",
    ".txt": "application/vnd.google-apps.document",
}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def get_credentials() -> Credentials:
    """
    Load cached credentials or run the OAuth2 flow if needed.

    On first run, a browser window will open asking the user to authorise
    the application. After authorisation the token is saved to `token.json`
    so subsequent runs do not require re-authentication.

    Returns:
        Authorised google.oauth2.credentials.Credentials object.
    """
    creds = None

    # Load previously saved token if it exists.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no valid credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired access token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"OAuth2 credentials file '{CREDENTIALS_FILE}' not found.\n"
                    "Download it from the Google Cloud Console:\n"
                    "  APIs & Services > Credentials > OAuth 2.0 Client IDs > Download JSON\n"
                    f"Then save it as '{CREDENTIALS_FILE}' in the same directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for subsequent runs.
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
        print(f"Token saved to '{TOKEN_FILE}'.")

    return creds


# ---------------------------------------------------------------------------
# Upload helpers
# ---------------------------------------------------------------------------

def detect_mime_type(file_path: str) -> str:
    """
    Attempt to detect the MIME type of a file by its extension.

    Falls back to 'application/octet-stream' if the type cannot be determined.

    Args:
        file_path: Path to the local file.

    Returns:
        MIME type string.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def upload_file(
    service,
    local_path: str,
    drive_name: str | None = None,
    folder_id: str | None = None,
    convert: bool = False,
    resumable: bool = True,
) -> str | None:
    """
    Upload a local file to Google Drive.

    Args:
        service:      Authorised Google Drive service object.
        local_path:   Path to the local file to upload.
        drive_name:   Display name for the file in Drive. Defaults to the
                      local filename.
        folder_id:    Google Drive folder ID to upload into. If None, the
                      file is placed in My Drive root.
        convert:      If True, convert the file to the equivalent Google
                      Workspace format (e.g. CSV to Google Sheets).
        resumable:    If True, use resumable upload (recommended for files
                      larger than 5 MB).

    Returns:
        The Drive file ID of the uploaded file, or None if the upload failed.
    """
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"Local file not found: '{local_path}'")

    # Resolve display name.
    name = drive_name or os.path.basename(local_path)

    # Build file metadata.
    file_metadata: dict = {"name": name}

    if folder_id:
        file_metadata["parents"] = [folder_id]

    # Determine conversion target MIME type (if requested).
    if convert:
        ext = os.path.splitext(local_path)[1].lower()
        target_mime = CONVERSION_MIME_MAP.get(ext)
        if target_mime:
            file_metadata["mimeType"] = target_mime
            print(f"Converting '{ext}' to Google Workspace type: {target_mime}")
        else:
            print(
                f"Warning: No Google Workspace conversion mapping found for '{ext}'. "
                "Uploading without conversion."
            )

    # Detect source MIME type.
    source_mime = detect_mime_type(local_path)

    # Create the MediaFileUpload object.
    media = MediaFileUpload(local_path, mimetype=source_mime, resumable=resumable)

    print(f"Uploading '{local_path}' ({source_mime}) -> Drive name: '{name}' ...")

    try:
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
            .execute()
        )

        file_id = file.get("id")
        file_name = file.get("name")
        web_link = file.get("webViewLink", "N/A")

        print("Upload successful!")
        print(f"   File name : {file_name}")
        print(f"   File ID   : {file_id}")
        print(f"   View link : {web_link}")

        return file_id

    except HttpError as error:
        print(f"An error occurred during upload: {error}")
        return None


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a local file to Google Drive using the Drive API v3.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="Path to the local file to upload.",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Display name for the file in Google Drive. "
             "Defaults to the local filename.",
    )
    parser.add_argument(
        "--folder-id",
        default=None,
        metavar="FOLDER_ID",
        help="Google Drive folder ID to upload the file into. "
             "Find it in the URL when you open the folder: "
             "drive.google.com/drive/folders/<FOLDER_ID>",
    )
    parser.add_argument(
        "--convert",
        action="store_true",
        help="Convert the file to the equivalent Google Workspace format "
             "(e.g. .csv to Google Sheets, .docx to Google Docs).",
    )
    parser.add_argument(
        "--no-resumable",
        action="store_true",
        help="Disable resumable upload (not recommended for large files).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 1. Authenticate.
    print("Authenticating with Google Drive...")
    creds = get_credentials()

    # 2. Build the Drive service.
    service = build("drive", "v3", credentials=creds)

    # 3. Upload the file.
    upload_file(
        service=service,
        local_path=args.file,
        drive_name=args.name,
        folder_id=args.folder_id,
        convert=args.convert,
        resumable=not args.no_resumable,
    )


if __name__ == "__main__":
    main()
