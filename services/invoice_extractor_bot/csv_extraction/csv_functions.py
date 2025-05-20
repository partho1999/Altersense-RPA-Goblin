# csv_extraction/csv_functions.py
from lynko.settings import BASE_DIR
import pandas as pd
import os

def save_excel(df):
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # output_path = os.path.join(BASE_DIR, f'{filename}.xlsx')
    # df.to_excel(output_path, index=False)
    # print(f"The Excel file has been saved in the csv_extraction directory as '{filename}.xlsx'")
    output_excel_file = os.path.join(BASE_DIR, 'media/invoice_extractor_data/invoice_report.xlsx')
    sheet_name = 'InvoiceReport'

    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter', datetime_format='yyyy-mm-dd' ) as writer:
        
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Get the xlsxwriter workbook and worksheet objects.
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Create an Excel table.
        num_rows, num_cols = df.shape
        worksheet.add_table(0, 0, num_rows, num_cols - 1, {'columns': [{'header': col} for col in df.columns]})
