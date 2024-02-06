


import os
from flask import current_app
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

session = boto3.Session(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


import base64
import os
from botocore.exceptions import NoCredentialsError, ClientError
from flask import current_app

def upload_file_to_s3(file):
    """
    Encode a file-like object to Base64 and upload it to an S3 bucket into a specified folder.
    If the bucket does not exist, it is created.
    """
    bucket_name = 'itc-agent'

    try:
        current_app.logger.info(f"Uploading file: {file.filename} to S3 bucket")

        allowed_extensions = ['.pdf', '.txt', '.docx', '.zip']
        filename = file.filename
        extension = os.path.splitext(filename)[1]
        if extension.lower() not in allowed_extensions:
            return False, f"File {filename} has an unsupported extension. Skipping."

        object_name = f"chatbot-files/{filename}"

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
        # file_content = file.read()
        # encoded_content = base64.b64encode(file_content)

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
    bucket_name = 'itc-agent'


    try:
        s3_client = session.client('s3')
        folder_name = 'chatbot-files/'
        file_list = []
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)

        for page in pages:
            if 'Contents' in page:
                for item in page['Contents']:
                    file_path = item['Key']
                    file_name = file_path.replace(folder_name, '')
                    file_list.append(file_name)
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
    Retrieve a file from a specified folder in an S3 bucket.
    """
    current_app.logger.info("About to download file from s3 for indexing")
    bucket_name = "itc-agent"
    
    try:
        s3_client = session.client('s3')
        object_key = "chatbot-files/" + file_name

        if file_name.lower() == 'all':
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=object_key)
            files_content = {}
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        file_content = s3_client.get_object(Bucket=bucket_name, Key=obj['Key'])['Body'].read()
                        files_content[obj['Key']] = file_content
            return True, files_content
        else:
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

    
    
    


