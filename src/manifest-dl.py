import os
import re
from pathlib import Path

import datetime
import calendar 

# Globals
config_file = "manifest-dl-config.txt"
all_manifests = []
all_manifests_datetime = []
datetime_as_prefix = ""
filelist = ""

with open(config_file, "r") as file:
    for line in file:
        if line.startswith("#"):
            continue

        key, value = line.strip().split("=")
        key = key.strip()
        value = value.strip()

        if key == "path_to_bin":
            path_to_bin = Path(value)
        elif key == "username":
            username = value
        elif key == "app":
            app = int(value)
        elif key == "depot":
            depot = int(value)
        elif key == "output":
            output = Path(value)
        elif key == "manifests":
            manifests = Path(value)
        elif key == "datetime_as_prefix":
            datetime_as_prefix = value
        elif key == "filelist":
            filelist = Path(value)
try:
    path_to_bin
    username
    app
    depot
    output
    manifests
except NameError:
    print("Error: missing config values")
    exit(1)

def month_to_value(month_s):
    for month_id in range(1, 13):
        if calendar.month_name[month_id] == month_s: return month_id
    raise Exception(f"{month_s} is not valid!")

def datetime_to_epoch(dt):
    datetime_s, _ = dt.split("UTC")
    datetime_s = datetime_s.strip()
    day_s, month_s, year_s, _, time_s = datetime_s.split(" ")
    month = month_to_value(month_s)
    time = datetime.time.fromisoformat(time_s)
    return str(int(datetime.datetime(int(year_s), month, int(day_s), time.hour, time.minute, time.second, tzinfo=datetime.timezone.utc).timestamp()))

def get_manifest(line):
    _, _, manifest = line.partition("ago")
    manifest = manifest.split()[0] # There is an chance that a branch may be specified at the end of the line, so we split the line and select only the first option.
    return int(manifest)

manifest_data = open(manifests, "r")
for line in manifest_data:
    matches = get_manifest(line) # Manifest ID is not 19 digits only!
    if matches:
        all_manifests.append(matches)
        all_manifests_datetime.append(datetime_to_epoch(line))

for idx, manifest in enumerate(all_manifests):
    manifest_folder = manifest
    if datetime_as_prefix == "on":
        manifest_folder = all_manifests_datetime[idx] + "_" + str(manifest_folder)
    command = (f"{path_to_bin} -app "
               f"{app} -depot {depot} -manifest "
               f"{manifest} -username {username} -remember-password -dir {output}\\{app}\\{depot}\\{manifest_folder}")
    if filelist:
        command += f" -filelist {filelist}"
    try:
        os.system(command)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)