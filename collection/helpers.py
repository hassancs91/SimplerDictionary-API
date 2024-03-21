import datetime
import os
import uuid

import uuid
import boto3
import datetime
import os
import datetime
import uuid


from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

CONTABO_URL_ENDPOINT_URL = os.getenv("CONTABO_URL_ENDPOINT_URL")
CONTABO_BUCKET_NAME = os.getenv("CONTABO_BUCKET_NAME")
CONTABO_ACCESS_KEY = os.getenv("CONTABO_ACCESS_KEY")
CONTABO_SECRET_KEY = os.getenv("CONTABO_SECRET_KEY")


def generate_image_path(folder: str) -> str:
    # Get the script's directory (app/services)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the current year and month
    now = datetime.datetime.utcnow()
    year = now.year
    month = now.month

    # Use script_dir as the base and navigate to temp/ai/<folder>
    base_path = os.path.join(script_dir, "temp", "ai", folder)

    # Create the year and month subfolders if they don't exist
    year_folder = os.path.join(base_path, str(year))
    month_folder = os.path.join(year_folder, f"{month:02d}")
    os.makedirs(year_folder, exist_ok=True)
    os.makedirs(month_folder, exist_ok=True)

    # Generate a new GUID
    guid = uuid.uuid4()

    # Append the file extension (assuming you want to add an extension, e.g., .jpg, .png)
    file_name = f"{guid}.png"  # You can change the extension as per your requirement

    # Combine the folder path with the filename to create the full path of the file
    file_path = os.path.join(month_folder, file_name)
    return file_path


def save_base64_to_file(base64Image_bytes, file_path):
    with open(file_path, "wb") as f:
        f.write(base64Image_bytes)


def save_image_file_to_cloud(word, base64Image_bytes, folder):
    file_url = ""

    try:
        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Get the current year and month
        now = datetime.datetime.utcnow()
        year = now.year
        month = now.month

        # Use script_dir as the base and navigate to temp/ai/<folder>
        folder_path = os.path.join(script_dir, "temp", "ai", folder)

        # Create the year and month subfolders if they don't exist
        year_folder = os.path.join(folder_path, str(year))
        month_folder = os.path.join(year_folder, f"{month:02d}")
        os.makedirs(year_folder, exist_ok=True)
        os.makedirs(month_folder, exist_ok=True)

        # Get the file extension
        file_extension = ".png"

        # Generate a new GUID
        guid = uuid.uuid4()

        # Append the file extension
        file_name = f"{word}_{guid}{file_extension}"

        # Combine the folder path with the filename to create the full path of the file
        file_path = os.path.join(month_folder, file_name)

        save_base64_to_file(base64Image_bytes, file_path)

        _contabo_endpoint_url = CONTABO_URL_ENDPOINT_URL
        _contabo_bucket_name = CONTABO_BUCKET_NAME
        _access_key = CONTABO_ACCESS_KEY
        _secret_key = CONTABO_SECRET_KEY

        # Upload the file to the Contabo object storage bucket
        s3 = boto3.client(
            "s3",
            aws_access_key_id=_access_key,
            aws_secret_access_key=_secret_key,
            endpoint_url=_contabo_endpoint_url,
            config=boto3.session.Config(signature_version="s3v4"),
        )

        # Create a folder structure for each image
        key_name = f"pictures/{year}/{month:02d}/{file_name}"

        with open(file_path, "rb") as f:
            # Upload the file to the S3 bucket
            s3.upload_fileobj(
                f,
                _contabo_bucket_name,
                key_name,
                # ExtraArgs={"ContentType": response.headers["Content-Type"]},
            )

        file_url = f"https://pictures.simplerdictionary.com/{key_name}"

        # Delete the temporary file
        os.remove(file_path)
        return file_url
    except Exception as e:
        print(f"Error in save_image_file_st: {e}")
        return None
