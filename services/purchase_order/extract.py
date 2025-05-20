import os
import zipfile
import shutil

def extract(source_directory):

    # Define the source directory and subfolder names
    # source_directory = '/path/to/source_folder'
    zip_subfolder = 'zip'
    unzip_subfolder = 'unzip'
    result_subfolder = 'result'

    # Create subdirectories if they don't exist
    def create_directory(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Create the subdirectories
    create_directory(os.path.join(source_directory, zip_subfolder))
    create_directory(os.path.join(source_directory, unzip_subfolder))
    create_directory(os.path.join(source_directory, result_subfolder))

    # Loop through the files in the source directory
    for root, _, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.zip'):
                zip_file_path = os.path.join(root, file)
                
                # Move the zip file to the 'zip' subfolder
                destination_zip_path = os.path.join(source_directory, zip_subfolder, file)
                shutil.move(zip_file_path, destination_zip_path)
                
                # Extract the contents to the 'unzip' subfolder without creating subfolders
                with zipfile.ZipFile(destination_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(source_directory, unzip_subfolder))
                
                # print(f"Moved '{file}' to '{zip_subfolder}' and extracted to '{unzip_subfolder}'")
            else:
                other_file_path = os.path.join(root, file)
                
                # Move the other file to the 'unzip' subfolder
                destination_unzip_path = os.path.join(source_directory, unzip_subfolder, file)
                shutil.move(other_file_path, destination_unzip_path)

    # Perform any additional processing in the 'result' subfolder as needed
    result_directory = os.path.join(source_directory, result_subfolder)
    create_directory(result_directory)

    # Your additional processing logic can go here
    # For example, you can move or process the extracted files in the 'unzip' folder

    # print(f"Finished processing. Results can be found in '{result_directory}'.")




