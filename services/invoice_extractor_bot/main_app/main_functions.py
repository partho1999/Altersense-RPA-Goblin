# main_app/main_functions.py

from services.invoice_extractor_bot.pdf_extraction.extract_tables_with_pdfplumber import extract_tables_with_pdfplumber
from services.invoice_extractor_bot.main_app.extract_exporter_refs import extract_exporter_refs
from services.invoice_extractor_bot.pdf_extraction.extract_goods_description import extract_goods_description
from services.invoice_extractor_bot.pdf_extraction.extract_description import extract_description
from services.invoice_extractor_bot.pdf_extraction.extract_MOT import extract_MOT
from services.invoice_extractor_bot.pdf_extraction.extract_hm_code import extract_hm_code
from services.invoice_extractor_bot.pdf_extraction.extract_quantity import extract_quantity
from services.invoice_extractor_bot.pdf_extraction.extract_goods_type import extract_goods_type
from services.invoice_extractor_bot.pdf_extraction.extract_hs_code import extract_hs_code
from services.invoice_extractor_bot.pdf_extraction.extract_invoice_dates import extract_invoice_dates
from services.invoice_extractor_bot.pdf_extraction.extract_invoice_numbers import extract_invoice_numbers
from services.invoice_extractor_bot.pdf_extraction.extract_text_with_pdfplumber import extract_text_with_pdfplumber
import os
import pandas as pd
import sys
import uuid
from apps.commercial.services import (
    create_bot_activity_log,
    update_po_status_by_id,
    get_booking_config
)
from apps.commercial.schema import (
    ActivityLogSchema
)

# Adding the parent directory to the system path to enable imports from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def extract_pdf_data(directory):
    try:
        pdf_files = [file for file in os.listdir(
            directory) if file.lower().endswith(('.pdf', '.PDF'))]
        all_invoice_data = []
        for pdf_file in pdf_files:
            request_id = str(uuid.uuid4())
            pdf_path = os.path.join(directory, pdf_file)
            text = extract_text_with_pdfplumber(pdf_path)
            invoice_numbers = extract_invoice_numbers(text)
            invoice_dates = extract_invoice_dates(text)
            hs_codes = extract_hs_code(text)
            goods_types = extract_goods_type(text)
            quantities = extract_quantity(text)
            MOT_values = extract_MOT(text)
            goods_descriptions = extract_goods_description(text)
            hm_codes = extract_hm_code(text)
            exporter_refs = extract_exporter_refs(directory)
            for number, hs_code, goods_type, quantity, MOT, description, hm_code, exporter_ref in zip(
                    invoice_numbers, hs_codes,
                    goods_types, quantities, MOT_values, goods_descriptions, hm_codes,
                    exporter_refs['Exporters Ref']):
                # all_invoice_data.append(
                #     {'INVOICE NO': number, 'INVOICE DATE': invoice_dates, 'EXPORTERS REF': exporter_ref,
                #      'HS CODE': hs_code, 'DESCRIPTION': goods_type, 'COMPOSITION': description,
                #      'QUANTITY': quantity, 'PO NO': hm_code, 'COUNTRY ISO': MOT, 'FCR STATUS': None})
                all_invoice_data.append(
                    {'invoice_no': number, 'invoice_date': invoice_dates, 'exporters_ref': exporter_ref,
                     'hs_code': hs_code, 'description': goods_type, 'composition': description,
                     'quantity': quantity, 'po_no': hm_code, 'country_iso': MOT, 'fcr_status': None,
                     'request_id': request_id})
                # create_bot_activity_log(ActivityLogSchema(
                #     activity_type='Booking', activity='Failed to land on login page', request_id=request_id))

                create_bot_activity_log(ActivityLogSchema(
                    activity_type='Invoice Extraction', activity=f'Extracted invoice data. File:{pdf_file}', request_id=request_id))

        return all_invoice_data
    except Exception as e:
        raise Exception(
            f'Error occurred while extracting data from {directory}: {str(e)}')
