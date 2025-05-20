import os
import re
import time
import logging
import pdfplumber
import pandas as pd
from . import extract
from . import all_code
from . import file_validation
from project_settings.settings import BASE_DIR
from apps.commercial.services import create_bot_activity_log, save_po_data
from apps.commercial.schema import ActivityLogSchema

class POExtractor:
    source_directory = os.path.join(BASE_DIR, 'media/purchase_data')

    def __init__(self, source_directory, purchase_order_list, country_breakdown_list):
        self.source_directory = source_directory if source_directory else os.path.join(
            BASE_DIR, 'media/purchase_data')
        self.purchase_order_list = purchase_order_list
        self.country_breakdown_list = country_breakdown_list


def po(request_id):
    source_directory = os.path.join(BASE_DIR, 'media/purchase_data')

    start_time = time.time()

    # Extract Zip files

    try:
        extract.extract(source_directory)
        elapsed_time = time.time() - start_time

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)

    # Construct the full path to the log file within the "Log" folder
    log_file_path = os.path.join(
        f'{source_directory}/result', 'purchase_order_log.log')

    # Configure logging
    logging.basicConfig(level=logging.INFO, filename=log_file_path,
                        format="%(asctime)s - %(levelname)s - %(message)s", filemode="w")
    create_bot_activity_log(ActivityLogSchema(
        activity='PO Extraction', activity_type='Started', request_id=request_id))

    logging.info('Process Started')

    logging.info('Folder Selected')

    logging.info('Extracted Zip Files')

    # Read Pdf list
    pdf_list = os.listdir(f'{source_directory}/unzip')
    # po = purchase order,  tcb = total country breakdown
    purchase_order_list = file_validation.main(pdf_list)
    # 2d list to 1d list
    print(f'Purchase Order List 2d: {purchase_order_list}')
    purchase_order_list = [
        item for sublist in purchase_order_list for item in sublist]
    print(f'Purchase Order List 1d: {purchase_order_list}')
    country_breakdown_list = file_validation.main(pdf_list)
    country_breakdown_list = [
        item for sublist in country_breakdown_list for item in sublist]
    print(f'Country Breakdown List: {country_breakdown_list}')

    # Functions

    def match_pattern(pattern):
        matched = re.search(pattern, text)
        if matched:
            value = matched.group(1)
        else:
            value = None
        return value

    def get_value_after_keyword(lines, keyword):
        for i, line in enumerate(lines):
            if keyword in line:
                return lines[i + 1].strip() if i + 1 < len(lines) else None
        return None

    def get_time(country, tables):
        within_range = False
        for table in tables:
            for row in table:
                if "Time of Delivery" in row:
                    within_range = True
                    continue
                if "Total:" in row:
                    within_range = False
                    continue
                if within_range and country+' ' in row[1]:
                    date = row[0].replace(",", "")
                    return date

    def get_price(country, tables):
        print('Entered get price fucntion')
        avg_price_range = False
        avg_price = ""
        for table in tables:
            for row in table:
                if "Invoice Average Price" in row:
                    avg_price_range = True
                    continue
                if "Created:" in row[0]:
                    avg_price_range = False
                    continue
                if "License Order" in row[0]:
                    avg_price_range = False
                    continue
                if avg_price_range and country in row[1]:
                    avg_price = row[0]
        print(f'Get price: {avg_price}')
        return avg_price

    # Get country name
    def get_total(country, order_number):
        # Iterate through Country list
        # if len(country)>2:
        #     country = country[-2:]
        for country_breakdown in country_breakdown_list:
            if order_number in country_breakdown:
                with pdfplumber.open(f"{source_directory}/unzip/{country_breakdown}") as pdf:
                    page = pdf.pages[0]
                    text = page.extract_text()
                    # lines = text.split('\n')
                    # print(text)
                    # Extract tables from the page
                    tables = page.extract_tables()
                    within_range = False
                    for table in tables:
                        for row in table:
                            # print(row)
                            if "Country" and "Total" in row:
                                within_range = True
                                continue
                            if "Total:" in row:
                                within_range = False
                                continue
                            if within_range and country in row:
                                return row[3]

    logging.info('Extracting Data...')
    create_bot_activity_log(ActivityLogSchema(
        activity='PO Extraction', activity_type='Extracting Data', request_id=request_id))

    # try:
    try:
        for purchase_order in purchase_order_list:
            try:
                print("#" * 50)
                print('For loop PO: ', purchase_order)
                print("#" * 50)
                # Open the PDF file
                with pdfplumber.open(f"{source_directory}/unzip/{purchase_order}") as pdf:
                    # if '803828' in purchase_order:
                    #     print('Accessed the file')
                    page = pdf.pages[0]
                    text = page.extract_text()
                    lines = text.split("\n")
                    tables = page.extract_tables()
                    # if '803828' in purchase_order:
                    #     print('Got the table')
                    po_no_pattern = r"Order No:\s*(\d+-\d+)"
                    no_of_pieces_pattern = r"No of Pieces:\s+(\d+)"

                    customs_customer_group_pattern = r"Customs Customer Group:\s+(.+)"
                    item_pattern = r"Product Description:\s+(.*?)\s+-"
                    item_description_pattern = r"Product Description:\s+.*?- (.+)"

                    invoice_average_price_pattern = r"(\d+\.\d+\s+USD)"

                    # Extract Value

                    po_no = match_pattern(po_no_pattern)
                    order_no = po_no.split("-")[0] + "/*"
                    order_number = po_no.split("-")[0]

                    no_of_pieces = match_pattern(no_of_pieces_pattern)
                    no_of_pieces = int(no_of_pieces)

                    customs_customer_group = match_pattern(
                        customs_customer_group_pattern)

                    item = match_pattern(item_pattern)
                    item_description = match_pattern(item_description_pattern)

                    country_string = get_value_after_keyword(
                        lines, "Terms of Delivery")

                    country_list = list(country_string.split(","))

                    # Replace 'NL/' with an empty string in each item
                    # country_list = [item.replace('NL/', '') for item in country_list]
                    country_list = [item.strip() for item in country_list]

                    # ********************
                    # if '803828' in purchase_order:
                    #     print(f'Country List for {purchase_order}')
                    #     print(country_list)

                    # for i in range(len(country_list)):
                    #     if '/' in country_list[i]:
                    #         parts = country_list[i].split('/')
                    #         country_list[i] = parts[1]
                    extracted_data_return = []
                    for country in country_list:
                        print('For Country Code: ', country)
                        try:
                            delivery_time = get_time(country, tables)
                            delivery_time = pd.to_datetime(
                                delivery_time).date()
                        except:
                            delivery_time = 'Not Found'
                        # if '803828' in purchase_order:
                        print(f'Delivery time: {delivery_time}')
                        # parsed_date = datetime.strptime(delivery_time, "%d %b %Y")
                        # delivery_time = parsed_date.strftime("%d-%b-%Y")

                        # ********** Peanuts Error starts from here *********
                        avg_price = get_price(country, tables)
                        # if '803828' in purchase_order:
                        print(f'Average Price: {avg_price}')
                        currency_value = avg_price.split(' ')[0]
                        currency_value = float(currency_value)
                        currency = avg_price.split(' ')[1]
                        try:
                            currency_name, currency_code = all_code.currency_dict.get(
                                currency.strip())
                        except:
                            currency_name, currency_code = 'Not Found', 'Not Found'
                        total = float(get_total(country, order_number))
                        # if len(country)>2:
                        # if '/' in country:
                        #     splitted = country.split('/')
                        #     country = splitted[1]
                        # country = country[-2:]
                        # print(country)
                        if '/' in country:
                            splitted = country.split('/')
                            print('Splitted: ', splitted)
                            country = splitted[1]
                            try:
                                country_name, country_code = all_code.country_dict.get(
                                    country)
                            except:
                                country_name, country_code = 'Not Found', 'Not Found'
                        else:
                            try:
                                country_name, country_code = all_code.country_dict.get(
                                    country)
                            except:
                                country_name, country_code = 'Not Found', 'Not Found'
                        print(country_name, country_code)
                        # country_code = country_dict.get(country.strip())
                        # country_name = country_name_dict.get(country.strip())
                        quantity_in_pcs = int(no_of_pieces * total)
                        value = total*currency_value
                        # value = float('{:,.2f}'.format(value))
                        description = f'{item} {customs_customer_group}'

                        new_data = {
                            "PO NO": [po_no],
                            "ORDER NO": [order_no],
                            "ITEM": [item],
                            # "ITEM DESCRIPTION": [item_description],
                            "DESCRIPTION": [description],
                            "GENDER": [customs_customer_group],
                            "COUNTRY ISO": [country],
                            "COUNTRY NAME": [country_name],
                            "COUNTRY CODE": [country_code],  # From exp
                            "NO OF PCS PER PACK": [no_of_pieces],
                            "QUANTITY IN PACK": [total],
                            "QUANTITY IN PCS": [quantity_in_pcs],
                            "QUANTITY": [""],
                            "INVOICE AVERAGE PRICE": [avg_price],
                            "CURRENCY ISO": [currency],
                            "CURRENCY NAME": [currency_name],
                            "CURRENCY CODE": [currency_code],  # From exp
                            "VALUE": [value],
                            "DELIVERY TIME": [delivery_time],
                            "S/C NO": [""],
                            'LC NO': [""],
                            'BIN': [""],
                            "AD CODE": [""],
                            "COMMODITY CODE": [""],
                            'INCOTERM': [""],
                            'UNIT CODE': [""],
                            'UNIT': [""],
                            'AREA CODE': [""],
                            "INVOICE NO": [""],
                            'INVOICE DATE': [""],
                            'INVOICE AMOUNT': [""],
                            'CMT AMOUNT': [""],
                            'FREIGHT': [""],
                            'INSURANCE': [""],
                            'OTHER CHARGES': [""],
                            'CARRIER/VESSEL': [""],
                            'DEST PORT': [""],
                            'TRANS DOC TYPE': [""],
                            'TRANS DOC NO': [""],
                            'TRANS DOC DATE': [""],
                            'SHIP PORT': [""],
                            'SECTOR': [""],
                            'FOB AMOUNT': [""],
                            "SIGNATORY ID": [""],
                            "REMARKS": [""],
                            'BANK REF NO': [""],
                            "EXP SERIAL": [""],
                            "EXP YEAR": [""],
                            "FULL EXP": [""],
                            "ISSUE DATE": [""],
                            "EXP STATUS": [""],
                            "BOOKING STATUS": [""],
                        }

                        extracted_data = {
                            "po_no": po_no,
                            "order_no": order_no,
                            "item": item,
                            "description": description,
                            "gender": customs_customer_group,
                            "country_iso": country,
                            "country_name": country_name,
                            "country_code": country_code,
                            "no_of_pcs_per_pack": no_of_pieces,
                            "quantity_in_pack": total,
                            "quantity_in_pcs": quantity_in_pcs,
                            "invoice_average_price": avg_price,
                            "currency_iso": currency,
                            "currency_name": currency_name,
                            "currency_code": currency_code,
                            "value": value,
                            "delivery_time": delivery_time,
                        }
                        # extracted_data_return.append(extracted_data)
                        save_po_data(extracted_data, request_id)
                        create_bot_activity_log(ActivityLogSchema(
                            activity='PO Extraction', activity_type='Data extracted', request_id=request_id))
                        # print("#" * 50)
                        # print("#" * 50)
                        # print('Extracted Data End')
                        # print("#" * 50)
                        # print("#" * 50)
            except Exception as e:
                logging.error(e)
                create_bot_activity_log(ActivityLogSchema(
                    activity='PO Extraction', activity_type=f'Error: {str(e)}', request_id=request_id))

        return extracted_data_return

    except Exception as e:
        logging.error(e)
        raise str(e)
