import os
from extract import process_match_data

# Specify the folder path
folder_path = "Datasets/ipl_json"

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    # Check if it is a file (not a folder)
    if os.path.isfile(file_path) & filename.endswith(".json"):
        process_match_data(file_path, folder_path+"_processed")