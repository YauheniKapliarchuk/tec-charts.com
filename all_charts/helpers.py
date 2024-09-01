"""Helper functions for the project."""

import json
import os

from pathlib import Path
import requests

from ftplib import FTP_TLS
import gzip
import shutil
from datetime import datetime

from all_charts.clodflare import save_json_file

def save_file(file_data: dict, file_name: str = "COD0OPSFIN_20232130000_01D_01H_GIM.json"):
    file_path = os.path.join(
        Path(os.path.abspath(__file__)).parent.parent,
        "data",
        "JSON",
        file_name,
    )
    with open(file_path, "w") as f:
        f.write(json.dumps(file_data))


def get_hour_key(hour):
    if hour == 24:
        data_key = "00:00:00"
    else:
        if hour < 10:
            hour = f"0{hour}"
        else:
            hour = f"{hour}"

        data_key = f"{hour}:00:00"

    return data_key


def get_data_for_plot(date_hour: str, file_name: str):
    """Get data for a given date and hour.

    date_hour format = "%Y/%m/%d %H:%M:%S"
    """
    file_path = os.path.join(
        Path(os.path.abspath(__file__)).parent.parent,
        "data",
        "JSON",
        file_name,
    )
    with open(file_path, "r") as f:
        file_data = json.loads(f.read())

    print('Get Data test filename: ' + file_name)
    print('Get Data test: ' + date_hour)
    return file_data[date_hour]

# def upload_file_from_nasa():
#     # Reads the URL from the command line argument
#     url = 'https://cddis.nasa.gov/archive/gnss/products/ionex/2024/163/COD0OPSRAP_20241630000_01D_01H_GIM.INX.gz'
#
#     # Assigns the local file name to the last part of the URL
#     filename = url.split('/')[-1]
#
#     # Makes request of URL, stores response in variable r
#     r = requests.get(url, auth=('yauheni_kapliarchuk', 'Support-1!11'))
# #     print('Status Code ', r.status_code)
# #     print('TEXT: ', r.text)
# #     print('TEXT: ', r.json)
#
#     # Opens a local file of same name as remote file for writing to
#     with open(filename, 'wb') as fd:
#         for chunk in r.iter_content(chunk_size=1000):
#             fd.write(chunk)
#
#     # Closes local file
#     fd.close()

def upload_file_from_nasa(date, station: str = 'CODE'):
    if not date:
        return
    
    prefix = get_station_prefix(station)

    email = 'ek.genia13@gmail.com'
    formatted_date = convert_number_to_date_format(date)
    directory = f'/gnss/products/ionex/{formatted_date.split("/")[0]}/{formatted_date.split("/")[1]}'
    filename = f'{prefix}0OPSRAP_{date}0000_01D_{get_nasa_file_option(station)}H_GIM.INX.gz'

    ftps = FTP_TLS(host='gdc.cddis.eosdis.nasa.gov')
    ftps.login(user='anonymous', passwd=email)
    ftps.prot_p()
    ftps.cwd(directory)
    ftps.retrbinary("RETR " + filename, open(filename, 'wb').write)

    unzip_file(filename)


def get_data_for_day_plots(file_name: str = "COD0OPSFIN_20232130000_01D_01H_GIM.json"):
    """Get data for a given date and hour.

    date_hour format = "%Y/%m/%d %H:%M:%S"
    """
    file_path = os.path.join(
        Path(os.path.abspath(__file__)).parent.parent,
        "data",
        "JSON",
        file_name,
    )
    with open(file_path, "r") as f:
        file_data = json.loads(f.read())

    return file_data

def unzip_file(gz_path, extract_to=None):
    """
    Decompress a .gz file.

    :param gz_path: Path to the .gz file
    :param extract_to: Directory to extract the contents to (default: same directory as the .gz file)
    :return: Path to the decompressed file
    """
    if extract_to is None:
        extract_to = os.path.dirname(gz_path)

    file_name = os.path.basename(gz_path)
    decompressed_file_path = os.path.join(extract_to, file_name[:-3])  # Remove the .gz extension

    with gzip.open(gz_path, 'rb') as f_in:
        with open(decompressed_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f'File "{gz_path}" decompressed successfully to "{decompressed_file_path}".')
    return decompressed_file_path

def convert_date_to_number(date_str):
    if date_str is None:
        return None
    
    try:
        # Parse the input date string
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Extract the year and the day of the year
        year = date_obj.year
        day_of_year = date_obj.timetuple().tm_yday
        
        # Combine the year and the day of the year into the desired format
        result = int(f"{year}{day_of_year:03d}")
        
        return result
    except ValueError:
        # Handle the case where the date_str is not in the correct format
        return None
    
def convert_number_to_date_format(date_number):
    print('test date number: ', date_number)
    year = str(date_number)[:4]
    day_of_year = str(date_number)[4:]
    return f"{year}/{day_of_year}"

def is_ready_for_read (line):
    return 'EPOCH OF CURRENT MAP' not in line and 'START OF TEC MAP' not in line and 'END OF TEC MAP' not in line

# # Read the file and parse blocks
def convert_ionex_to_json(selected_date, station: str = 'CODE'):
    count = 0
    start_hour = 0
    parse_day = False
    prefix = get_station_prefix(station)

    day_data = {}
    hour_data = []
    current_altitude_data = []
    year, month, day, hour, minute, second = 0, 0, 0, 0, 0, 0

    # file_name = os.path.dirname("COD0OPSFIN_" + str(selected_date) + "0000_01D_01H_GIM.INX")

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

    file_path = os.path.join(
        Path(os.path.abspath(__file__)).parent.parent,
        "data",
        "JSON",
        prefix + "0OPSRAP_" + str(selected_date) + "0000_01D_" + get_nasa_file_option(station) + "H_GIM.json",
    )

    save_file(day_data, file_path)

    save_json_file(str(selected_date), prefix + "0OPSRAP_" + str(selected_date) + "0000_01D_" + get_nasa_file_option(station) + "H_GIM.json", file_path, station)

def check_local_file_exists(file_path):
    # Проверка существования файла
    if os.path.exists(file_path):
        print(f"File {file_path} exists locally")
        return True
    else:
        print(f"File {file_path} does not exist locally")
        return False
    
def get_station_prefix(station):
    if station == "CODE":
        return "COD"
    elif station == "JPL":
        return "JPL"
    
def get_nasa_file_option(station):
    if station == "CODE":
        return "01"
    elif station == "JPL":
        return "02"
