import time
import sys
import os
import logging
from project_settings.settings import BASE_DIR
from services.fcr_bot.fcr.fcr import Fcr
import pandas as pd

from apps.commercial.services import (
    create_bot_activity_log,
    # TODO: Update fcr status for po
    update_po_status_by_id,
    # TODO: need global config file
    get_booking_config
)

from apps.commercial.schema import (
    ActivityLogSchema
)


def main(data, request_id, username, password):

    create_bot_activity_log(ActivityLogSchema(
        activity_type='FCR', activity='Started', request_id=request_id))

    bot = Fcr(request_id)
    # bot.test()

    create_bot_activity_log(ActivityLogSchema(
        activity_type='FCR', activity='FCR Bot started', request_id=request_id))

    # Land login page
    create_bot_activity_log(ActivityLogSchema(
        activity_type='FCR', activity='Landing on MAERSK login page', request_id=request_id))
    login_page_error = bot.land_login_page()
    if login_page_error:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity=login_page_error, request_id=request_id))
        return login_page_error

    # Login
    damco_server_error = bot.login(username, password)
    if damco_server_error:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity=damco_server_error, request_id=request_id))
        return damco_server_error

    # Check login status
    login_error = bot.login_auth()
    if login_error:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity=f'Login error: {login_error}', request_id=request_id))
        return login_error

    create_bot_activity_log(ActivityLogSchema(
        activity_type='FCR', activity='Logged in', request_id=request_id))

    c = 1

    df = data

    print('**********Data***********: ')
    print("Data: ", df)
    print('**********Data***********: ')

    try:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity='Reading data from fcr config', request_id=request_id))
        # Read data from booking_config
        configs = get_booking_config()

        # print('**********Configs***********: ')
        # print(configs)
        # print('**********Configs***********: ')

        fcr_data = configs['fcr']
        fcr_template = fcr_data['header_tab']['fcr_template']
        additional_desc = fcr_data['marks&numbers_tab']['modified_description']
        delivery_party = fcr_data['parties_tab']['delivery_party']

        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity=f'FCR Config data read successfully!', request_id=request_id))

    except Exception as e:

        create_bot_activity_log(ActivityLogSchema(activity_type='FCR', activity=f'Error reading data from fcr config, error: {e}', request_id=request_id))
        
        return f'{e} could not read data from fcr config file'
    row = df
    # for row in df:

    status = ''
    finish_msg = ''
    print('**********Iteration***********: ', c)
    c += 1
    try:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity=f'Running FCR bot for order no: {c}', request_id=request_id))

        # TODO: Extract data from invoice and update to db
        po_number = row.po_no
        po_number = po_number.split('-')[0]
        country_iso = row.country_iso
        qty = row.quantity
        date = row.invoice_date
        # gd = row.description
        gd = row.composition  # gd = goods description
        inv_number = row.invoice_no
        exp_ref = row.exporters_ref
        full_hs_code = row.hs_code
        hs_code = str(full_hs_code)[:6]
        description = row.description
        order_number = row.po_no

        # Description change
        words = description.split()
        stripped_description = ' '.join(words[:-1])
        modified_description = f'{stripped_description} {additional_desc}'
        gt = modified_description

        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity=f'Running fcr bot for PO: {po_number} Country: {country_iso}', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Searching page', request_id=request_id))
            status = bot.search_page()
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Page searched', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Booking tab', request_id=request_id))
            status = bot.booking_tab()
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Booking tab selected', request_id=request_id))

        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity='Expand filter', request_id=request_id))
        bot.expand_filter()
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity='Filter expanded', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Search PO', request_id=request_id))
            status = bot.po_no(po_number)
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='PO searched', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='SKU', request_id=request_id))
            status = bot.sku(country_iso)
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='SKU selected', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Search PO', request_id=request_id))
            status = bot.search_po()
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='PO searched', request_id=request_id))

        time.sleep(2)

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Select PO', request_id=request_id))
            status = bot.find_fcr(qty)
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='PO selected', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Header tab', request_id=request_id))
            status = bot.select_header_tab()
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Header tab selected', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='FCR template', request_id=request_id))
            status = bot.select_template(fcr_template)
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='FCR template selected', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Select apply btn', request_id=request_id))
            status = bot.select_apply_btn(fcr_template)
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Apply btn selected', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Marks and numbers tab', request_id=request_id))
            status = bot.select_marksandnumbers_tab()
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Marks and numbers tab selected', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Set marks and numbers', request_id=request_id))
            status = bot.set_summary(
                gt, gd, date, order_number, inv_number, exp_ref, hs_code)
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Marks and numbers set', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Parties tab', request_id=request_id))
            status = bot.select_save_type()
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Parties tab selected', request_id=request_id))

        if not status:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Delivery party', request_id=request_id))
            status = bot.save(delivery_party)
            create_bot_activity_log(ActivityLogSchema(
                activity_type='FCR', activity='Delivery party selected', request_id=request_id))

        time.sleep(2)

    except Exception as e:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity=f'FCR Bot failed, error:{str(e)}', request_id=request_id))

    bot.quit()
    create_bot_activity_log(ActivityLogSchema(
        activity_type='FCR', activity='FCR Bot completed, terminating', request_id=request_id))

    create_bot_activity_log(ActivityLogSchema(
        activity_type='FCR', activity='FCR Bot completed',
        request_id=request_id, draft=str(df)))


# if __name__ == "__main__":
#     file_path = sys.argv[1]
#     username = sys.argv[2]
#     password = sys.argv[3]
#     main(file_path, username, password)
