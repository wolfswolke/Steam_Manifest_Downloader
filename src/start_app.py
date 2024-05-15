import os
import re
from pathlib import Path
# GLOBALS
manifest_file = "./manifests.txt"
config_file = "./config.txt"
all_manifests = []

with open(config_file, "r") as file:
    for line in file:
        key, value = line.strip().split("=")
        key = key.strip()
        value = value.strip()

        if key == "depot_downloader_binary":
            depot_downloader_binary = Path(value)
        elif key == "username":
            username = value
        elif key == "app_id":
            app_id = int(value)
        elif key == "depot":
            depot = int(value)
        elif key == "depot_output":
            depot_output = Path(value)

try:
    depot_downloader_binary
    username
    app_id
    depot
    depot_output
except NameError:
    print("Error: Missing config values")
    exit(1)

# LOGIC
manifest_data = open(manifest_file, "r")
for line in manifest_data:
    matches = re.findall(r'\b\d{19}\b', line)
    if matches:
        number_as_string = matches[0]
        number_as_int = int(number_as_string)
        all_manifests.append(number_as_int)

for manifest in all_manifests:
    command = (f"{depot_downloader_binary} -app "
               f"{app_id} -depot {depot} -manifest "
               f"{manifest} -username {username} -remember-password -dir {depot_output}\\{app_id}\\{depot}\\{manifest}")
    try:
        os.system(command)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)