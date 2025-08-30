import json, requests, os, subprocess, urllib.request
from tqdm import tqdm
def clone_github_repo(repo_url):
    try:
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        if os.path.exists(repo_name):
            print(f"Error: A folder named '{repo_name}' already exists in the current directory.")
            return
        print(f"Cloning repository '{repo_url}'...")
        subprocess.run(['git', 'clone', repo_url], check=True)
        print(f"Repository '{repo_name}' cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f'Error: Failed to clone the repository. {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')
def read_json_file(file_path):
    response = urllib.request.urlopen(file_path)
    data = json.loads(response.read())
    return data
def download_7z_file(url, output_filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        with open(output_filename, 'wb') as file, tqdm(desc=
            f'Downloading {output_filename}', total=total_size, unit='B',
            unit_scale=True, unit_divisor=1024) as progress_bar:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
                progress_bar.update(len(chunk))
        print(f'Downloaded {output_filename} to the current directory.')
    else:
        print('Failed to download the file. Seems encountering a connection problem.')
if __name__ == '__main__':
    print('Please select:\n1. download full pack\n2. clone the node only')
    choice = input('Enter your choice (1 to 2): ')
    if choice == '1':
        version = ('https://raw.githubusercontent.com/calcuis/gguf/main/version.json')
        ver = read_json_file(version)
        url = (f"https://github.com/calcuis/gguf/releases/download/{ver[0]['version']}/ComfyUI_GGUF_windows_portable.7z")
        output_filename = 'comfy.7z'
        download_7z_file(url, output_filename)
    elif choice == '2':
        repo_url = 'https://github.com/calcuis/gguf'
        clone_github_repo(repo_url)
    else:
        print('Not a valid number.')