import requests
import zipfile
import os
from tqdm import tqdm
import io

def download_and_extract_file(file_url, txt_filename, destination_folder):
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        zip_buffer = io.BytesIO()
        file_size = int(response.headers.get('Content-Length', 0))
        progress_bar = tqdm(total=file_size, unit="B", unit_scale=True)

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                zip_buffer.write(chunk)
                progress_bar.update(len(chunk))
        progress_bar.close()

        with zipfile.ZipFile(zip_buffer) as zip_file:
            txt_file_name = zip_file.namelist()[0]
            txt_file_data = zip_file.read(txt_file_name)
            txt_file_path = os.path.join(destination_folder, txt_filename)
            with open(txt_file_path, "wb") as txt_file:
                txt_file.write(txt_file_data)
            print(f"Downloaded and extracted '{txt_filename}' to '{destination_folder}' successfully.")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

def download_file(file_url, destination_folder, file_name):
    os.makedirs(destination_folder, exist_ok=True)
    file_path = os.path.join(destination_folder, file_name)
    if os.path.exists(file_path):
        print("The {} file has already been downloaded.".format(file_name))
    else:
        try:
            response = requests.get(file_url, stream=True)
            if response.status_code == 200:
                file_size = int(response.headers.get('Content-Length', 0))
                progress_bar = tqdm(total=file_size, unit="B", unit_scale=True)
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            progress_bar.update(len(chunk))
                progress_bar.close()
                print(f"Downloaded '{file_name}' to '{destination_folder}' successfully.")
            else:
                print(f"Failed to download the file. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while downloading the file: {str(e)}")

# download geojson and capital_csv
geojson_url = "https://datahub.io/core/geo-countries/r/countries.geojson"
capital_url = "https://gist.githubusercontent.com/ofou/df09a6834a8421b4f376c875194915c9/raw/355eb56e164ddc3cd1a9467c524422cb674e71a9/country-capital-lat-long-population.csv"
destination_folder = os.path.join("data", "secondary", "country-capital-lat-long-population")
geojson_file_name = "countries.geojson"
capital_file_name = "country-capital-lat-long-population.csv"
download_file(geojson_url, destination_folder, geojson_file_name)
download_file(capital_url, destination_folder, capital_file_name)

#download primary excel dataset
years = [2010, 2012, 2014, 2016, 2018, 2022]
tournament_ids = [36795, 77681, 140380, 232875, 368908, 653631]
for i in range(6):
    year = years[i]
    t_id = tournament_ids[i]
    excel_url = 'https://chess-results.com/tnr{}.aspx?lan=1&zeilen=99999&art=1&turdet=YES&flag=30&prt=4&excel=2010'.format(t_id)
    destination_folder = os.path.join("data", "primary")
    excel_file_name = "chessResultsList_{}.xlsx".format(year)
    download_file(excel_url, destination_folder, excel_file_name)

# Base URL for the file downloads
base_url = "http://ratings.fide.com/download/"
destination_folder = os.path.join("data", "secondary", "fide_ratings_list")
os.makedirs(destination_folder, exist_ok=True)

ref_file = os.path.join(destination_folder, "standard_jan23frl.txt")

if os.path.exists(ref_file):
    print("The FIDE rating lists have already been downloaded.")
else:
    print("Downloading the FIDE rating lists. It will take a while.")
    for i in range(10, 24):
        if i < 13:
            file_url = f"{base_url}jan{i}frl.zip"
        else:
            file_url = f"{base_url}standard_jan{i}frl.zip"
        txt_filename = f"standard_jan{i}frl.txt"
        download_and_extract_file(file_url, txt_filename, destination_folder)


status = True