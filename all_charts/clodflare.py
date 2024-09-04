import boto3
from botocore.exceptions import ClientError
import os
from django.conf import settings

class CloudflareR2Client:
    def __init__(self, bucket_name=None, endpoint_url=None, access_key=None, secret_key=None):
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url or settings.R2_ENDPOINT_URL,
            aws_access_key_id=access_key or settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=secret_key or settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = bucket_name or settings.R2_BUCKET_NAME

    def check_folder_exists(self, folder_name):
        print('Cloudflare checking bucket...')
        try:
            result = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_name)
            print('Cloudflare contents in Bucket: ', 'Contents' in result)
            return 'Contents' in result
        except ClientError as e:
            print(f"Error checking folder: {e}")
            return False

    def save_json_file(self, folder_name, file_name, json_file_path, station='CODE'):
        file_key = f"{folder_name}/{station}/{file_name}"
        try:
            print(f'Saving file {file_name} to {file_key}...')
            with open(json_file_path, 'rb') as file_data:
                self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=file_data)
                print(f"JSON file saved to {file_key} on Cloudflare R2")
        except ClientError as e:
            print(f"Error saving JSON file: {e}")

    def check_file_exists(self, folder_name, file_name, station='CODE'):
        file_key = f"{folder_name}/{station}/{file_name}"
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=file_key)
            print(f"File {file_key} exists on Cloudflare R2")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"File {file_key} does not exist on Cloudflare R2")
                return False
            else:
                print(f"Error checking file: {e}")
                raise

    def get_json_file(self, file_key):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            print(f"Error getting JSON file: {e}")
            return None

    def save_images_to_r2(self, folder_name, image_files, station='CODE'):
        image_urls = []
        for image_file in image_files:
            file_key = f"{folder_name}/{station}/{os.path.basename(image_file)}"
            try:
                print(f'Uploading image {image_file} to {file_key}...')
                with open(image_file, 'rb') as file_data:
                    self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=file_data)
                    image_url = self.generate_image_link(folder_name, os.path.basename(image_file), station)
                    image_urls.append(image_url)
                    print(f"Image {file_key} saved to Cloudflare R2")
            except ClientError as e:
                print(f"Error saving image {file_key}: {e}")
        return image_urls

    def has_png_files_in_r2(self, folder_path, station='CODE'):
        folder_key = f"{folder_path}/{station}/"
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_key)
            if 'Contents' in response:
                return any(obj['Key'].endswith('.png') for obj in response['Contents'])
            return False
        except ClientError as e:
            print(f"Error checking PNG files in R2: {e}")
            return False

    def save_image_to_r2(self, folder_path, file_name, image_data, station='CODE'):
        file_key = f"{folder_path}/{station}/{file_name}"
        try:
            print(f'Saving image {file_name} to {file_key}...')
            self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=image_data)
            return self.generate_image_link(folder_path, file_name, station)
        except ClientError as e:
            print(f"Error saving image to R2: {e}")
            return None

    def generate_image_link(self, date, file_name, station='CODE'):
        return f"https://tec-charts.org/{date}/{station}/{file_name}"

# How to use in Django
# r2_client = CloudflareR2Client()
# r2_client.save_json_file('2024-08-25', 'data.json', 'path/to/data.json')
