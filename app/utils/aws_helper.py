


import os
from flask import current_app
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def upload_file_to_s3(file):
    """
    Upload a file-like object to an S3 bucket into a specified folder.
    """
    try:
        current_app.logger.info(f"Uploading file: {file.filename} to s3 bucket")
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region_name = os.getenv('AWS_REGION')

        boto3.setup_default_session(region_name=region_name,
                                    aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key)

        allowed_extensions = ['.pdf', '.txt', '.docx', '.zip']
        filename = file.filename
        extension = os.path.splitext(filename)[1]
        if extension.lower() not in allowed_extensions:
            return False, f"File {filename} has an unsupported extension. Skipping."

        object_name = f"chatbot-files/{filename}"

        s3_client = boto3.client('s3')
        file.seek(0)
        s3_client.upload_fileobj(file, 'chatbot', object_name)
        return True, f"File {filename} uploaded to chatbot/{object_name}"
    except NoCredentialsError:
        return False, "Error uploading file. Credentials not available"
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        return False, f"Error uploading file: {error_msg}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"




def list_files_in_folder():
    """
    List files in a specified folder of an S3 bucket.
    """
    current_app.logger.info("Listing chatbot bucket files in folder 'chatbot-files'")
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region_name = os.getenv('AWS_REGION')

    boto3.setup_default_session(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    s3_client = boto3.client('s3')
    bucket_name = 'chatbot'
    folder_name = 'chatbot-files/'
    file_list = []

    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)

        for page in pages:
            if 'Contents' in page:
                for item in page['Contents']:
                    file_path = item['Key']
                    # Optionally, strip the folder name from the file path
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
    try:
        s3_client = boto3.client('s3')
        object_key = "chatbot-files/" + file_name

        if file_name.lower() == 'all':
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket='chatbot', Prefix=object_key)
            files_content = {}
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        file_content = s3_client.get_object(Bucket='chatbot', Key=obj['Key'])['Body'].read()
                        files_content[obj['Key']] = file_content
            return True, files_content
        else:
            response = s3_client.get_object(Bucket='chatbot', Key=object_key)
            file_content = response['Body'].read()
            return True, file_content
    except NoCredentialsError:
        return False, "Error retrieving file. Credentials not available"
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        return False, f"Error retrieving file: {error_msg}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

    
    
    


