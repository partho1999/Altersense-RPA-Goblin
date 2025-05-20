# main.py

from . main_app.main_functions import extract_pdf_data, extract_exporter_refs
from . csv_extraction.csv_functions import save_excel
import pandas as pd

def main(folder_path):

    try:
        print(f'Derived Folder Path: {folder_path}')
        all_invoice_data = extract_pdf_data(folder_path)
        df = pd.DataFrame(all_invoice_data)
        print(df)
        # exporter_refs_df = extract_exporter_refs(folder_path)

        # Print DataFrame to EXCEL file in the same directory
        save_excel(df)


    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    folder_path = sys.argv[1]
    print(f'Folder Path: {folder_path}')
    # main(folder_path)

