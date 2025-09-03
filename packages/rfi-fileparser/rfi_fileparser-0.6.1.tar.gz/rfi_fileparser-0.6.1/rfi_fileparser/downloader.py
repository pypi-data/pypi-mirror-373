import os
import requests
import argparse
from rfi_fileparser import util


def generate_urls(all_dates, folder_name):
    if folder_name == "jamming":
        filenames_remote = ['events', 'heatmap'] + [f"{hour:02}00/heatmap" for hour in range(24)]
        urls = ["https://waas-nas.stanford.edu/data/" + folder_name + "/" + sub_date + "/" + filename + ".json" for
                sub_date in all_dates for filename in filenames_remote]
    elif folder_name == "spoofing":
        filenames_remote = ['beforeAndDuringSpoofing', 'duringAndAfterSpoofing', 'events', 'heatmap']
        urls = ["https://waas-nas.stanford.edu/data/" + folder_name + "/" + sub_date + "/" + filename + ".json" for sub_date in
                all_dates for filename in filenames_remote]
    else:
        all_months = set([sub_date[:-3] for sub_date in all_dates])
        urls = ["https://waas-nas.stanford.edu/data/dashboard/general.json"] + \
               ["https://waas-nas.stanford.edu/data/" + folder_name + "/" + sub_month + "/statistics.json" for sub_month in all_months]
    return urls


def download_files(start_date, end_date, data_type):
    # step 0: sanity check of user inputs
    if util.is_valid_date(start_date) and util.is_valid_date(end_date) and util.is_vaild_range(start_date, end_date) and util.is_valid_type(data_type):
        print(f"Processing '{data_type}' files from {start_date} to {end_date} ...")

        # Step 1: List of JSON file URLs
        all_dates = util.dates_in_between(start_date, end_date)
        urls = generate_urls(all_dates, data_type)

        # Step 2: Local folder to save downloaded files
        output_folder = "downloaded_json_files"
        print(os.makedirs(output_folder, exist_ok=True))  # Create folder if it doesn't exist

        # Step 3: Download each file
        for url in urls:
            local_path = url.split('/')[4:-1]
            local_filename = url.split('/')[-1]
            # check if files already exist locally
            if os.path.isfile(os.path.join(output_folder, *local_path, local_filename)):
                continue
            try:
                response = requests.get(url, verify=False)
                response.raise_for_status()  # Raise error if download failed

                # Step 1: Construct full folder path
                full_folder_path = os.path.join(output_folder, *local_path)
                # Step 2: Create directories if they don't exist
                os.makedirs(full_folder_path, exist_ok=True)
                # Step 3: Create full file path
                output_path = os.path.join(full_folder_path, local_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Downloaded: {output_path}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {url}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Download GNSS interference JSON data.")
    parser.add_argument("--start", required=True, help="Start date (YYYY/MM/DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY/MM/DD)")
    parser.add_argument("--type", required=True, choices=["dashboard", "jamming", "spoofing"], help="Data type")

    args = parser.parse_args()
    download_files(args.start, args.end, args.type)
    # download_files("2025/03/23", "2025/03/29", "jamming") # valid_keys = ['dashboard', 'jamming', 'spoofing']


if __name__ == "__main__":
    main()
