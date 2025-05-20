import os
import math
import time
import logging
from . import constants as const
from project_settings.settings import BASE_DIR
from bs4 import BeautifulSoup
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

# Demo data: {'id': 6, 'po_no': '568081-5832', 'order_no': '568081/*', 'item': 'Vest top', 'gender': 'Men', 'country_iso': 'CL', 'delivery_time': '2023-09-18', 'purchaseorderbooking': {'id': 16, 'summary_marks': 'Dolorum ut quia anim', 'summary_desc': 'Asperiores molestiae', 'no_of_pcs_in_pack': 'Tempora fugiat et di', 'status': 'pending', 'request_id': '386039266e944a05ac52c8295c654d20'}}
# follow this data to the booking bot mainly keys


class Booking(webdriver.Chrome):

    def __init__(self, request_id, teardown=False):
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

    def try_except_handler(
        self, func, *args, custom_message=None, exit_process=False, **kwargs
    ):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_message = (
                custom_message or f"An exception occurred in {func.__name__}: {e}"
            )

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
            # Add more types as needed
        }
        try:
            # Use an explicit wait to wait for the element with the specified XPath
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((by_type[elem_type], elem_val))
            )
            # If the element is found, click on it to close the popup
            # print("Element found")
            # create_bot_activity_log(ActivityLogSchema(
            #     bot='Booking Bot', activity=f'Element found', activity_type='Info', request_id=self.request_id))

            return element
        except TimeoutException as e:
            # If the element is not found within the specified time, handle the timeout
            logging.error(f"Element Not Found. Skipping...: {str(e)}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f"Element Not Found. Skipping...: {str(e)}", activity_type='Error', request_id=self.request_id))
        except NoSuchElementException as e:
            # If the element is not found, handle the exception
            logging.error(f"Element Not Found. Skipping...: {str(e)}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f"Element Not Found. Skipping...: {str(e)}", activity_type='Error', request_id=self.request_id))
        except Exception as e:
            # Handle any other unexpected exceptions
            logging.error(f"An error occurred: {str(e)}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'An error occurred: {str(e)}', activity_type='Error', request_id=self.request_id))
            # print(f"An error occurred: {str(e)}")

    def get_by_soup(self, page_source, heading):
        try:
            # Use BeautifulSoup to parse the HTML
            soup = BeautifulSoup(page_source, "html.parser")

            # Find the element by its text content
            product_type_heading = soup.find(text=heading)

            # Find the parent row of the 'Product Type' element
            row = product_type_heading.find_parent("tr")

            # Find the select element within this row
            select_element = row.find("select")

            # Select the 'Apron' option from the dropdown (assuming value is 'Apron')
            product_type_id = select_element.get("id")

            return product_type_id
        except Exception as e:
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Exception by beautiful soup: {str(e)}', activity_type='Error', request_id=self.request_id))
            return {'Exception by beautiful soup': e}

    def land_login_page(self):
        try:
            self.driver.get(const.LOGIN_URL)
            print(f'Bot landed on Maersk login page: {const.LOGIN_URL}')
            logging.info(f'Bot landed on Maersk login page: {const.LOGIN_URL}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Bot landed on Maersk login page: {const.LOGIN_URL}', activity_type='Info', request_id=self.request_id))
            # self.get('asdfasdf')
        except ConnectionError as e:
            logging.error(f"Failed to connect to the server: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Failed to connect to the server: {e}', activity_type='Error', request_id=self.request_id))
            return 'Connection error: Failed to connect to the server'
        except TimeoutError as e:
            logging.error(f"Request timed out: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Request timed out: {e}', activity_type='Error', request_id=self.request_id))
            return 'Timeout error: Request timed out'
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'An unexpected error occurred: {e}', activity_type='Error', request_id=self.request_id))
            return 'An unexpected error occurred'

    def login(self, damco_username, damco_password):
        # try:
            
        # Username
        username = self.get_element(
            'ID', "ctl00_ContentPlaceHolder1_UsernameTextBox")
        if username:
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Username field found. Username: {damco_username}', activity_type='Info', request_id=self.request_id))

            username.clear()
            # username.send_keys(damco_username)
            username.send_keys('maliko')
            logging.info('Fill up username')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Fill up username', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Username field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Username field not available', activity_type='Error', request_id=self.request_id))
            self.driver.quit()
            return 'Could not load Maersk portal login page'

        # Password
        password = self.get_element(
            'ID', "ctl00_ContentPlaceHolder1_PasswordTextBox")
        if password:
            password.clear()
            # password.send_keys(damco_password)
            password.send_keys('Sjr8Qnc5')
            logging.info('Fill up password')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Fill up password', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Password field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Password field not available', activity_type='Error', request_id=self.request_id))
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
                bot='Booking Bot', activity='Click on signin button', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Signin button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Signin button not available', activity_type='Error', request_id=self.request_id))
            self.driver.quit()
            return 'Could not load Maersk portal login page'
        # except Exception as e:
        #     create_bot_activity_log(ActivityLogSchema(
        #             bot='Booking Bot', activity=f'Login error occurred: {e}', activity_type='Error', request_id=self.request_id))

            
    def auth_fail(self):
        auth_elem = self.get_element(
            'ID', 'ctl00_ContentPlaceHolder1_ErrorTextLabel')
        if auth_elem:
            logging.error('Authentication error! Invalid Username or Password')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Authentication error! Invalid Username or Password', activity_type='Error', request_id=self.request_id))
            self.driver.quit()
            return 'Invalid username or password'
    
    def login_auth(self):
        # Find the search button
        search = self.get_element("XPATH", "//a[normalize-space()='Search']")
        
        # Check if the search button exists
        if search:
            # Click the search button
            logging.info('Login Successful')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Login Successful', activity_type='Info', request_id=self.request_id))
            
        else:
            login_failed_msg = self.get_element("ID", "ctl00_ContentPlaceHolder1_ErrorTextLabel")
            if login_failed_msg:
                error_txt = login_failed_msg.text
                logging.error(f'Login failed: {error_txt}')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity=f'Login failed: {error_txt}', activity_type='Error', request_id=self.request_id))
                return f'Login failed: {error_txt}'
                
            else:
                logging.error('Login Failed')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity='Login Failed', activity_type='Error', request_id=self.request_id))
                return 'Login Failed'

    def search_page(self):
        try:
            self.driver.get(const.SEARCH_URL)
            logging.info(
                f'Navigating to search order page: {const.SEARCH_URL}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Navigating to search order page', activity_type='Info', request_id=self.request_id))
        except ConnectionError as e:
            logging.error(f"Failed to connect to the server: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Failed to connect to the server: {e}', activity_type='Error', request_id=self.request_id))
            return 'Connection error: Failed to connect to the server'
        except TimeoutError as e:
            logging.error(f"Request timed out: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Request timed out: {e}', activity_type='Error', request_id=self.request_id))
            return 'Timeout error: Request timed out'
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'An unexpected error occurred: {e}', activity_type='Error', request_id=self.request_id))
            return 'An unexpected error occurred'

    def search(self):
        # Search Button
        search = self.get_element("XPATH", "//a[normalize-space()='Search']")
        if search:
            search.click()
            logging.info('Click on search button')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on search button', activity_type='Info', request_id=self.request_id))
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on search button', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Search btn not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Search btn not available', activity_type='Error', request_id=self.request_id))
            return 'Search btn not available'

    def search_purchase_order(self, order_no):
        purchase_order_tab = self.get_element(
            "XPATH", "//span[normalize-space()='Purchase Order']"
        )
        if purchase_order_tab:
            purchase_order_tab.click()
            logging.info('Click on purchase order tab')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on purchase order tab', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Purchase order tab not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Purchase order tab not available', activity_type='Error', request_id=self.request_id))
            return 'Purchase order tab not available'

        # Input PO Number
        po_number = self.get_element('XPATH', "//input[@id='searchPO_PO_No']")
        if po_number:
            po_number.clear()
            po_number.send_keys(order_no)
            logging.info(f'Fill up purchase order number: {order_no}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Fill up purchase order number: {order_no}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Purchase order field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Purchase order field not available', activity_type='Error', request_id=self.request_id))
            return 'Purchase order field not available'
        # Click Seaerch button
        search_po_btn = self.get_element('ID', "searchPObtn")
        if search_po_btn:
            search_po_btn.click()
            logging.info('Click search purchase order')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click search purchase order', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Search purchase order button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Search purchase order button not available', activity_type='Error', request_id=self.request_id))
            return 'Search purchase order button not available'

    def handle_po_error(self):
        search_error_elem = self.get_element('ID', 'poErrorMsg')
        if search_error_elem:
            logging.error(f'No Purchase Orders found matching the search criteria for {order_no}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'No Purchase Orders found matching the search criteria for {order_no}', activity_type='Error', request_id=self.request_id))
            return f'No Purchase Orders found matching the search criteria for {order_no}'
        else:
            logging.info('No error msg found after search po. Proceeding with the rest of the process')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='No error msg found after search po. Proceeding with the rest of the process', activity_type='Info', request_id=self.request_id))


    def click_po_link(self, order_no):
        # Check PO Number
        '''
        
        select_po = self.get_element("XPATH", "//div[@id='grid_rowSelector_0']")
        if select_po:
            select_po.click()
            logging.info(f'Select checkbox for order no: {order_no}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select checkbox for order no: {order_no}', activity_type='Info', request_id=self.request_id))
            
        else:
            logging.info(f'No purchase orders found for order no: {order_no}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'No purchase orders found for order no: {order_no}', activity_type='Info', request_id=self.request_id))
            return f'No purchase orders found for order no: {order_no}'
        
        '''
        try:
            xpath_order_no = order_no[:6]
        except Exception as e:
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Could not slice order no: {order_no}', activity_type='Error', request_id=self.request_id))

        # Click Po Link
        po_no_link = self.get_element('XPATH', f"//*[contains(text(), '{xpath_order_no}')]")
        if po_no_link:
            po_no_link.click()
            logging.info(f'Clicked po link for order no: {order_no}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Clicked po link for order no: {order_no}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error(f'No purchase orders found for order no: {order_no}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'No purchase orders found for order no: {order_no}', activity_type='Ifo', request_id=self.request_id))
            return f'No purchase orders found for order no: {order_no}'

    def select_booking(self, country_iso):
        create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Bot started select booking function', activity_type='Info', request_id=self.request_id))

        country_elem = self.get_element(
            "XPATH", f"//*[contains(text(), '{country_iso}/')]"
        )
        if country_elem:
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Row matched with {country_iso}', activity_type='Info', request_id=self.request_id))

        else:
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'No country matched with {country_iso}', activity_type='Info', request_id=self.request_id))

            return f'No country matched with {country_iso}'

        # Get the row country elem resides in
        row = country_elem.find_element(By.XPATH, "./ancestor::tr")

        # Find the checkbox within the row by its name
        checkbox = row.find_element(
            By.XPATH, ".//input[@name='chk' and @type='checkbox']"
        )

        if checkbox:
            checkbox.click()
            logging.info(f'Click chcekcbox for country: {country_iso}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Click chcekcbox for country: {country_iso}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error(f'No country matched with: {country_iso}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'No country matched with: {country_iso}', activity_type='Error', request_id=self.request_id))
            return f'No country matched with: {country_iso}'
        # Click select booking
        book_selected = self.get_element(
            'XPATH', "//a[text()='Book selected']")
        if book_selected:
            book_selected.click()
            logging.info('Click select booking button')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click select booking button', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Select booking button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Select booking button not available', activity_type='Error', request_id=self.request_id))
            return 'Select booking button not available'

    def handle_alert(self):
        # try:
        #     alert = Alert(self)
        #     alert_text = alert.text
        #     # alert.dismiss()
        #     # print('dismissed alert')
        #     # print(f'Alert Text: {alert_text}')
        #     logging.error(f'Alert found: {alert_text}')
        #     create_bot_activity_log(ActivityLogSchema(
        #         bot='Booking Bot', activity=f'Alert found: {alert_text}', activity_type='Error', request_id=self.request_id))
        #     return f'Alert found: {alert_text}'
        # except:
        #     return None
        create_bot_activity_log(ActivityLogSchema(
            bot='Booking Bot', activity='Starting handle alert function', activity_type='Info', request_id=self.request_id))

        try:
            wait = WebDriverWait(self.driver, 5)
            alert = wait.until(EC.alert_is_present())
            if alert:
                alert_text = alert.text
                logging.info(f'Alert found: {alert_text}')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity=f'Alert found: {alert_text}', activity_type='Info', request_id=self.request_id))
                alert.dismiss()
                logging.info('Dismissed alert and prceeding with rest of the process')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity='Dismissed alert and prceeding with rest of the process', activity_type='Info', request_id=self.request_id))
                return alert_text
        except TimeoutException:
            # Handle the case where alert is not found within the timeout
            logging.info('No alert found after clicking select booking, proceeding without handling it')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='No alert found after clicking select booking, proceeding without handling it', activity_type='Info', request_id=self.request_id))



    def header_page(self, delivery_date, gender, item, template, construction_type):
        # Click header tab
        header_tab = self.get_element(
            "XPATH", "//td[@id='tab_treetab1']//span[contains(text(),'Header')]"
        )
        if header_tab:
            header_tab.click()
            logging.info('Click on header tab')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on header tab', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Header tab not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Header tab not available', activity_type='Error', request_id=self.request_id))
            return 'Header tab not available'
        # Delivery Date
        estimated_delivery_date = self.get_element(
            'XPATH', "//input[@id='estmDlvrDtId']"
        )
        if estimated_delivery_date:
            estimated_delivery_date.send_keys(delivery_date)
            logging.info(f'Select delivery date: {delivery_date}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select delivery date: {delivery_date}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Delivery date field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Delivery date field not available', activity_type='Error', request_id=self.request_id))
            return 'Delivery date field not available'

        # Select Template
        booking_template = self.get_element(
            'XPATH', "//select[@id='EditSOForm_soTemplateId']"
        )
        if booking_template:
            booking_dropdown = Select(booking_template)
            booking_dropdown.select_by_visible_text(template)
            logging.info(f'Select booking template: {template}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select booking template: {template}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Booking template field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Booking template field not available', activity_type='Error', request_id=self.request_id))
            return 'Booking template field not available'

        # Apply Template
        apply_button = self.get_element('XPATH', "//input[@id='ApplyBtnId']")
        if apply_button:
            apply_button.click()
            logging.info('Click on apply button')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on apply button', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Apply button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Apply button not available', activity_type='Error', request_id=self.request_id))
            return 'Apply button not available'

        # Get current page source
        page_source = self.driver.page_source

        # Product Type
        try:
            product_type_id = self.get_by_soup(page_source, "Product Type")
            product_type_element = self.get_element('ID', product_type_id)
            product_type_dropdown = Select(product_type_element)
            product_type_dropdown.select_by_visible_text(item)
            logging.info(f'Select product type: {item}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select product type: {item}', activity_type='Info', request_id=self.request_id))
        except:
            logging.error(f'Item {item} Not Matched')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Item {item} Not Matched', activity_type='Error', request_id=self.request_id))
            return f'Item {item} Not Matched'
        # Gender
        gender_id = self.get_by_soup(page_source, "Gender")
        gender_element = self.get_element('ID', gender_id)
        if gender_element:
            gender_dropdown = Select(gender_element)
            gender_dropdown.select_by_visible_text(gender)
            logging.info(f'Select gender: {gender}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f"Select gender: {gender}", activity_type='Info', request_id=self.request_id))
        else:
            logging.error(f'Gender {gender} not matched')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Gender {gender} not matched', activity_type='Error', request_id=self.request_id))
            return f'Gender {gender} not matched'

        # print('moved to gender dropdown')

        # Construction
        construction_id = self.get_by_soup(page_source, "Construction")
        construction_element = self.get_element('ID', construction_id)
        if construction_element:
            construction_dropdown = Select(construction_element)
            construction_dropdown.select_by_visible_text(construction_type)
            logging.info(f'Select construction type: {construction_type}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select construction type: {construction_type}', activity_type='Info', request_id=self.request_id))

        else:
            logging.error(f'Construction type {construction_type} not matched')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Construction type {construction_type} not matched', activity_type='Error', request_id=self.request_id))
            return f'Construction type {construction_type} not matched'
        

    def parties_page(self, delivery_party_val):
        # Parties Tab
        parties_tab = self.get_element(
            "XPATH", "//span[normalize-space()='Parties']")
        if parties_tab:
            parties_tab.click()
            logging.info('Click on Parties tab')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on Parties tab', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Parties tab not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Parties tab not available', activity_type='Error', request_id=self.request_id))
            return 'Parties tab not available'

        # Select Delivery Party
        delivery_party = self.get_element(
            'XPATH', "//select[@id='delvPartyGrpId']")
        if delivery_party:
            delivery_party_dropdown = Select(delivery_party)
            delivery_party_dropdown.select_by_visible_text(delivery_party_val)
            logging.info(f'Select delivery party: {delivery_party_val}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select delivery party: {delivery_party_val}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error(f'Delivery party: {delivery_party_val} not matched')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Delivery party: {delivery_party_val} not matched', activity_type='Error', request_id=self.request_id))
            return f'Delivery party: {delivery_party_val} not matched'

    def details_page(self, country_iso, summary_description, pcs_per_pack, package_type_val, unit_type_val, cargo_type_val, country_of_origin):
        # default html attribute value is set to 0. element.clear() can not remove 0
        def clear_and_sendkey(element, value):
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            element.send_keys(value)

        # Details Tab
        details_tab = self.get_element(
            "XPATH", "//span[normalize-space()='Details']")
        if details_tab:
            details_tab.click()
            logging.info('Click on Details tab')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on Details tab', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Details tab not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Details tab not available', activity_type='Error', request_id=self.request_id))
            return 'Details tab not available'
        # Summary Marks
        summary_marks = self.get_element(
            'XPATH', "//textarea[@id='summMkNum']")
        if summary_marks:
            summary_marks.send_keys(country_iso)
            logging.info(f'Fill up summary marks with value: {country_iso}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Fill up summary marks with value: {country_iso}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Summary marks field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Summary marks field not available', activity_type='Error', request_id=self.request_id))
            return 'Summary marks field not available'
        # Summary Description
        summary_description_element = self.get_element(
            'XPATH', "//textarea[@id='summDesc']"
        )
        if summary_description_element:
            summary_description_element.send_keys(summary_description)
            logging.info(
                f'Fill up Summary description with value: {summary_description} ')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Fill up Summary description with value: {summary_description} ', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Summary description field not avilable')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Summary description field not avilable', activity_type='Error', request_id=self.request_id))
            return 'Summary description field not avilable'
        # Select Cargo Type
        cargo_type = self.get_element('ID', "cargoTypeId")
        if cargo_type:
            cargo_type_dropdown = Select(cargo_type)
            cargo_type_dropdown.select_by_visible_text(cargo_type_val)
            logging.info(f'Select cargo type: {cargo_type_val}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select cargo type: {cargo_type_val}', activity_type='Info', request_id=self.request_id))
        else:
            logging.info('Cargo type field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Cargo type field not available', activity_type='Error', request_id=self.request_id))
        # Select Unit type
        unit_type = self.get_element('ID', "qtyUnitId0")
        if unit_type:
            unit_type_dropdown = Select(unit_type)
            unit_type_dropdown.select_by_visible_text(unit_type_val)
            logging.info(f'Select unit type: {unit_type_val}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select unit type: {unit_type_val}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Unit type field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Unit type field not available', activity_type='Error', request_id=self.request_id))
            return 'Unit type field not available'

        # Select Package type
        package_type = self.get_element('ID', "pkgUnitId0")
        if package_type:
            package_type_dropdown = Select(package_type)
            package_type_dropdown.select_by_visible_text(package_type_val)
            logging.info(f'Select package type: {package_type_val}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Select package type: {package_type_val}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Package type field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Package type field not available', activity_type='Error', request_id=self.request_id))
            return 'Package type field not available'

        # Get Quantity
        quantity_element = self.get_element('ID', "bookedQtyId0")
        if quantity_element:
            quantity = quantity_element.get_attribute("value")
            logging.info(
                f'Extracted total quantity from quantity field: {quantity}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Extracted total quantity from quantity field: {quantity}', activity_type='Info', request_id=self.request_id))
            quantity = int(quantity)
            quantity = math.ceil(quantity / pcs_per_pack)
            logging.info(
                f'Qty in pack: {pcs_per_pack} Calculated quantity : {quantity}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Qty in pack: {pcs_per_pack} Calculated quantity : {quantity}', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Quantity field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Quantity field not available', activity_type='Error', request_id=self.request_id))
            return 'Quantity field not available'
        # print(quantity)

        # Set package value
        packages_element = self.get_element(
            'XPATH', "//input[@id='bookedPackagesId0']")
        if packages_element:
            clear_and_sendkey(packages_element, quantity)
            logging.info('Fill up quantity in package')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Fill up quantity in package', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Packages field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Packages field not available', activity_type='Error', request_id=self.request_id))
            return 'Packages field not available'

        # HTS
        hts_code_field = self.get_element(
            'XPATH', "//input[@id='EditSOForm_soDto_soLineDtoList_0__soLineHtsDtoList_0__htsCode']"
        )
        if hts_code_field:
            hts_code = hts_code_field.get_attribute("value")
            logging.info(
                f'hts code field is present. Extracted code from hts field: {hts_code}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'hts code field is present. Extracted code from hts field: {hts_code}', activity_type='Info', request_id=self.request_id))
            # print('hts code',hts_code)
            if country_iso == 'ME' or country_iso == 'OD':
                hts_code = hts_code[:8]
                logging.info(
                    f'Country is ME/OD. Resizing hts code to 8 digit. New hts code: {hts_code} ')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity=f'Country is ME/OD. Resizing hts code to 8 digit. New hts code: {hts_code}', activity_type='Info', request_id=self.request_id))
            else:
                hts_code = hts_code[:6]
                logging.info(
                    f'Country is not ME/OD. Resizing hts code to 6 digit. New hts code: {hts_code}')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity=f'Country is not ME/OD. Resizing hts code to 6 digit. New hts code: {hts_code}', activity_type='Info', request_id=self.request_id))
            # hts_code_field.clear()
            # hts_code_field.send_keys(hts_code)
            clear_and_sendkey(hts_code_field, hts_code)
            logging.info('Fill up hts code')
            create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity='Fill up hts code', activity_type='Info', request_id=self.request_id))
        else:
            add_hts_code = self.get_element(
                'XPATH', "//input[@title='Add new HTSUS line']")
            logging.info(
                'Hts code field is not available. Bot will add the code field')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Hts code field is not available. Bot will add the code field', activity_type='Info', request_id=self.request_id))
            if add_hts_code:
                add_hts_code.click()
                logging.info('Add hts code field')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity='Bot added hts code field', activity_type='Info', request_id=self.request_id))
            hts_code_field = self.get_element(
                'XPATH', "//input[@id='EditSOForm_soDto_soLineDtoList_0__soLineHtsDtoList_0__htsCode']")
            if hts_code_field:
                if country_iso == 'ME' or country_iso == 'OD':
                    # hts_code_field.send_keys('61091000')
                    clear_and_sendkey(hts_code_field, '61091000')
                    logging.info(
                        f'Country is ME/OD. Fill up hts code: 61091000')
                    create_bot_activity_log(ActivityLogSchema(
                        bot='Booking Bot', activity=f'Country is ME/OD. Fill up hts code: 61091000', activity_type='Info', request_id=self.request_id))
                else:
                    # hts_code.send_keys('610910')
                    clear_and_sendkey(hts_code_field, '610910')
                    logging.info(
                        f'Country is not ME/OD. Fill up hts code: 610910')
                    create_bot_activity_log(ActivityLogSchema(
                        bot='Booking Bot', activity=f'Country is not ME/OD. Fill up hts code: 610910', activity_type='Info', request_id=self.request_id))

        # Origin
        origin_field = self.get_element(
            'XPATH', "//input[@id='EditSOForm_soDto_soLineDtoList_0__soLineHtsDtoList_0__country_countryCode']")
        # clear_and_sendkey(origin_field,'BD')
        if origin_field:
            clear_and_sendkey(origin_field, country_of_origin)
            logging.info(
                f'Fill up origin field with country of origin: {country_of_origin}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Fill up origin field with country of origin: {country_of_origin}', activity_type='Info', request_id=self.request_id))
        else:
            logging.info('Country of origin field not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Country of origin field not available', activity_type='Error', request_id=self.request_id))
            return 'Country of origin field not available'

    def handle_hts(self, hts_length):
        # HTS
        hts_code_field = self.get_element(
            'XPATH', "//input[@id='EditSOForm_soDto_soLineDtoList_0__soLineHtsDtoList_0__htsCode']"
        )
        if hts_code_field:
            hts_code = hts_code_field.get_attribute("value")
            # print('hts code',hts_code)
            hts_code = hts_code[:hts_length]
            # hts_code_field.clear()
            # hts_code_field.send_keys(hts_code)
            clear_and_sendkey(hts_code_field, hts_code)
        else:
            add_hts_code = self.get_element(
                'XPATH', "//input[@title='Add new HTSUS line']")
            if add_hts_code:
                add_hts_code.click()
            hts_code_field = self.get_element(
                'XPATH', "//input[@id='EditSOForm_soDto_soLineDtoList_0__soLineHtsDtoList_0__htsCode']")
            if hts_code_field:
                if country_iso == 'ME' or country_iso == 'OD':
                    # hts_code_field.send_keys('61091000')
                    clear_and_sendkey(hts_code_field, '61091000')
                else:
                    # hts_code.send_keys('610910')
                    clear_and_sendkey(hts_code_field, '610910')

    def save_booking(self):
        # Save booking
        save_as = self.get_element('ID', "SaveAsMenuBtnId")
        if save_as:
            save_as.click()
            logging.info('Click on Save As button')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on Save As button', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Save As button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Save As button not available', activity_type='Error', request_id=self.request_id))
            return 'Save As button not available'

        # carefully structure nested quotes with escape sequence
        draft = self.get_element(
            'XPATH', "//a[@onclick=\"saveAsBookingOption('draft')\"]"
        )
        # Save booking as draft
        # draft.click()

        # carefully structure nested quotes with escape sequence
        finished = self.get_element(
            'XPATH', "//a[@onclick=\"saveAsBookingOption('finished')\"]")
        # Save and finish booking
        if finished:
            finished.click()
            logging.info('Click on finished button')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Click on finished button', activity_type='Info', request_id=self.request_id))
        else:
            logging.error('Finished button not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Finished button not available', activity_type='Error', request_id=self.request_id))
            return 'Finished button not available'

        # Wait for the alert
        try:
            wait = WebDriverWait(self.driver, 5)
            alert = wait.until(EC.alert_is_present())
            if alert:
                alert.accept()
                logging.info('Accept alert after clicking finished')
                create_bot_activity_log(ActivityLogSchema(
                    bot='Booking Bot', activity='Accept alert after clicking finished', activity_type='Info', request_id=self.request_id))
                # self.switch_to.default_content()
        except TimeoutException:
            # Handle the case where alert is not found within the timeout
            print("No alert found, proceeding without handling it.")
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='No alert found, proceeding without handling it.', activity_type='Info', request_id=self.request_id))
            # You may want to log this or take further action based on your requirements

    # def final_alert(self):
    #     # Wait for the alert to be present for a maximum of 30 seconds
    #     wait = WebDriverWait(self, 5)
    #     alert = wait.until(EC.alert_is_present())

    #     if alert:
    #         alert = self.switch_to.alert
    #         alert.accept()
    #         self.switch_to.default_content()

    def get_finish_msg(self):

        try:
            finish_msg_element = self.get_element('ID', 'MsgDivId')
            while not finish_msg_element.text:  # Wait until element has text
                time.sleep(1)
                finish_msg_element = self.get_element('ID', 'MsgDivId')
            finish_msg = finish_msg_element.text
            logging.info(f'Extracted Finish msg: {finish_msg}')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity=f'Extracted Finish msg: {finish_msg}', activity_type='Info', request_id=self.request_id))
            return finish_msg
        except:
            logging.info('Finish msg not available')
            create_bot_activity_log(ActivityLogSchema(
                bot='Booking Bot', activity='Finish msg not available', activity_type='Error', request_id=self.request_id))
            return 'Finish msg not available'
