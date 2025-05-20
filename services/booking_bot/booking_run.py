import time
import sys
import os
import logging
from project_settings.settings import BASE_DIR
from . booking.booking import Booking
from . booking.constants import summary_desc
import pandas as pd
# from . import booking_config
from apps.commercial.services import (
    create_bot_activity_log,
    update_po_status_by_id,
    get_booking_config
)
from apps.commercial.schema import (
    ActivityLogSchema
)


# Demo data: {'id': 6, 'po_no': '568081-5832', 'order_no': '568081/*', 'item': 'Vest top', 'gender': 'Men', 'country_iso': 'CL', 'delivery_time': '2023-09-18', 'purchaseorderbooking': {'id': 16, 'summary_marks': 'Dolorum ut quia anim', 'summary_desc': 'Asperiores molestiae', 'no_of_pcs_in_pack': 'Tempora fugiat et di', 'status': 'pending', 'request_id': '386039266e944a05ac52c8295c654d20'}}
# follow this data to the booking bot mainly keys

def main(data, request_id, username, password):

    create_bot_activity_log(ActivityLogSchema(
        activity_type='Booking', activity='Started', request_id=request_id))


    bot = Booking(request_id)

    create_bot_activity_log(ActivityLogSchema(
        activity_type='Booking', activity='Bot started', request_id=request_id))

    # Land login page
    create_bot_activity_log(ActivityLogSchema(
        activity_type='Booking', activity='Landing on login page', request_id=request_id))
    login_page_error = bot.land_login_page()
    if login_page_error:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity=f'Failed to land on login page: {login_page_error}', request_id=request_id))
        # TODO: Stop all process here
        return login_page_error

    # Login
    damco_server_error = bot.login(username, password)
    if damco_server_error:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity=f'Login failed: {damco_server_error}', request_id=request_id))
        # TODO: Stop all process here
        return damco_server_error

    # Check auth fail
    auth_fail_msg = bot.login_auth()
    if auth_fail_msg:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity=f'Authentication failed: {auth_fail_msg}', request_id=request_id))
        # TODO: Stop all process here
        return auth_fail_msg
    
    df = data
    create_bot_activity_log(ActivityLogSchema(
        activity_type='Booking', activity=f'Dataframe: {df}', request_id=request_id))
    try:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity='Reading data from booking config', request_id=request_id))
        # Read data from booking_config
        booking_configs = get_booking_config()
        print("#"*20, "Booking Configs", "#"*20)
        print(booking_configs)
        print("#"*20, "Booking Configs", "#"*20)

        # bookig cong
        booking_data = booking_configs['booking']
        booking_template = booking_data['header']['booking_template']
        construction_type = booking_data['header']['construction_type']
        delivery_party = booking_data['parties']['delivery_party']
        cargo_type = booking_data['details']['cargo_type']
        unit = booking_data['details']['unit']
        package_type = booking_data['details']['package_type']
        qty_in_pack = booking_data['details']['qty_in_pack']
        country_of_origin = booking_data['details']['country_of_origin']
        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity='Read all data from booking config successfully', request_id=request_id))

        # {'booking': {'header': {'product_type': {'hoode': 'Hoodie', 't_shirt': 'T-Shirt', 'vest_top': 'Sweatshirt', 'polo_shirt': 'T-Shirt'}, 'booking_template': 'H&M', 'construction_type': 'Knitted'}, 'details': {'unit': 'PCS', 'hs_code': {'country_code': [{'title': 'ME', 'hs_length': 8}, {'title': 'OD', 'hs_length': 8}]}, 'cargo_type': 'Flatpack', 'qty_in_pack': 50, 'package_type': 'CARTONS', 'summary_desc': {}, 'summary_marks': {}, 'country_of_origin': 'BD'}, 'parties': {'delivery_party': 'H&M HENNES & MAURITZ GBC AB [SEHENNESMAHQ]'}}}

    except Exception as e:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity=f'Failed to read data from booking config, Error:{str(e)}', request_id=request_id))
        return f'{e} could not read data from booking config file'
    # Iterate through the df
    # for index, row in df.items():
    row = df
    status = ''
    finish_msg = ''
    
    def convert_item(item):
            item = item.lower().replace(' ', '_').replace('-', '_')
            if item in booking_data['header']['product_type']:
                return booking_data['header']['product_type'][item]
    
    try:
            
        try:
            po_no = row.get('po_no')
            order_no = row.get('order_no')
            item = row.get('item')
            item = convert_item(item)
            country_iso = row.get('country_iso')
            gender = row.get('gender')
            summary_desc = row.get('purchaseorderbooking')['summary_desc']
            create_bot_activity_log(ActivityLogSchema(
                activity_type='Booking', activity=f'read summary_desc from db : {summary_desc}', request_id=request_id))
            delivery_date = row.get('delivery_time')
            create_bot_activity_log(ActivityLogSchema(
                activity_type='Booking', activity=f'Read delivery time from db successfully: {delivery_date}', request_id=request_id))
            # delivery_date = row.get('delivery_time').date().strftime("%Y-%m-%d")
            create_bot_activity_log(ActivityLogSchema(
                activity_type='Booking', activity=f'Read data from db successfully', request_id=request_id))

        except Exception as e:
            create_bot_activity_log(ActivityLogSchema(
                activity_type='Booking', activity=f'Could not read data from db : {e}', request_id=request_id))

        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity=f'Running booking bot for PO: {po_no} Country: {country_iso}', request_id=request_id))

        # summary_description = summary_desc(po_no)
        
        if not status:
            status = bot.search_page()

        # Search purchase order
        if not status:
            status = bot.search_purchase_order(order_no)

        # Click po_link
        if not status:
            status = bot.click_po_link(order_no)

        # Select booking
        if not status:
            status = bot.select_booking(country_iso)

        # Handle Alert
        if not status:
            status = bot.handle_alert()

        # Header Page
        if not status:
            status = bot.header_page(delivery_date, gender, item, booking_template, construction_type)

        # Parties Page
        if not status:
            status = bot.parties_page(delivery_party)

        # Details Page
        # if not status:country_iso, summary_description, pcs_per_pack, package_type_val, unit_type_val, cargo_type_val, country_of_origin
            status = bot.details_page(country_iso, summary_desc,qty_in_pack, package_type, unit, cargo_type, country_of_origin)

        # Save Booking
        if not status:
            status = bot.save_booking()

        time.sleep(2)

        # Get finish msg
        if not status:
            finish_msg = bot.get_finish_msg()

        time.sleep(2)

    except Exception as e:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='Booking', activity=f'Bot failed, error:{str(e)}', request_id=request_id))
        # if status == '' or status == None:
        #     df.at[index, 'BOOKING STATUS'] = finish_msg
        # else:
        #     df.at[index, 'BOOKING STATUS'] = status

    bot.quit()
    create_bot_activity_log(ActivityLogSchema(
        activity_type='Booking', activity='Bot completed, terminating', request_id=request_id))


if __name__ == "__main__":
    file_path = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    main(file_path, username, password)