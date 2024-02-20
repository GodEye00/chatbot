


import os
from flask import current_app
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ..helpers.indexing import delete_index

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

session = boto3.Session(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
bucket_name = "itc-agent"
object_name = "chatbot-files/"

def upload_file_to_s3(file, object_name=object_name):
    """
    Encode a file-like object to Base64 and upload it to an S3 bucket into a specified or provided folder.
    If the bucket does not exist, it is created.
    """

    try:
        current_app.logger.info(f"Uploading file: {file.filename} to S3 bucket")

        allowed_extensions = ['.pdf', '.txt', '.docx', '.zip']
        filename = file.filename
        extension = os.path.splitext(filename)[1]
        if extension.lower() not in allowed_extensions:
            return False, f"File {filename} has an unsupported extension. Skipping."


        s3_client = session.client('s3')

        # Check if the bucket exists and create it if not
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            current_app.logger.info(f"Bucket '{bucket_name}' already exists.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404' or error_code == 'NoSuchBucket':
                current_app.logger.info(f"Bucket '{bucket_name}' does not exist. Creating bucket...")
                if region_name == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    location = {'LocationConstraint': region_name}
                    s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
                current_app.logger.info(f"Bucket '{bucket_name}' created.")
            else:
                current_app.logger.exception(f"S3 Connectivity check failed: {e}")
                return False, f"S3 Connectivity check failed. Error: {e}"

        file.seek(0)

        current_app.logger.info('About to finally upload file to S3')
        response = s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=file)
        current_app.logger.info(f"Upload file to S3 successfully. Response: {response}")
        return True, f"File {filename} encoded and uploaded to {bucket_name}/{object_name} in Base64 format"
    except NoCredentialsError as e:
        current_app.logger.exception("Error uploading file. Credentials not available: {e}")
        return False, "Error uploading file. Credentials not available"
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        current_app.logger.exception(f"Error uploading file: {e}")
        return False, f"Error uploading file: {error_msg}"
    except Exception as e:
        current_app.logger.exception(f"Unexpected error: {str(e)}")
        return False, f"Unexpected error: {str(e)}"




def list_files_in_folder():
    """
    List files in a specified folder of an S3 bucket.
    """
    current_app.logger.info("Listing files in folder 'chatbot-files'")


    try:
        s3_client = session.client('s3')
        file_list = []
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)

        for page in pages:
            if 'Contents' in page:
                for item in page['Contents']:
                    file_path = item['Key']
                    file_list.append(file_path)
        return True, file_list
    except NoCredentialsError:
        current_app.logger.exception("Credentials not available")
        return False, "Credentials not available"
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        current_app.logger.exception(f"ClientError: {error_msg}")
        return False, error_msg
    except Exception as e:
        current_app.logger.exception(f"Unexpected error: {str(e)}")
        return False, f"Unexpected error: {str(e)}"



def get_file_from_s3(file_name):
    """
    Retrieve files from an S3 bucket based on the specified parameters.
    :param file_name: The name of the file, 'all' to retrieve all files in the bucket, or specific file name.
    :param is_folder: The folder name within the S3 bucket to retrieve files from.
    """
    is_folder=False

    try:
        s3_client = session.client('s3')

        if not file_name.startswith(object_name):
            is_folder = True

        if file_name.lower() == 'all':
            # Retrieve all files in the bucket.
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket_name)
            files_content = {}
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        file_content = s3_client.get_object(Bucket=bucket_name, Key=obj['Key'])['Body'].read()
                        files_content[obj['Key']] = file_content
            return True, files_content
        else:
            if is_folder:
                # Retrieving all files in the specified folder.
                object_key = (file_name if file_name.endswith('/') else file_name + '/')
                paginator = s3_client.get_paginator('list_objects_v2')
                page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=object_key)
                files_content = {}
                for page in page_iterator:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            file_content = s3_client.get_object(Bucket=bucket_name, Key=obj['Key'])['Body'].read()
                            files_content[obj['Key']] = file_content
                return True, files_content if files_content else (False, "No files found in the specified folder")
            else:
                object_key = file_name
                response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                file_content = response['Body'].read()
                return True, file_content
    except NoCredentialsError:
        return False, "Error retrieving file. Credentials not available"
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        return False, f"Error retrieving file: {error_msg}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"





def delete_from_s3(file_name):
    """
    Deletes a file or all files within a folder from an S3 bucket.

    :param file_name: The key of the file or the prefix of the folder to delete.
    """
    is_folder = False

    try:

        if not file_name.startswith(file_name):
            is_folder = True

        s3_client = session.client('s3')
        if is_folder:
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=file_name)

            objects_to_delete = []
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objects_to_delete.append({'Key': obj['Key']})

            if objects_to_delete:
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={
                        'Objects': objects_to_delete,
                        'Quiet': True
                    }
                )
            return True, "Folder and its contents deleted successfully."
        else:
            success, message = delete_index(file_name)
            if success:
                s3_client.delete_object(Bucket=bucket_name, Key=file_name)
                return True, "File deleted successfully."
            else:
                return False, message
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        current_app.logger.error(f'A client error occurred while deleting object; {error_msg}')
        return False, f"Error deleting object: {error_msg}"
    except Exception as e:
        current_app.logger.exception(f"Exception while trying to delete file from s3. Error: {e}")
        return False, f"Unexpected error: {str(e)}"




