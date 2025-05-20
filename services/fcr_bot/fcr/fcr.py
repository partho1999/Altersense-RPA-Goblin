import os
import pandas as pd
import requests
from project_settings.settings import BASE_DIR
import math
import logging
from . import constants as const
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from apps.commercial.services import create_bot_activity_log
from apps.commercial.schema import ActivityLogSchema
from time import sleep

import uuid
from selenium import webdriver

#  log_configuration
# log_directory = os.path.join(BASE_DIR, 'media/fcr_data')  # LOG DIRECTORY PATH
# log_file_path = os.path.join(log_directory, 'fcr.log') # Define the full path to the log file
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s') # Configure logging to save to the specified file

class Fcr(webdriver.Chrome):
    def __init__(self, request_id, teardown=False):
        # Create Chrome options and add the desired capabilities
        self.request_id = request_id
        self.teardown = teardown
        chromeOptions = webdriver.ChromeOptions()
        driver_path = '/usr/local/bin/chromedriver'
        chromeOptions.add_argument('--headless')
        chromeOptions.add_argument('--disable-gpu')
        chromeOptions.add_argument('--no-sandbox')
        
        self.driver = webdriver.Chrome(
            driver_path, options=chromeOptions)
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        path = 'https://www.googleal.com/'
        self.base_url = path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.driver.quit()
            
    def test(self):
        print("#" * 50)
        print("Test Started")
        self.driver.get('https://www.google.com/')
        print("#" * 50)
        print("https://www.google.com/----title-->>>>>: ", self.driver.title)
        print("#" * 50)
        print("Test Ended")
        print("#" * 50)
        
    def take_screenshot(self, url):
        self.driver.get(url)
        self.driver.save_screenshot("screenshot.png")
        self.driver.quit()
        
    def tearDown(self):
        sleep(5)
        self.driver.quit()

    def quit(self):
        self.driver.quit()

    def try_except_handler(self, func, *args, custom_message=None, exit_process=False, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_message = custom_message or f"An exception occurred in {func.__name__}: {e}"
            logging.error(error_message)  # Replace print with logging.error
            if exit_process:
                self.driver.quit()
                exit()


    def get_element(self, elem_type, elem_val):
        by_type = {
            "ID": By.ID,
            "NAME": By.NAME,
            "XPATH": By.XPATH,
            "TAG_NAME": By.TAG_NAME,
            "LINK_TEXT": By.LINK_TEXT,
            "CLASS_NAME": By.CLASS_NAME,
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
        }
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_type[elem_type], elem_val))
            )
            logging.info("Element found")  # Replace print with logging.info
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Element found', activity_type='Info', request_id=self.request_id))
            return element
        except TimeoutException:
            # If the element is not found within the specified time, handle the timeout
            print("Element Not Found. Skipping...")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Element not found,Skipping', activity_type='Error', request_id=self.request_id))
        except NoSuchElementException:
            # If the element is not found, handle the exception
            print("Element Not Found. Skipping...")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Element not found, Skipping', activity_type='Error', request_id=self.request_id))
        except Exception as e:
            # Handle any other unexpected exceptions
            print(f"An error occurred")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'An error occurred: {str(e)}', activity_type='Error', request_id=self.request_id))

    def get_by_soup(self, page_source, heading):
        soup = BeautifulSoup(page_source, "html.parser")
        product_type_heading = soup.find(text=heading)
        row = product_type_heading.find_parent("tr")
        select_element = row.find("select")
        product_type_id = select_element.get("id")
        return product_type_id

    def land_login_page(self):
        try:
            self.driver.get(const.LOGIN_URL)
            logging.info(f'Bot landed on Maersk login page: {const.LOGIN_URL}')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Bot landed on Maersk login page', activity_type='Info', request_id=self.request_id))
            # self.get('asdfasdf')
        except ConnectionError as e:
            logging.error(f"Failed to connect to the server: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Failed to connect to the server: {e}', activity_type='Error', request_id=self.request_id))
            return 'Connection error: Failed to connect to the server'
        except TimeoutError as e:
            logging.error(f"Request timed out: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Request timed out: {e}', activity_type='Error', request_id=self.request_id))
            return 'Timeout error: Request timed out'
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'An unexpected error occurred: {e}', activity_type='Error', request_id=self.request_id))
            return 'An unexpected error occurred'
        
    def login(self, damco_username, damco_password):
        # Username
        username = self.get_element(
            'ID', "ctl00_ContentPlaceHolder1_UsernameTextBox")
        if username:
            username.clear()
            username.send_keys(damco_username)
            logging.info('Fill up username')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Fill up username', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Username field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Username field not available', activity_type='Error', request_id=self.request_id))
            self.driver.quit()
            return 'Could not load Maersk portal login page'

        # Password
        password = self.get_element(
            'ID', "ctl00_ContentPlaceHolder1_PasswordTextBox")
        if password:
            password.clear()
            password.send_keys(damco_password)
            logging.info('Fill up password')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Fill up password', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Password field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Password field not available', activity_type='Error', request_id=self.request_id))
            self.driver.quit()
            return 'Could not load Maersk portal login page'
        self.driver.implicitly_wait(5)

        # Signin
        signin_button = self.get_element(
            'ID', "ctl00_ContentPlaceHolder1_SubmitButton"
        )
        if signin_button:
            signin_button.click()
            logging.info('Click on signin button')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Click on signin button', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Signin button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Signin button not available', activity_type='Error', request_id=self.request_id))
            self.driver.quit()
            return 'Could not load Maersk portal login page'
        
        

        
    def login_auth(self):
        # Find the search button
        search = self.get_element("XPATH", "//a[normalize-space()='Search']")
        
        # Check if the search button exists
        if search:
            # Click the search button
            logging.info('Login Successful')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Login Successful', activity_type='Info', request_id=self.request_id))
            
        else:
            login_failed_msg = self.get_element("ID", "ctl00_ContentPlaceHolder1_ErrorTextLabel")
            if login_failed_msg:
                error_txt = login_failed_msg.text
                logging.error(f'Login failed: {error_txt}')
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity=f'Login failed: {error_txt}', activity_type='Error', request_id=self.request_id))
                return f'Login failed: {error_txt}'
                
            else:
                logging.error('Login Failed')
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Login Failed', activity_type='Error', request_id=self.request_id))
                return 'Login Failed'

    def search_page(self):
        try:
            self.get(const.SEARCH_URL)
            logging.info(
                f'Navigating to search order page: {const.SEARCH_URL}')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Navigating to search order page', activity_type='Info', request_id=self.request_id))
        except ConnectionError as e:
            logging.error(f"Failed to connect to the server: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Failed to connect to the server: {e}', activity_type='Error', request_id=self.request_id))
            return 'Connection error: Failed to connect to the server'
        except TimeoutError as e:
            logging.error(f"Request timed out: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Request timed out: {e}', activity_type='Error', request_id=self.request_id))
            return 'Timeout error: Request timed out'
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'An unexpected error occurred: {e}', activity_type='Error', request_id=self.request_id))
            return 'An unexpected error occurred'
    
    def booking_tab(self):
        # Find the booking tab button
        booking_tab_btn = self.get_element('ID', 'tab_treetab2')
        
        # Check if the booking tab button exists
        if booking_tab_btn:
            # Click the booking tab button
            booking_tab_btn.click()
            logging.info('Booking tab button clicked')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Booking tab button clicked', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Booking tab not found')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Booking tab not found', activity_type='Error', request_id=self.request_id))
            return 'booking tab not found'
            
    def expand_filter(self):
        # Find the filter button
        filter_btn = self.get_element('ID', 'soMoreBtn')
        
        # Check if the filter button exists
        if filter_btn:
            # Get the text of the filter button
            filter_status = filter_btn.text
            
            # Print the filter status
            logging.info('Filter status: %s', filter_status)
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Booking tab filter status: {filter_status}', activity_type='Info', request_id=self.request_id))
            
        # Check if the filter button exists and its text is 'More filters'
        if filter_btn and filter_status=='More filters':
            # Click the filter button to expand the filter section
            filter_btn.click()
            logging.info('Filter button clicked')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Filter button clicked', activity_type='Info', request_id=self.request_id))
            
            
    def po_no(self, po_number):
        # Find the PO number field by its ID
        po_no_field = self.get_element('ID', 'searchSO_PO_NO')
        
        if po_no_field:
            logging.info('Found PO number field')
            po_no_field.clear()
            logging.info('Cleared PO number field')
            po_no_field.send_keys(f'{po_number}/*')
            logging.info(f'Sent keys to PO number field: {po_number}')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Sent keys to PO number field: {po_number}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('PO number field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='PO number field not available', activity_type='Error', request_id=self.request_id))
            return 'Po no field not available'
            
    def sku(self, country_iso):
        # Find the SKU field by its ID
        sku_field = self.get_element('ID', 'searchSO_SKU')
        
        if sku_field:
            sku_field.clear()
            logging.info('Cleared SKU field')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Found SKU field and cleared the field', activity_type='Info', request_id=self.request_id))
            sku_field.send_keys(f'{country_iso}/*')
            logging.info(f'Sent keys to SKU field: {country_iso}')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Sent keys to SKU field: {country_iso}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('SKU field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'SKU field not available', activity_type='Error', request_id=self.request_id))            
            return 'SKU field not available'
    
    def search_po(self):
        """
        Click the search PO button if found.
        """
        search_po_btn = self.get_element('ID', 'searchSObtn')
        if search_po_btn:
            logging.info('Found search PO button')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Found Search PO button', activity_type='Info', request_id=self.request_id))
            search_po_btn.click()
            logging.info('Clicked search PO button')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Clicked search PO button', activity_type='Info', request_id=self.request_id))
        else:
            logging.warning('Search PO button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Search PO button not available', activity_type='Error', request_id=self.request_id))
            return 'Search button not available'

            
    def find_fcr(self, qty):

        try:
            # Wait for the table to appear
            table = WebDriverWait(self, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dojoxGridContent")))
            logging.info('Found table')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Found data table', activity_type='Info', request_id=self.request_id))
        except TimeoutException:
            logging.error('Table not found, timeout exceeded')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Table not found, timeout exceeded', activity_type='Error', request_id=self.request_id))
            return 'Table could not be loaded'
        
        # Wait for all the rows to appear in the table
        rows = WebDriverWait(table, 30).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))
        logging.info('Found rows')
        create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Found rows in the data table', activity_type='Info', request_id=self.request_id))

        
        for index, row in enumerate(rows):
            try:
                # Extract quantity from each row
                cells = row.find_elements(By.TAG_NAME, "td")
                quantity_cell = cells[29]  # Adjust the index as per your HTML structure
                quantity = quantity_cell.text.strip()
                logging.info('QTY::::::: %s', quantity)
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity=f'Fetched quantity from table: {quantity}', activity_type='Info', request_id=self.request_id))
            

                if quantity == str(qty):
                    logging.info("Qty matches")
                    create_bot_activity_log(ActivityLogSchema(
                        bot='FCR Bot', activity=f'Fetched quantity matched with given quantity: {qty}', activity_type='Info', request_id=self.request_id))

                # Check booking status
                booking_status_cell = cells[10]  # Adjust the index as per your HTML structure
                booking_status = booking_status_cell.text.strip()
                logging.info("Booking Status: %s", booking_status)
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity=f'Fetched booking status from table row: {booking_status}', activity_type='Info', request_id=self.request_id))
                
                # If booking status is "Delivered" and quantity matches,
                # check the checkbox, perform further actions and wait

                # Check if booking status is "Delivered" and quantity matches
                if  quantity == str(qty) and "DELIVERED" in booking_status:
                        # Check the checkbox for the delivered item
                        checkbox_id = f"gridSo_rowSelector_{index}"
                        checkbox = self.find_element(By.ID, checkbox_id)
                        checkbox.click()
                        logging.info(f"Checkbox checked for delivered item at row {index + 1}.")
                        create_bot_activity_log(ActivityLogSchema(
                            bot='FCR Bot', activity=f"Checkbox checked for delivered item at row {index + 1}", activity_type='Info', request_id=self.request_id))

                        # Click the create button to start processing
                        create_button = self.get_element('XPATH', "//button[normalize-space()='Create']")
                        create_button.click()
                        logging.info('Clicked on create button')
                        create_bot_activity_log(ActivityLogSchema(
                            bot='FCR Bot', activity='Clicked on create button', activity_type='Info', request_id=self.request_id))

                        # Click the FCR menu button
                        fcr_button =self.get_element('ID', "FCRMenuId")
                        fcr_button.click()
                        logging.info('Clicked on fcr button')
                        create_bot_activity_log(ActivityLogSchema(
                            bot='FCR Bot', activity='Clicked on fcr button', activity_type='Info', request_id=self.request_id))

                        
                        try:
                            # Wait for the pop-up to appear (adjust timeout as needed)
                            popup = WebDriverWait(self, 5).until(
                                EC.alert_is_present())

                            # Get the text of the pop-up
                            popup_text = popup.text
                            logging.info("Pop-up text: %s", popup_text)
                            create_bot_activity_log(ActivityLogSchema(
                                bot='FCR Bot', activity=f'Pop-up appeared: {popup_text}', activity_type='Info', request_id=self.request_id))


                            # Close the pop-up
                            popup.accept()
                            logging.info("Pop-up closed.")
                            create_bot_activity_log(ActivityLogSchema(
                                bot='FCR Bot', activity='Pop-up closed', activity_type='Info', request_id=self.request_id))
                            return popup_text
                            
                        except TimeoutException:
                            logging.info("No pop-up appeared within the specified time. Continuing with the rest of the process.")
                            create_bot_activity_log(ActivityLogSchema(
                                bot='FCR Bot', activity='No pop-up appeared within the specified time. Continuing with the rest of the process.', activity_type='Info', request_id=self.request_id))

                            
                
                elif quantity == str(qty) and "CONFIRMED" in booking_status:
                    # If the booking status is "Confirmed", return a message indicating this
                    logging.info("Status: Confirmed. Skipping ...")
                    create_bot_activity_log(ActivityLogSchema(
                        bot='FCR Bot', activity='Status: Confirmed. Skipping ...', activity_type='Info', request_id=self.request_id))
                    return "Status on the booking must be partially or fully delivered in order to create FCR"
                                 
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity=f'An error occurred: {e}', activity_type='Error', request_id=self.request_id))

                

    def select_header_tab(self):
        try:
            # Wait until the header tab is clickable
            headertab = WebDriverWait(self, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Header']"))
            )
            headertab.click()
            logging.info("Header tab clicked.")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Header tab clicked', activity_type='Info', request_id=self.request_id))

        except TimeoutException:
            logging.warning('Header tab not available.')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Header tab not available', activity_type='Error', request_id=self.request_id))
            return 'Header tab not available'


    def select_template(self, fcr_template):
        # Select the template option
        template = self.get_element("XPATH", "//select[@id='TemplateId']")
        if template:
            template_dropdown = Select(template)
            template_dropdown.select_by_visible_text(fcr_template)
            logging.info(f'Template selected: {fcr_template}')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Template selected: {fcr_template}', activity_type='Info', request_id=self.request_id))
        else:
            logging.warning('Template not available.')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Template field not available', activity_type='Error', request_id=self.request_id))
            return 'Template field not available'


    def select_apply_btn(self, fcr_template):
        # Click the apply button
        apply_button = self.get_element('XPATH', "//input[@value='Apply']")
        if apply_button:
            apply_button.click()
            logging.info(f'Template Applied: {fcr_template}')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Template Applied: {fcr_template}', activity_type='Info', request_id=self.request_id))
        else:
            logging.warning('Apply button not available.')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Apply button not available', activity_type='Error', request_id=self.request_id))
            return 'Apply button not available'

    def select_marksandnumbers_tab(self):
        # Click the 'Marks & numbers' tab
        marksandnumbers_tab = self.get_element('XPATH', "//span[normalize-space()='Marks & numbers']")
        if marksandnumbers_tab:
            marksandnumbers_tab.click()
            logging.info("Marks and numbers tab clicked.")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Marks and numbers tab clicked', activity_type='Info', request_id=self.request_id))

        else:
            logging.warning('Marks and numbers tab not available.')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Marks and numbers tab not available', activity_type='Error', request_id=self.request_id))
            return 'Marks and numbers tab not available'


    def set_summary(self, gt, gd, date, order_number, inv_number, exp_ref, hs_code):
        # Clear the summary field and set its text
        summary_field = self.get_element('XPATH', "//textarea[@id='descriptionTextId']")
        if summary_field:
            summary_field.clear()
            updated_summary = f"{gt}\n\n{gd}\nORDER NO:{order_number}\nINV NO:{inv_number} DATE:{date}\nCONT. NO:{exp_ref}\n{hs_code}\n"
            summary_field.send_keys(updated_summary)
            logging.info(f"Setting summary field text to: {updated_summary}")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Setting summary field text to: {updated_summary}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('summary field is invalid')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Summary field is invalid', activity_type='Error', request_id=self.request_id))            
            return 'summary field is invalid'


    def select_save_type(self):
        save_type_btn = self.get_element('ID', 'fcrStatus')
        if save_type_btn:
            save_type_dropdown = Select(save_type_btn)
            save_type_dropdown.select_by_visible_text('finished')
            logging.info("Select save type as finished from dropdown")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Select save type as finished from dropdown', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Save type button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Marks and numbers tab not available', activity_type='Error', request_id=self.request_id))
            return 'Save type button not available'

    def save(self, delivery_party):
        save = self.get_element('ID', 'save_definition')
        save.click()
        try:
            # Wait for the pop-up to appear (adjust timeout as needed)
            popup = WebDriverWait(self, 5).until(
                EC.alert_is_present())

            # Get the text of the pop-up
            popup_text = popup.text
            logging.info("Pop-up text: %s", popup_text)
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity=f'Pop-up appeared: {popup_text}', activity_type='Info', request_id=self.request_id))

            # Close the pop-up
            popup.accept()
            logging.info("Pop-up closed.")
            create_bot_activity_log(ActivityLogSchema(
                bot='FCR Bot', activity='Pop-up closed', activity_type='Info', request_id=self.request_id))

            # Visit party tab
            parties_tab = self.get_element('XPATH', "//span[normalize-space()='Parties']")
            if parties_tab:
                parties_tab.click()
                logging.info("Successfully clicked parties tab")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Successfully clicked parties tab', activity_type='Info', request_id=self.request_id))
            else:
                logging.error("Parties tab not available. Continuing without clicking.")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Parties tab not available. Continuing without clicking', activity_type='Error', request_id=self.request_id))

            # Select Delivery Party
            notify_party_group_1_dropdown = self.get_element('ID', "notifyParty1ListId")
            if notify_party_group_1_dropdown:
                notify_party_group_1_dropdown = Select(notify_party_group_1_dropdown)
                notify_party_group_1_dropdown.select_by_visible_text(delivery_party)
                logging.info(f"Successfully selected {delivery_party} from notify party group 1 dropdown")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity=f'Successfully selected {delivery_party} from notify party group 1 dropdown', activity_type='Info', request_id=self.request_id))
            else:
                logging.warning("Notify party group 1 dropdown not found. Continuing without selecting.")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Notify party group 1 dropdown not found. Continuing without selecting', activity_type='Error', request_id=self.request_id))                

            #Save as 
            save_type_btn = self.get_element('ID', 'fcrStatus')
            if save_type_btn:
                save_type_dropdown = Select(save_type_btn)
                save_type_dropdown.select_by_visible_text('finished')
                logging.info("Select save type as finished from dropdown")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Select save type as finished from dropdown', activity_type='Info', request_id=self.request_id))                
            else:
                logging.error('Save type button not available')
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Save type button not available', activity_type='Error', request_id=self.request_id))                                
                return 'Save type button not available'
            
            # Save btn
            save_btn = self.get_element('ID', 'save_definition')
            if save_btn:
                save_btn.click()
                time.sleep(7)
                logging.info("Successfully clicked save button")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Successfully clicked save button', activity_type='Info', request_id=self.request_id))                                
            else:
                logging.warning("Save button not available. Continuing without clicking.")
                create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='Save button not available. Continuing without clicking', activity_type='Error', request_id=self.request_id))                                

        except TimeoutException:
            logging.info("No pop-up appeared within the specified time. Continuing with the rest of the process.")
            create_bot_activity_log(ActivityLogSchema(
                    bot='FCR Bot', activity='No pop-up appeared within the specified time. Continuing with the rest of the process', activity_type='Info', request_id=self.request_id))