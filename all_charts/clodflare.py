import boto3
from botocore.exceptions import ClientError
import os

def check_folder_exists(bucket_name, folder_name):
    # https://${bucketName}.${accountId}.r2.cloudflarestorage.com
    print('Cloudflare checking bucket...')
    s3 = boto3.client(
        's3', 
        endpoint_url='',
        aws_access_key_id='',
        aws_secret_access_key=''
    )
    
    try:
        result = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        print('Cloudflare contents in Bucket: ', 'Contents' in result)
        # Если результат содержит объекты, значит папка существует
        if 'Contents' in result:
            return True
        return False
    except ClientError as e:
        print(f"Error checking folder: {e}")
        return False
    
def save_json_file(folder_name, file_name, json_file_path, station: str = 'CODE', bucket_name: str = 'tec-charts'):
    s3 = boto3.client(
        's3', 
        endpoint_url='',
        aws_access_key_id='',
        aws_secret_access_key=''
    )
    
     # Путь к файлу на R2
    print('Saving file... ')
    print('File name: ', file_name)
    print('Folder name: ', folder_name)

    file_key = f"{folder_name}/{station}/{file_name}"

    try:
        # Чтение JSON файла
        print('Reading file...')
        with open(json_file_path, 'rb') as file_data:
            # Сохранение файла на R2
            s3.put_object(Bucket=bucket_name, Key=file_key, Body=file_data)
            print(f"JSON file saved to {file_key} on Cloudflare R2")
    except ClientError as e:
        print(f"Error saving JSON file: {e}")

def check_file_exists(folder_name, file_name, station: str = 'CODE', bucket_name: str = 'tec-charts'):
    # Настройка клиента S3 для Cloudflare R2
    s3 = boto3.client(
        's3', 
        endpoint_url='',
        aws_access_key_id='',
        aws_secret_access_key=''
    )
    
    # Путь к файлу на R2
    file_key = f"{folder_name}/{station}/{file_name}"

    try:
        # Попытка получить метаданные файла
        s3.head_object(Bucket=bucket_name, Key=file_key)
        print(f"File {file_key} exists on Cloudflare R2")
        return True
    except ClientError as e:
        # Если объект не существует, выбрасывается ошибка
        if e.response['Error']['Code'] == '404':
            print(f"File {file_key} does not exist on Cloudflare R2")
            return False
        else:
            print(f"Error checking file: {e}")
            raise

def get_json_file(bucket_name, file_key):
    s3 = boto3.client(
        's3', 
        endpoint_url='',
        aws_access_key_id='',
        aws_secret_access_key=''
    )
    
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        json_content = response['Body'].read().decode('utf-8')
        return json_content
    except ClientError as e:
        print(f"Error getting JSON file: {e}")
        return None
    
def save_images_to_r2(folder_name, image_files, station: str = 'CODE', bucket_name: str = 'tec-charts'):
    s3 = boto3.client(
        's3', 
        endpoint_url='',
        aws_access_key_id='',
        aws_secret_access_key=''
    )
    
    image_urls = []

    for image_file in image_files:
        file_key = f"{folder_name}/{station}/{os.path.basename(image_file)}"
        print('Uploading IMAGE: ', image_file)
        print('on R2...')
        
        try:
            with open(image_file, 'rb') as file_data:
                s3.put_object(Bucket=bucket_name, Key=file_key, Body=file_data)
                image_url = f"https://pub-317be47945864f39a0927a7bf12f53fb.r2.dev/{bucket_name}/{file_key}"
                image_urls.append(image_url)
                print(f"Image {file_key} saved to Cloudflare R2")
        except ClientError as e:
            print(f"Error saving image {file_key}: {e}")
    
    return image_urls

def has_png_files_in_r2(folder_path, station: str = 'CODE', bucket_name: str = 'tec-charts'):
    # Настройка клиента S3 для Cloudflare R2
    s3 = boto3.client(
        's3', 
        endpoint_url='',
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    # Полный путь до папки на R2
    folder_key = f"tec-charts/{folder_path}/"

    try:
        # Получение списка объектов в указанной папке
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)
        
        # Проверка на наличие .png файлов
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.png'):
                    return True
        
        return False

    except ClientError as e:
        print(f"Error checking PNG files in R2: {e}")
        return False

    except ClientError as e:
        print(f"Error checking PNG files in R2: {e}")
        return False
    
def save_image_to_r2(folder_path, file_name, image_data, station: str = 'CODE', bucket_name: str = 'tec-charts'):
    s3 = boto3.client(
        's3', 
        endpoint_url='',
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    file_key = f"{folder_path}/{station}/{file_name}"

    try:
        s3.put_object(Bucket=bucket_name, Key=file_key, Body=image_data)
        print(f"Image saved to R2 at {file_key}")

        # Формируем публичный URL для доступа к изображению
        image_url = f"https://pub-317be47945864f39a0927a7bf12f53fb.r2.dev/{bucket_name}/{file_key}"
        return image_url
    except ClientError as e:
        print(f"Error saving image to R2: {e}")
        return None
    
def generate_image_link(date, file_name, station: str = 'CODE', bucket_name: str = 'tec-charts'):
    return f"https://pub-317be47945864f39a0927a7bf12f53fb.r2.dev/{bucket_name}/{date}/{station}/{file_name}"