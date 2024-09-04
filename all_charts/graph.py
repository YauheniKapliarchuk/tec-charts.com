"""Test function for plot."""
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import os
from datetime import datetime
from pathlib import Path

from mpl_toolkits.axes_grid1 import make_axes_locatable
import cartopy.crs as ccrs
from datetime import datetime, timedelta

from all_charts.helpers import get_data_for_plot, get_hour_key, convert_date_to_number, upload_file_from_nasa, convert_ionex_to_json, convert_number_to_date_format

from all_charts.clodflare import CloudflareR2Client
from all_charts.helpers import save_file, check_local_file_exists, get_station_prefix, get_nasa_file_option

def getCloudflareClient():
    return CloudflareR2Client()

def get_graph():
    # Create a new figure and plot some data
    plt.figure()
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]
    plt.plot(x, y)

    # Save the figure to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())

    return string.decode('utf-8')


def get_plot(tec_data):
    # Create the plot
    proj = ccrs.PlateCarree()
    f, ax = plt.subplots(1, 1, figsize=(10, 6), subplot_kw=dict(projection=proj))
    ax.coastlines()
    h = plt.imshow(
        tec_data,
        cmap='viridis',
        extent=[-180, 180, -87.5, 87.5],
        transform=proj,
        aspect='auto',
    )
    plt.title('Total Electron Content (TEC) Map')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size='5%', pad=0.1, axes_class=plt.Axes)
    f.add_axes(ax_cb)
    # Add color bar
    cb = plt.colorbar(h, cax=ax_cb)
    cb.set_label('TECU ($10^{16} \\mathrm{el}/\\mathrm{m}^2$)')

    plt.grid()

    return plt


def get_graph_v2(date_hour, date, station):
    file_name =  get_station_prefix(station) + "0OPSRAP_" + str(date) + "0000_01D_" + get_nasa_file_option(station) + "H_GIM.json"
    data = get_data_for_plot(date_hour, file_name)

    # Create a new figure and plot some data
    plt = get_plot(data)

    # Save the figure to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    file_name = f"matplotlib-data-{reformat_date_string(date_hour)}.png"
    file_path = None

    r2cliect = getCloudflareClient()

    if not r2cliect.check_file_exists(date, file_name, station):
        print('Check Image doesn\'t exists: ', True)
        file_path = r2cliect.save_image_to_r2(str(date), file_name, buf.read(), station)
    else:
        file_path = r2cliect.generate_image_link(date, file_name, station)

    return {
        'url': file_path,
        'data': data
    }


def get_graphs_hourly(selected_date: None, station: str = 'CODE'):
    # If selected_date is None or not present, set it to two days before today
    selected_date = get_valid_date(selected_date)

    data = {}
    formatedDate = convert_date_to_number(str(selected_date))

    print('SELECTED DATE: ', str(selected_date))

    station_prefix = get_station_prefix(station)
    nasa_file_option = get_nasa_file_option(station)

    r2cliect = getCloudflareClient()

    file_key = str(formatedDate) + '/' + station + "/" + station_prefix +"0OPSRAP_" + str(formatedDate) + "0000_01D_" + nasa_file_option + "H_GIM.json"
    selected_date_exist = r2cliect.check_file_exists(formatedDate,  station_prefix + "0OPSRAP_" + str(formatedDate) + "0000_01D_" + nasa_file_option + "H_GIM.json", station)

    print('CHECK Selected Date data is exist: ', selected_date_exist)

    local_file_path = os.path.join(
        Path(os.path.abspath(__file__)).parent.parent,
            "data",
            "JSON",
            "COD0OPSRAP_" + str(formatedDate) + "0000_01D_" + nasa_file_option + "H_GIM.json"
        )

    if not selected_date_exist:
        upload_file_from_nasa(formatedDate, station)
        convert_ionex_to_json(formatedDate, station)
    elif not check_local_file_exists(local_file_path):
        json_data = r2cliect.get_json_file(file_key)
        save_file(json_data, local_file_path)

    if station == "CODE":
        for hour in range(25):
            date_hour = format_date(str(selected_date)) + ' ' + get_hour_key(hour)
            data_path = get_graph_v2(date_hour, formatedDate, station)
            print('Saved data: ', data_path['url'])
            data[date_hour] = data_path
    elif station == "JPL":
        for hour in range(0, 23, 2):
            date_hour = format_date(str(selected_date)) + ' ' + get_hour_key(hour)
            data_path = get_graph_v2(date_hour, formatedDate, station)
            print('Saved data: ', data_path['url'])
            data[date_hour] = data_path

    return data

def reformat_date_string(original_string):
    # Extract the date and time part of the string
    date_time_str = original_string.split(' ')[-2:]
    date_time_str = ' '.join(date_time_str)

    # Parse the extracted date and time string
    date_time_obj = datetime.strptime(date_time_str, '%Y/%m/%d %H:%M:%S')

    # Format the date and time as required
    formatted_date_time = date_time_obj.strftime('%Y-%m-%d-%H-%M-%S')

    return formatted_date_time

def format_date(date_str):
    # Split the input string by "-"
    year, month, day = date_str.split('-')
    
    # Format the output string as "YYYY/MM/DD"
    formatted_date = f"{year}/{month}/{day}"
    
    return formatted_date

def get_valid_date(selected_date_str):
    # If the date is not provided or invalid, return the date 2 days earlier than the current date
    if not selected_date_str:
        return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    # Converting the string into a datetime object
    selected_date = datetime.strptime(str(selected_date_str), '%Y-%m-%d').date()
    
    # Checking if the date is 2 days earlier than the current date
    if selected_date >= datetime.now().date() - timedelta(days=2):
        return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    
    return selected_date_str

def get_generated_ionex_json_url(station: str, selected_date: str) -> str:
    """
    Generates the URL for the TEC chart based on the selected satellite and date.
    
    :param selected_date: Date in the format 'YYYY-MM-DD'
    :param selected_satellite: Either 'CODE' or 'JPL'
    :return: Generated URL as a string
    """
     
    formatted_date = convert_date_to_number(str(selected_date))

    if station == "CODE":
        return f"https://tec-charts.org/{formatted_date}/CODE/COD0OPSRAP_{formatted_date}0000_01D_01H_GIM.json"
    elif station == "JPL":
        return f"https://tec-charts.org/{formatted_date}/JPL/JPL0OPSRAP_{formatted_date}0000_01D_02H_GIM.json"
    else:
        return None  # Return None or raise an exception if the satellite is unknown