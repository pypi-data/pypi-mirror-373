import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from azure.storage.blob import BlobServiceClient, ContentSettings
from fastapi import UploadFile
from uuid import UUID, uuid4


class CommonService:
    @staticmethod
    async def send_email(data):
        try:
            SMTP_SERVER = data.get("SMTP_SERVER")
            SMTP_PORT = data.get("SMTP_PORT")
            EMAIL = data.get("EMAIL")
            EMAIL_PASSWORD = data.get("EMAIL_PASSWORD")
            subject = data.get("subject")
            from_address = data.get("from_address")
            to_address = data.get("to_address")
            body = data.get("body")

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.ehlo()
            server.login(EMAIL, EMAIL_PASSWORD)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_address
            msg["To"] = to_address

            msg.attach(MIMEText(body, "html"))
            server.sendmail(from_address, to_address, msg.as_string())
        except:
            raise

    @staticmethod
    async def save_file_to_azure(
        storage_info: dict, file: UploadFile, file_id: Optional[UUID] = None
    ) -> str:
        try:
            AZURE_STORAGE_ACCOUNT_NAME = storage_info.get("AZURE_STORAGE_ACCOUNT_NAME")
            AZURE_STORAGE_ACCOUNT_KEY = storage_info.get("AZURE_STORAGE_ACCOUNT_KEY")
            AZURE_CONTAINER_NAME = storage_info.get("AZURE_CONTAINER_NAME")

            # Configure Azure Storage Blob
            blob_service_client = BlobServiceClient.from_connection_string(
                f"DefaultEndpointsProtocol=https;AccountName={AZURE_STORAGE_ACCOUNT_NAME};AccountKey={AZURE_STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
            )
            container_client = blob_service_client.get_container_client(
                AZURE_CONTAINER_NAME
            )

            unique_blob_name = (
                f"{uuid4() if file_id is None else file_id}-{file.filename}"
            )

            blob_client = container_client.get_blob_client(unique_blob_name)

            content = file.file.read()

            file.file.close()

            blob_client.upload_blob(
                content,
                content_settings=ContentSettings(content_type=file.content_type),
            )

            return f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{unique_blob_name}"
        except Exception as e:
            raise e
