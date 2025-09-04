__version__ = '1.0.1'

import os
import zipfile
import urllib.request
import sys
import subprocess
import tempfile
import shutil
import re

def get_layer_from_api_tl(api_tl_path):
    #Get LAYER version from api.tl file
    try:
        with open(api_tl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        layer_match = re.search(r'// LAYER (\d+)', content)
        if layer_match:
            return int(layer_match.group(1))
        return None
    except Exception as e:
        print(f"[telethon_up]:Error reading api.tl: {e}")
        return None

def download_api_tl(temp_dir):
    #Download api.tl file once to temporary directory
    api_tl_url = "https://github.com/telegramdesktop/tdesktop/raw/dev/Telegram/SourceFiles/mtproto/scheme/api.tl"
    api_tl_path = os.path.join(temp_dir, "api.tl")
    
    try:
        urllib.request.urlretrieve(api_tl_url, api_tl_path)
        return api_tl_path
    except Exception as e:
        print(f"[telethon_up]:Error downloading api.tl: {e}")
        return None

def download_and_update_telethon(api_tl_path, latest_layer):
    #Download and update Telethon source with pre-downloaded api.tl
    
    telethon_zip_url = "https://github.com/amirwolf5122/Telethon/archive/1v.zip"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        zip_path = tmp_file.name
    
    try:
        # Download Telethon source
        urllib.request.urlretrieve(telethon_zip_url, zip_path)
        
        # Extract to temporary directory
        extract_dir = "Telethon_temp"
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find Telethon folder
        extracted_folders = os.listdir(extract_dir)
        telethon_folder = None
        for folder in extracted_folders:
            if folder.startswith('Telethon'):
                telethon_folder = os.path.join(extract_dir, folder)
                break
        
        if not telethon_folder:
            print("[telethon_up]:Telethon folder not found in extracted files")
            return False
        
        # Copy pre-downloaded api.tl to Telethon
        target_api_tl_path = os.path.join(telethon_folder, "telethon_generator", "data", "api.tl")
        os.makedirs(os.path.dirname(target_api_tl_path), exist_ok=True)
        shutil.copy(api_tl_path, target_api_tl_path)
        
        # Install Telethon
        setup_py = os.path.join(telethon_folder, "setup.py")
        if os.path.exists(setup_py):
            print("[telethon_up]:Installing updated Telethon...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", ".", "--force-reinstall"],
                capture_output=True,
                text=True,
                cwd=telethon_folder
            )
            
            if result.returncode == 0:
                print(f"Telethon updated successfully to layer {latest_layer}!")
                return True
            else:
                print(f"[telethon_up]:Installation failed: {result.stderr}")
                return False
        else:
            print("[telethon_up]:setup.py not found in Telethon directory")
            return False
            
    except Exception as e:
        print(f"[telethon_up]:Error during Telethon update: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary files
        try:
            os.unlink(zip_path)
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir, ignore_errors=True)
        except:
            pass

def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download api.tl once
        api_tl_path = download_api_tl(temp_dir)
        if not api_tl_path:
            return
        
        # Check layer version
        latest_layer = get_layer_from_api_tl(api_tl_path)
        if not latest_layer:
            print("[telethon_up]:Could not determine latest layer")
            return
            
        try:
            from telethon.tl.alltlobjects import LAYER
            current_layer = LAYER
            if current_layer < latest_layer:
                print(f"[telethon_up]:Updating Telethon from layer {current_layer} to {latest_layer}...")
                success = download_and_update_telethon(api_tl_path, latest_layer)
                if not success:
                    print("[telethon_up]:Failed to update Telethon")
                    return
            else:
                print("[telethon_up]:Telethon is up to date!")
                return
                
        except ImportError:
            print("[telethon_up]:Telethon not found, installing latest version...")
            success = download_and_update_telethon(api_tl_path, latest_layer)
            if not success:
                raise ImportError("[telethon_up]:Failed to install Telethon")
        
        # Final verification
        try:
            from telethon.tl.alltlobjects import LAYER
            print(f"[telethon_up]:Final Telethon LAYER version: {LAYER}")
        except ImportError:
            raise ImportError("[telethon_up]:Failed to import Telethon even after installation")

if __name__ == "__main__":
    main()
