import os
from datetime import datetime
import sys
from pathlib import Path

if not sys.platform.startswith('win'):
    print("This script is intended to run on Windows only. Sorry!")
    sys.exit(1)

try:
    import win32file
    import win32con
    import pywintypes
except ImportError:
    print("This script requires the pywin32 package. Please install it using 'pip install pywin32'.")
    sys.exit(1)

def parse_line(line):
    try:
        parts = line.strip().split('\t')
        if len(parts) < 3:
            return None, None
        timestamp_str = parts[0].strip()
        manifest_id = parts[-1].strip()
        if not manifest_id.isdigit():
            return None, None
        return timestamp_str, manifest_id
    except Exception as e:
        print(f"Error parsing line: {str(e)}")
        return None, None

def parse_timestamp(timestamp_str):
    try:
        clean_str = timestamp_str.replace('UTC', '').replace('–', '').strip()
        return datetime.strptime(clean_str, '%d %B %Y %H:%M:%S')
    except ValueError as e:
        print(f"Failed to parse timestamp '{timestamp_str}': {str(e)}")
        raise

def update_folder_dates(root_path, input_file_path):
    root_path = Path(root_path)
    input_file_path = Path(input_file_path)

    if not root_path.exists():
        print(f"Root path does not exist: {root_path}")
        return False
    if not root_path.is_dir():
        print(f"Root path is not a directory: {root_path}")
        return False
    if not input_file_path.exists():
        print(f"Input file does not exist: {input_file_path}")
        return False

    success_count = 0
    error_count = 0
    processed_folders = set()

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"Starting processing of {len(lines)} entries from {input_file_path}")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                timestamp_str, manifest_id = parse_line(line)
                if not timestamp_str or not manifest_id:
                    print(f"Line {line_num}: Invalid format, skipping: {line}")
                    error_count += 1
                    continue

                folder_path = root_path / manifest_id

                if manifest_id in processed_folders:
                    print(f"Line {line_num}: Duplicate folder {manifest_id}, skipping")
                    continue

                processed_folders.add(manifest_id)
                dt = parse_timestamp(timestamp_str)
                if not folder_path.exists():
                    print(f"Line {line_num}: Folder not found: {folder_path}")
                    error_count += 1
                    continue

                if not folder_path.is_dir():
                    print(f"Line {line_num}: Path is not a folder: {folder_path}")
                    error_count += 1
                    continue

                epoch_time = dt.timestamp()

                print(f"Processing {manifest_id} - setting date to {dt}")

                try:
                    os.utime(folder_path, (epoch_time, epoch_time))
                    win_time = pywintypes.Time(dt)
                    hfile = win32file.CreateFile(
                        str(folder_path), win32con.GENERIC_WRITE,
                        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                        None, win32con.OPEN_EXISTING,
                        win32con.FILE_FLAG_BACKUP_SEMANTICS, None)
                    win32file.SetFileTime(hfile, win_time, win_time, win_time)
                    hfile.close()
                    success_count += 1
                    print(f"Successfully updated timestamps for {folder_path}")
                except Exception as e:
                    print(f"Line {line_num}: Failed to update timestamps for {folder_path}: {str(e)}")
                    error_count += 1
                    continue
            except Exception as e:
                print(f"Line {line_num}: Error processing line '{line}': {str(e)}")
                error_count += 1
                continue

    except Exception as e:
        print(f"Fatal error processing input file: {str(e)}")
        return False

    print("\nProcessing complete. Summary:")
    print(f"Root path processed: {root_path}")
    print(f"Total entries processed: {len(processed_folders)}")
    print(f"Successfully updated: {success_count}")
    print(f"Errors encountered: {error_count}")

    return error_count == 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_folder_dates.py <root_path> <input_file>")
        print("Example: python update_folder_dates.py X:\\depots\\56534\\ dates.txt")
        print("Example: python update_folder_dates.py X:\\depots\\56534\\ C:\\tmp\\dates.txt")
        sys.exit(1)

    root_path = sys.argv[1]
    input_file = sys.argv[2]

    print(f"Starting folder date updater with root path: {root_path}")
    print(f"Using input file: {input_file}")

    success = update_folder_dates(root_path, input_file)

    if not success:
        print("Completed with errors. Check the log for details.")
        sys.exit(1)

    print("All operations completed successfully.")
