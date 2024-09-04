"""Helper functions for the project."""

import json
import os

from pathlib import Path

from ftplib import FTP_TLS
import gzip
import shutil
from datetime import datetime

from all_charts.clodflare import CloudflareR2Client

DATA_DIR = Path(os.path.abspath(__file__)).parent.parent / "data" / "JSON"

def get_cloudflare_client():
    return CloudflareR2Client()


def save_file(file_data: dict, file_name: str = "default.json"):
    file_path = DATA_DIR / file_name
    with open(file_path, "w") as f:
        f.write(json.dumps(file_data))
    return file_path


def get_hour_key(hour: int) -> str:
    """Return the hour key in the format HH:00:00."""
    if hour == 24:
        return "00:00:00"
    return f"{hour:02d}:00:00"

def get_data_for_plot(date_hour: str, file_name: str) -> dict:
    """Get data for a given date and hour."""
    file_path = DATA_DIR / file_name
    with open(file_path, "r") as f:
        file_data = json.loads(f.read())
    return file_data[date_hour]

def upload_file_from_nasa(date: int, station: str = 'CODE'):
    if not date:
        return
    
    prefix = get_station_prefix(station)
    email = 'ek.genia13@gmail.com'
    formatted_date = convert_number_to_date_format(date)
    directory = f'/gnss/products/ionex/{formatted_date.split("/")[0]}/{formatted_date.split("/")[1]}'
    filename = f'{prefix}0OPSRAP_{date}0000_01D_{get_nasa_file_option(station)}H_GIM.INX.gz'

    with FTP_TLS(host='gdc.cddis.eosdis.nasa.gov') as ftps:
        ftps.login(user='anonymous', passwd=email)
        ftps.prot_p()
        ftps.cwd(directory)
        with open(filename, 'wb') as file:
            ftps.retrbinary("RETR " + filename, file.write)
    
    unzip_file(filename)
    os.remove(filename)

def get_data_for_day_plots(file_name: str) -> dict:
    """Get data for the entire day. date_hour format = "%Y/%m/%d %H:%M:%S"""
    file_path = DATA_DIR / file_name
    with open(file_path, "r") as f:
        file_data = json.loads(f.read())
    return file_data

def unzip_file(gz_path: str, extract_to: str = None) -> str:
    """Decompress a .gz file."""
    extract_to = extract_to or os.path.dirname(gz_path)
    decompressed_file_path = os.path.join(extract_to, os.path.basename(gz_path)[:-3])

    with gzip.open(gz_path, 'rb') as f_in, open(decompressed_file_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    print(f'File "{gz_path}" decompressed successfully to "{decompressed_file_path}".')
    return decompressed_file_path

def convert_date_to_number(date_str: str) -> int:
    """Convert a date string to a number in the format YYYYDDD."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        year = date_obj.year
        day_of_year = date_obj.timetuple().tm_yday
        return int(f"{year}{day_of_year:03d}")
    except ValueError:
        return None

def convert_number_to_date_format(date_number: int) -> str:
    """Convert a number in the format YYYYDDD to a date string."""
    year = str(date_number)[:4]
    day_of_year = str(date_number)[4:]
    return f"{year}/{day_of_year}"  

def is_ready_for_read (line):
    return 'EPOCH OF CURRENT MAP' not in line and 'START OF TEC MAP' not in line and 'END OF TEC MAP' not in line

# Read the file and parse blocks
def convert_ionex_to_json(selected_date, station: str = 'CODE'):
    parse_day = False
    prefix = get_station_prefix(station)

    day_data = {}
    hour_data = []
    current_altitude_data = []
    year, month, day, hour, minute, second = 0, 0, 0, 0, 0, 0

    file_name = os.path.join(
        Path(os.path.abspath(__file__)).parent.parent,
        prefix + "0OPSRAP_" + str(selected_date) + "0000_01D_" + get_nasa_file_option(station) + "H_GIM.INX",
    )

    print('Path: ', file_name)

    with open(file_name, 'r') as file:
    # with open('/Users/admin/Downloads/COD0OPSFIN_20232130000_01D_01H_GIM.INX', 'r') as file:
        for line in file:
            if line.strip():  # Non-empty line
                if 'START OF TEC MAP' in line:
                    parse_day = True

                if 'EPOCH OF CURRENT MAP' in line:
                    date_info = line.strip().split()
                    year, month, day, hour, minute, second = map(int, date_info[:6])

                if 'END OF TEC MAP' in line:
                    day_data[f"{year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}"] = hour_data
                    hour_data = []
                    current_altitude_data = []
                    parse_day = False
                    # break

                if is_ready_for_read(line):
                    if parse_day:
                        if 'LAT/LON1/LON2/DLON/H' in line:
                            if len(current_altitude_data) > 0:
                                current_altitude_data.pop()
                                hour_data.append(current_altitude_data)
                                current_altitude_data = []
                        else: 
                            numbers_list = line.split()
                            numbers_array = [int(number) for number in numbers_list]
                            current_altitude_data = current_altitude_data + numbers_array

    json_file_name = f"{prefix}0OPSRAP_{selected_date}0000_01D_{get_nasa_file_option(station)}H_GIM.json"
    file_path = save_file(day_data, json_file_name)

    save_file(day_data, file_path)

    r2_client = get_cloudflare_client()
    r2_client.save_json_file(str(selected_date), json_file_name, file_path, station)
    os.remove(file_name)
    
def check_local_file_exists(file_path: str) -> bool:
    """Check if a local file exists."""
    exists = os.path.exists(file_path)
    print(f"File {file_path} {'exists' if exists else 'does not exist'} locally.")
    return exists
    
def get_station_prefix(station: str) -> str:
    """Get station prefix."""
    return {
        "CODE": "COD",
        "JPL": "JPL"
    }.get(station, "UNKNOWN")

def get_nasa_file_option(station: str) -> str:
    """Get NASA file option based on the station."""
    return {
        "CODE": "01",
        "JPL": "02"
    }.get(station, "00")
