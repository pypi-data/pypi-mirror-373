import json, requests, urllib.request
from tqdm import tqdm

def read_json_file(file_path):
    response = urllib.request.urlopen(file_path)
    data = json.loads(response.read())
    return data
def download_file(url, output_filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        with open(output_filename, 'wb') as file, tqdm(
            desc=f"Downloading {output_filename}",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
                progress_bar.update(len(chunk))
        print(f"Downloaded {output_filename} to the current directory.")
    else:
        print("Failed to download the file. Seems encountering a connection problem.")

version = "https://raw.githubusercontent.com/calcuis/gguf-quantizor/main/version.json"
jdata = read_json_file(version)
url = f"https://github.com/calcuis/gguf-quantizor/releases/download/{jdata[0]['version']}/quantizor.exe"
output_filename = "quantizor.exe"
download_file(url, output_filename)