import os
import time

import pandas as pd
from BoschRpaMagicBox.smb_functions import *
from BoschRpaMagicBox.common_functions import *

SE16_TABLE_NAME_INPUT_CSS_SELECTOR = "input[title='Table Name']"
POPUP_WINDOW_OK_BUTTON_CSS_SELECTOR = ".urPWInnerBorder div[title='Continue (Enter)']"
REPORTING_PERIOD_CSS_SELECTOR = "div[title^='Reporting Period:']"
REPORTING_PERIOD_DROPDOWN_CSS_SELECTOR = "input[aria-roledescription='Dropdown List Box'"
REPORTING_PERIOD_DROPDOWN_LIST_CSS_SELECTOR = "#DD_DATESAPLHR_QUERY_APPL_AREA-scrl div.lsListbox__values"
QUERY_PARAMETER_TR_CSS_SELECTOR = "table[id$='mrss-cont-none-content'] tr[id*='mrss-cont-none-Row'][id^='C']"
OUTPUT_BUTTON_CSS_SELECTOR = "div[title='Start output (F8)']"
GET_VARIANT_CSS_SELECTOR = "div[title^='Get Variant']"
GET_VARIANT_EXECUTE_CSS_SELECTOR = ".urPWFooterHeight div[title='Execute (F8)']"
PAYROLL_PERIOD_BUTTON_CSS_SELECTOR = "div[lsdata*='Payroll\\\\x20period']"
LOG_OFF_CSS_SELECTOR = 'div[title="Log Off (Shift+F3)"]'
SAP_QUERY_INPUT_NAME = "SAP Query (S): Query name"
SAP_INFO_SET_INPUT_CSS_SELECTOR = "input[title='SAP Query (S): InfoSet']"
SAP_INFO_SET_SPAN_CSS_SELECTOR = "span[title='SAP Query (S): InfoSet']"
SAP_INFO_SET_ROWS_TR_CSS_SELECTOR = "tr[id^='SHresultgrid'][id*='mrss-cont-none-Row']"
SAP_INFO_SET_ROWS_SPAN_CSS_SELECTOR = "tr[id^='SHresultgrid'][id*='mrss-cont-none-Row'] td:first-child div span"
SAP_INFO_SET_COPY_BUTTON_NAME = "Copy"
FAILED_LOAD_MESSAGE_CSS_SELECTOR = "span.lsMessageBar__text"
INITIALIZE_BUTTON_CSS_SELECTOR = "div[title='Initialize Values (Shift+F1)']"
ORGANIZATION_DATA_CSS_SELECTOR = "div[title^='Organizational data' i]"
ORGANIZATION_SEARCH_CSS_SELECTOR = "span[title='Sales Organization']"
ORGANIZATION_INPUT_CSS_SELECTOR = "input[id^='sh_find']"
ORGANIZATION_HIDDEN_INPUT_CSS_SELECTOR = "input[id^='DDSH']"
ORGANIZATION_RESTRICTION_BUTTON_CSS_SELECTOR = "span[title='Expand content']"
SALES_ORGANIZATION_INPUT_CSS_SELECTOR = "input[title='Sales Organization']"
SAP_LOGO_CSS_SELECTOR = '#messageareaLogoImage'
EXPAND_REPORT_SECTION_ICON_CSS_SELECTOR = "img[src$='s_b_expa.png']"
Y01F_FILE_NAME_INPUT_CSS_SELECTOR = "input[title='File for Report Writer output']"


class MiniRpaSapAutomation:
    def __init__(self, user_name: str, user_password: str, server_name: str, share_name: str, port: int, from_period: str, to_period: str, report_save_path: str,
                 report_process_folder_path: str, report_period_type: str, has_save_folder: bool = True, save_folder_path: str = '', has_proxy: bool = False,
                 proxy_area: str = 'hk', is_private: bool = False, is_headless=False, firefox_binary_location: str = '', geckodriver_binary_location: str = '',
                 timeout=1800, auto_get_screenshot=False, time_interval=5, browser_screenshot_tag=''):
        """

        Args:
            auto_get_screenshot(bool): This is the flag whether to auto get browser screenshots
            time_interval(int): This is the time interval to get screenshot
            browser_screenshot_tag(str): Tag in screenshot name
            is_private(bool): Whether to open a private window
            has_save_folder(bool):This is the flag whether to set save folder path
            save_folder_path(str): This is the folder path of save folder
            has_proxy(bool): This is whether to use proxy when open browser
            proxy_area(str): This is the proxy setting for network.proxy.autoconfig_url
            firefox_binary_location(str): This is the path of firefox.exe
            is_headless(bool): This indicates whether to use headless mode to execute automation task
            timeout(int): This is the timeout setting
            geckodriver_binary_location(str): This is the path of geckodriver.exe
            user_name(str): This is the username
            user_password(str): This is the password
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            port(int): This is the port number of the server name
            from_period(str):This is the start month
            to_period(str): This is the end month
            report_process_folder_path(str): This is the file path for process excel
            report_save_path(str): This is the folder path for original data
            report_period_type(str): This is the report period type. e.g. period, current_date
        """
        self.user_name = user_name
        self.user_password = user_password
        self.server_name = server_name
        self.share_name = share_name
        self.port = port
        self.from_period = from_period
        self.to_period = to_period
        self.report_save_path = report_save_path
        self.browser_screenshot_tag = browser_screenshot_tag
        self.report_process_folder_path = report_process_folder_path
        self.report_period_type = report_period_type
        self.skip_download_process = False
        # self.clear_existed_files_and_screenshots(report_save_path, need_clear)
        self.web_rpa = get_sap_web_gui_functions()
        self.browser, self.wait = self.web_rpa.initial_browser(has_save_folder, save_folder_path, has_proxy, proxy_area, is_private, is_headless, firefox_binary_location,
                                                               geckodriver_binary_location, timeout, auto_get_screenshot, time_interval, browser_screenshot_tag, True, user_name,
                                                               user_password, server_name, share_name, report_save_path)

    def clear_existed_files_and_screenshots(self, report_save_path, exception_str='Common'):
        """ This function is used to clear existed files and screenshots.

        Args:
            report_save_path(str): This is the folder path of save folder
            exception_str(str): This is the string to exclude when file name or folder name contains current string
        """
        smb_traverse_delete_file(self.user_name, self.user_password, self.server_name, self.share_name, report_save_path, exception_str=exception_str)

        # except_str_list = [item.upper().strip() for item in exception_str.replace('，', ',').split(',') if item.strip()]
        # traverse_result_list = smb_traverse_remote_folder(self.user_name, self.user_password, self.server_name, self.share_name, report_save_path)
        # for traverse_item_dict in traverse_result_list:
        #     item_name = traverse_item_dict['name']
        #     item_name_upper = item_name.upper()
        #     if traverse_item_dict['is_folder']:
        #         if not any(keyword in item_name_upper for keyword in except_str_list):
        #             folder_path = os.path.join(report_save_path, item_name)
        #             self.clear_existed_files_and_screenshots(folder_path, exception_str)
        #     else:
        #         if not any(keyword in item_name_upper for keyword in except_str_list):
        #             file_path = os.path.join(report_save_path, item_name)
        #             smb_delete_file(self.user_name, self.user_password, self.server_name, self.share_name, file_path)

    def login_sap(self, sap_system, sap_user, sap_password, need_clear=False, exception_str='Common'):
        """ This function is used to log in SAP system.

        Args:

            sap_system(str): This is the name of SAP system
            sap_user(str): This is the username of SAP system
            sap_password(str): This is the password of SAP system
            need_clear(bool): This is the flag whether to clear existed files and screenshots
            exception_str(str): This is the string to exclude when file name or folder name contains current string
        """
        if need_clear:
            self.clear_existed_files_and_screenshots(self.report_save_path, exception_str)
        self.web_rpa.login_web_sap(sap_system, sap_user, sap_password)

    def input_sap_t_code(self, t_code):
        """ This function is used to input t_code in SAP system.

        Args:

            t_code(str): This is the transaction code of SAP system
        """
        self.web_rpa.input_t_code(t_code)

    def input_se16_table_name(self, table_name):
        """ This function is used to input table name in SE16.

        Args:

            table_name(str): This is the name of table
        """
        sleep(1)
        self.web_rpa.wait_element_presence_by_css_selector(SE16_TABLE_NAME_INPUT_CSS_SELECTOR)
        self.web_rpa.move_to_and_click_element(SE16_TABLE_NAME_INPUT_CSS_SELECTOR)
        self.web_rpa.fill_input_field_with_single_value(table_name, SE16_TABLE_NAME_INPUT_CSS_SELECTOR, is_tab=True)
        sleep(1)
        self.web_rpa.click_or_input_by_css_selector("div.lsRasterLayout", 'click')
        sleep(1)
        self.web_rpa.press_keyboard_shortcut([Keys.ENTER], target_css_selector="div.lsRasterLayout")
        sleep(2)

    def input_sap_query_name(self, query_name):
        """ This function is used to input query name in SE16.

        Args:
            query_name(str): This is the name of query

        """
        self.input_field_single_value(SAP_QUERY_INPUT_NAME, 1, query_name, is_enter=True, is_tab=False, need_click_tip=False)

    def input_field_single_value(self, field_title, field_index, field_value, is_enter, is_tab, need_click_tip):
        """ This function is used to input single field value in SE16.

        Args:
            field_index(int): This is the index of field. e.g. 1,2
            is_enter(bool): This is the flag whether to press enter
            is_tab(bool): This is the flag whether to press tab
            need_click_tip(bool): This is the flag whether to click tip
            field_title(str): This is the title of field
            field_value(str): This is the value of field
        """
        self.web_rpa.wait_element_presence_by_css_selector(f"input[title='{field_title}']")
        target_input_element = self.web_rpa.find_input_element_by_title(field_title, field_index)
        if target_input_element is not None:
            self.web_rpa.move_to_and_click_element('', target_element=target_input_element)
            sleep(1)
            self.web_rpa.fill_input_field_with_single_value(field_value, '', is_enter, is_tab, need_click_tip, '', target_input_element)
            sleep(1)
        else:
            raise ValueError(f'Cannot find field: {field_title} with index: {field_index}')

    def input_field_multiple_values(self, field_button_index, tab_index, field_values, second_field_values):
        """ This function is used to input multiple field values in SE16.

        Args:
            field_button_index(int): This is the index of field button. e.g. 1,2
            tab_index(int): This is the index of tab. e.g. 1,2
            field_values(list): This is the list of values
            second_field_values(list): This is the list of second values
        """
        second_field_values = [field_value for field_value in second_field_values if str(field_value).strip()]
        if second_field_values and tab_index in [2, 4]:
            temp_field_values = []
            for field_index, field_value in enumerate(field_values):
                try:
                    temp_field_values.append(f"{field_value}\t{second_field_values[field_index]}")
                except IndexError:
                    temp_field_values.append(f"{field_value}\t ")
            field_values = temp_field_values

        self.web_rpa.input_multiple_selection_with_index(field_values, field_button_index, tab_index, clear_section_data=True)

    def input_query_field_multiple_values(self, field_button_index, tab_index, field_values, second_field_values):
        """ This function is used to input multiple field values in SE16.

        Args:
            field_button_index(int): This is the index of field button. e.g. 1,2
            tab_index(int): This is the index of tab. e.g. 1,2
            field_values(list): This is the list of values
            second_field_values(list): This is the list of second values
        """
        second_field_values = [field_value for field_value in second_field_values if str(field_value).strip()]
        if second_field_values and tab_index in [2, 4]:
            temp_field_values = []
            for field_index, field_value in enumerate(field_values):
                try:
                    temp_field_values.append(f"{field_value}\t{second_field_values[field_index]}")
                except IndexError:
                    temp_field_values.append(f"{field_value}\t ")
            field_values = temp_field_values

        self.web_rpa.input_query_multiple_selection_with_index(field_values, field_button_index, tab_index, clear_section_data=True)

    def click_radio_checkbox(self, radio_checkbox_title):
        """ This function is used to click radio or checkbox in SE16.

        Args:
            radio_checkbox_title(str): This is the title of radio or checkbox
        """
        wait_time = 60
        while wait_time > 0:
            try:
                self.web_rpa.browser.find_element(By.CSS_SELECTOR, f"span[title='{radio_checkbox_title}']")
                self.web_rpa.click_or_input_by_css_selector(f"span[title='{radio_checkbox_title}']", 'click')
                return
            except NoSuchElementException:
                try:
                    self.web_rpa.browser.find_element(By.CSS_SELECTOR, f"span[aria-label='{radio_checkbox_title}']")
                    self.web_rpa.click_or_input_by_css_selector(f"span[aria-label='{radio_checkbox_title}']", 'click')
                    return
                except NoSuchElementException:
                    sleep(1)
                    wait_time -= 1
        raise Exception(f"Cannot find radio or checkbox with title: {radio_checkbox_title}")

        # try:
        #     self.web_rpa.click_or_input_by_css_selector(f"span[title='{radio_checkbox_title}']", 'click')
        # except:
        #     self.web_rpa.click_or_input_by_css_selector(f"span[aria-label='{radio_checkbox_title}']", 'click')

    def click_radio_checkbox_by_mouse(self, radio_checkbox_title):
        """ This function is used to click radio or checkbox in SE16.

        Args:
            radio_checkbox_title(str): This is the title of radio or checkbox
        """
        wait_time = 60
        while wait_time > 0:
            try:
                self.web_rpa.browser.find_element(By.CSS_SELECTOR, f"span[title='{radio_checkbox_title}']")
                self.web_rpa.move_to_and_click_element(f"span[title='{radio_checkbox_title}']")
                return
            except NoSuchElementException:
                try:
                    self.web_rpa.browser.find_element(By.CSS_SELECTOR, f"span[aria-label='{radio_checkbox_title}']")
                    self.web_rpa.move_to_and_click_element(f"span[aria-label='{radio_checkbox_title}']")
                    return
                except NoSuchElementException:
                    sleep(1)
                    wait_time -= 1
        raise Exception(f"Cannot find radio or checkbox with title: {radio_checkbox_title}")

    def click_button(self, button_title):
        """ This function is used to click button

        Args:
            button_title(str): This is the title of button
        """
        self.web_rpa.click_or_input_by_css_selector(f"div[title='{button_title}']", 'click')
        sleep(1)

    def click_button_by_mouse(self, button_title):
        """ This function is used to click button by mouse.

        Args:
            button_title(str): This is the title of button
        """
        self.web_rpa.move_to_and_click_element(f"div[title='{button_title}']")
        sleep(1)

    def click_execute_button(self):
        """ This function is used to click execute button in SE16.
        """
        self.web_rpa.click_execute_button()
        sleep(3)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)

    def click_output_button(self):
        """ This function is used to click output button.
        """
        self.web_rpa.press_keyboard_shortcut([Keys.F8])
        # self.web_rpa.move_to_and_click_element(OUTPUT_BUTTON_CSS_SELECTOR)
        sleep(3)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)

    def check_data_load_status(self, failed_load_message):
        """ This function is used to check data load status.

        Args:
            failed_load_message(str): This is the message of failed
        """
        sleep(2)
        self.web_rpa.wait_invisibility_of_loading_window()
        try:
            message_element = self.web_rpa.browser.find_element(By.CSS_SELECTOR, FAILED_LOAD_MESSAGE_CSS_SELECTOR)
            if message_element.text == failed_load_message:
                self.skip_download_process = True
                print(f'Failed to load data: {failed_load_message}')
                self.back_to_home_page()
            else:
                print(f'Current message is: {message_element.text}')
        except:
            print('Data loaded successfully!')

    def select_layout_before_download_excel(self, layout_name: str, shortcut_list: list):
        """ This function is used to select layout before downloading excel.

        Args:
            layout_name(str): This is the name of layout
            shortcut_list(list): This is the list of shortcuts
        """
        self.web_rpa.wait_invisibility_of_loading_window()
        self.web_rpa.select_sap_layout(layout_name, shortcut_list)
        sleep(1)

    def select_se16_layout_before_download_excel(self, layout_name: str, shortcut_list: list):
        """ This function is used to select layout before downloading excel.

        Args:
            layout_name(str): This is the name of layout
            shortcut_list(list): This is the list of shortcuts
        """
        self.web_rpa.wait_invisibility_of_loading_window()
        self.web_rpa.select_sap_se16_layout(layout_name, shortcut_list)
        sleep(1)

    def context_click_in_table(self, column_name, context_menu_item_name):
        """ This function is used to context click in table.

        Args:
            column_name(str): This is the name of column
            context_menu_item_name(str): This is the name of context menu item
        """
        div_column_css_selector = f"div[title='{column_name}']"
        span_column_css_selector = f"span[title='{column_name}']"

        # column_css_selector = ''
        while True:
            try:
                print(f'try to find {div_column_css_selector}')
                self.web_rpa.browser.find_element(By.CSS_SELECTOR, div_column_css_selector)
                column_css_selector = div_column_css_selector
                break
            except NoSuchElementException:
                try:
                    print(f'try to find {span_column_css_selector}')
                    self.web_rpa.browser.find_element(By.CSS_SELECTOR, span_column_css_selector)
                    column_css_selector = span_column_css_selector
                    break
                except NoSuchElementException:
                    sleep(1)
                    pass

        self.web_rpa.activate_context_click(column_css_selector)
        sleep(2)
        self.web_rpa.click_or_input_by_css_selector(f"tr[aria-label^='{context_menu_item_name}']", 'click')
        # self.web_rpa.move_to_and_click_element(f"tr[aria-label^='{context_menu_item_name}']")
        sleep(1)

    def download_excel_by_context_click(self, column_name, context_menu_item_name, file_name):
        """ This function is used to download excel by context click.

        Args:
            column_name(str): This is the name of column
            context_menu_item_name(str): This is the name of context menu item
            file_name(str): This is the name of file
        """
        self.web_rpa.wait_invisibility_of_loading_window()
        self.context_click_in_table(column_name, context_menu_item_name)
        sleep(1)
        is_cancelled = self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)
        if is_cancelled:
            self.web_rpa.wait_invisibility_of_loading_window()
            self.context_click_in_table(column_name, context_menu_item_name)
            sleep(1)
            self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)

    def download_excel_by_menu_click(self, file_name):
        """ This function is used to download excel by menu click.

        Args:
            file_name(str): This is the name of file
        """
        sleep(2)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)
        self.web_rpa.activate_context_click('#cuaheader-title')
        self.web_rpa.click_or_input_by_css_selector("tr[aria-label^='Print Preview']", 'click')
        sleep(5)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)
        self.web_rpa.activate_context_click('#cuaheader-title')
        self.web_rpa.click_or_input_by_css_selector("tr[aria-label^='Spreadsheet...']", 'click')
        sleep(1)
        is_cancelled = self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)
        if is_cancelled:
            self.web_rpa.wait_invisibility_of_loading_window()
            self.web_rpa.activate_context_click('#cuaheader-title')
            self.web_rpa.click_or_input_by_css_selector("tr[aria-label^='Spreadsheet...']", 'click')
            sleep(1)
            self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)

    def download_excel_by_views_button_click(self, file_name):
        """ This function is used to download Excel by views button click.

        Args:
            file_name(str): This is the name of file
        """
        sleep(2)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)
        self.web_rpa.click_or_input_by_css_selector("div[title='Views']", 'click')
        sleep(2)
        self.web_rpa.click_or_input_by_css_selector("tr[aria-label='List Output']", 'click')
        sleep(4)
        self.web_rpa.wait_invisibility_of_loading_window()
        self.web_rpa.wait_element_invisible_by_css_selector("div[title='Views']")
        sleep(1)
        self.web_rpa.activate_context_click('#cuaheader-title')
        self.web_rpa.click_or_input_by_css_selector("tr[aria-label^='Spreadsheet...']", 'click')
        sleep(1)
        is_cancelled = self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)
        if is_cancelled:
            self.web_rpa.wait_invisibility_of_loading_window()
            self.web_rpa.activate_context_click('#cuaheader-title')
            self.web_rpa.click_or_input_by_css_selector("tr[aria-label^='Spreadsheet...']", 'click')
            sleep(1)
            self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)

    def download_excel_by_export_button_click(self, file_name):
        """ This function is used to download Excel by export click.

        Args:
            file_name(str): This is the name of file
        """
        sleep(2)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)
        self.web_rpa.click_or_input_by_css_selector("div[title='Export']", 'click')
        sleep(2)
        self.web_rpa.move_to_and_click_element("tr[aria-label='Spreadsheet']")
        sleep(2)
        self.web_rpa.wait_invisibility_of_loading_window()
        is_cancelled = self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)
        if is_cancelled:
            self.web_rpa.click_or_input_by_css_selector("div[title='Export']", 'click')
            sleep(2)
            self.web_rpa.move_to_and_click_element("tr[aria-label='Spreadsheet']")
            sleep(2)
            self.web_rpa.wait_invisibility_of_loading_window()
            sleep(1)
            self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)

    def download_excel_by_click_spreadsheet_button(self, spreadsheet_title, file_name):
        """ This function is used to download excel by clicking spreadsheet button.

        Args:
            file_name(str): This is the name of file
            spreadsheet_title(str): This is the title of spreadsheet
        """
        self.web_rpa.wait_invisibility_of_loading_window()
        self.web_rpa.click_or_input_by_css_selector(f"div[title='{spreadsheet_title}']", 'click')
        sleep(1)
        is_cancelled = self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)
        sleep(1)
        if is_cancelled:
            self.web_rpa.wait_invisibility_of_loading_window()
            self.web_rpa.click_or_input_by_css_selector(f"div[title='{spreadsheet_title}']", 'click')
            sleep(1)
            self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name,
                                                        self.report_save_path)

    def download_excel_by_click_print_preview(self, print_preview_title, spreadsheet_title, file_name):
        """ This function is used to download excel by clicking print preview.

        Args:
            print_preview_title(str): This is the title of print preview
            spreadsheet_title(str): This is the title of spreadsheet
            file_name(str): This is the name of file
        """
        self.web_rpa.wait_invisibility_of_loading_window()
        self.web_rpa.click_or_input_by_css_selector(f"div[title='{print_preview_title}']", 'click')
        sleep(1)
        self.download_excel_by_click_spreadsheet_button(spreadsheet_title, file_name)

    def download_excel_by_press_short_keys(self, shortcut_list, file_name):
        """ This function is used to download excel by pressing short keys.

        Args:
            file_name(str): This is the name of file
            shortcut_list(list): This is the list of short keys
        """
        self.web_rpa.wait_invisibility_of_loading_window()
        self.web_rpa.press_keyboard_shortcut(shortcut_list)
        sleep(1)
        is_cancelled = self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)
        sleep(1)
        if is_cancelled:
            self.web_rpa.wait_invisibility_of_loading_window()
            self.web_rpa.press_keyboard_shortcut(shortcut_list)
            sleep(1)
            self.web_rpa.input_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)

    def download_y01k_report_data(self, file_name, shortcut_list):
        """ This function is used to download Y01K data.

        Args:
            file_name(str): This is the name of file
            shortcut_list(list): This is the list of shortcuts
        """
        sleep(1)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)
        self.web_rpa.press_keyboard_shortcut(shortcut_list)
        sleep(5)

        skip_download_process = False
        self.web_rpa.wait_element_presence_by_css_selector(SAP_LOGO_CSS_SELECTOR)
        message_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "div[id$='contentdiv'][id^='userarealist'] div:first-child")
        if message_elements:
            for message_element in message_elements:
                if 'Report contains no data' in message_element.text.strip():
                    skip_download_process = True
                    print(f'No data found: {file_name}')
                    sleep(3)
                    break

        if not skip_download_process:
            sleep(1)
            self.web_rpa.input_y01f_download_excel_file_name(file_name, True, self.user_name, self.user_password, self.server_name, self.share_name, self.report_save_path)

    def save_screenshot(self, screenshot_folder_path, screenshot_file_name_tag='sap_screenshot', name_format='time'):
        """ This function is used to save screenshot.

        Args:
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
        """
        local_save_folder_path = self.report_save_path + os.sep + "Screenshot"
        if not os.path.exists(local_save_folder_path):
            os.mkdir(local_save_folder_path)

        screenshot_file_name, screenshot_file_path = self.web_rpa.get_screenshot(local_save_folder_path, screenshot_file_name_tag, name_format)
        remote_screenshot_file_path = os.path.join(screenshot_folder_path, screenshot_file_name)
        smb_copy_file_local_to_remote(self.user_name, self.user_password, self.server_name, self.share_name, screenshot_file_path, remote_screenshot_file_path, self.port)

    def check_button_popup_and_click(self, button_title, try_times=5):
        """ This function is used to check element exist and click.

        Args:
            button_title(str): This is the css selector of button
            try_times(int): This is the times to try
        """
        self.web_rpa.wait_invisibility_of_loading_window()
        button_css_selector = f"div[title='{button_title}']"
        try_time = 1
        while try_time <= try_times:
            print(f'try_time: {try_time}')
            try:
                print(f'try to find {button_css_selector}')
                self.web_rpa.browser.find_element(By.CSS_SELECTOR, button_css_selector)
            except NoSuchElementException:
                sleep(1)
                try_time += 1
            else:
                self.web_rpa.click_or_input_by_css_selector(button_css_selector, 'click')
                sleep(2)
                break

    def press_keyboard_shortcut(self, shortcut_list):
        """ This function is used to press shortcut.

        Args:
            shortcut_list(list): This is the list of shortcuts
        """
        self.web_rpa.press_keyboard_shortcut(shortcut_list)

    def input_reporting_period(self, reporting_period_name, reporting_start_date, reporting_end_date):
        """ This function is used to input reporting period.

        Args:
            reporting_period_name(str): This is the name of reporting period
            reporting_start_date(str): This is the start date
            reporting_end_date(str): This is the end date
        """
        self.web_rpa.click_or_input_by_css_selector(REPORTING_PERIOD_CSS_SELECTOR, 'click')
        sleep(1)
        self.web_rpa.wait_element_presence_by_css_selector(REPORTING_PERIOD_DROPDOWN_CSS_SELECTOR)
        self.web_rpa.click_or_input_by_css_selector(REPORTING_PERIOD_DROPDOWN_CSS_SELECTOR, 'click')
        sleep(1)
        self.web_rpa.wait_element_presence_by_css_selector(REPORTING_PERIOD_DROPDOWN_LIST_CSS_SELECTOR)

        self.web_rpa.click_or_input_by_css_selector(f"div[data-itemvalue2='{reporting_period_name}'", 'click')

        if reporting_period_name in ['Key Date', 'Other Period'] and reporting_start_date:
            self.input_field_single_value('Start Date', 1, reporting_start_date, is_enter=True, is_tab=False, need_click_tip=False)
            sleep(1)

        if reporting_period_name in ['Other Period'] and reporting_end_date:
            self.input_field_single_value('End Date', 1, reporting_end_date, is_enter=True, is_tab=False, need_click_tip=False)
            sleep(1)

    def input_query_values_from_existed_data(self, query_button_index, query_value_input_method='local_file', remote_folder_path='', query_value_columns=None, file_name='',
                                             sheet_name='Sheet1', tab_index=1, has_range=False, start_range=None, end_range=None):
        """ This function is used to input query values.

        Args:
            query_button_index(int): This is the index of query button
            query_value_input_method(str): This is the method to input query values. remote_file or local_file
            remote_folder_path(str): This is the path of remote folder
            query_value_columns(list): This is the list of query columns
            file_name(str): This is the path of file
            sheet_name(str): This is the name of sheet
            tab_index(int): This is the index of tab
            has_range(bool): This indicates whether to has range
            start_range(int): This is the start range of data
            end_range(int): This is the end range of data
        """
        if query_value_columns is None:
            query_value_columns = []

        is_file_exist, file_data = self.load_downloaded_excel_file(query_value_input_method, file_name, sheet_name, remote_folder_path)
        if is_file_exist:
            if has_range and not file_data.empty:
                start_range = abs(int(start_range)) - 1 if start_range else 0
                end_range = abs(int(end_range)) if end_range else file_data.shape[0]

                start_range = 0 if start_range < 0 else start_range
                end_range = file_data.shape[0] if end_range > file_data.shape[0] else end_range

                if start_range > end_range:
                    start_range, end_range = end_range, start_range

                file_data = file_data.iloc[start_range:end_range, :]
                if file_data.empty:
                    print(f'No data found in the range: {start_range} - {end_range}')
                    self.skip_download_process = True
                    self.back_to_home_page()

            if len(query_value_columns) == 2:
                file_data['paste_column'] = file_data[query_value_columns[0]] + '\t' + file_data[query_value_columns[1]]
                query_value_list = file_data['paste_column'].tolist()
            elif len(query_value_columns) == 1:
                query_value_list = file_data[query_value_columns[0]].tolist()
            else:
                raise ValueError('The query_value_columns should be correct values!')
            self.web_rpa.input_multiple_selection_with_index(query_value_list, query_button_index, tab_index, clear_section_data=True)
            sleep(2)
        else:
            self.skip_download_process = True
            self.back_to_home_page()

    def load_downloaded_excel_file(self, query_value_input_method, file_name, sheet_name='Sheet1', remote_folder_path=''):
        """ This function is used to load downloaded Excel file.

        Args:
            file_name(str): This is the name of file
            sheet_name(str): This is the name of sheet
            query_value_input_method(str): This is the method to input query values. remote_file or local_file
            remote_folder_path(str): This is the path of remote folder
        """
        file_data = pd.DataFrame()
        is_file_exist = True

        try:
            if query_value_input_method == 'local_file':
                file_path = self.web_rpa.save_folder_path + os.sep + file_name
                if os.path.exists(file_path):
                    file_data = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
                else:
                    is_file_exist = False
                    print(f'Cannot load file: {file_name} from local folder: {self.web_rpa.save_folder_path}')

            elif query_value_input_method == 'remote_file':
                if not remote_folder_path:
                    remote_folder_path = self.report_save_path
                full_remote_file_path = os.path.join(remote_folder_path, file_name)
                # full_remote_file_path = os.path.join(remote_folder_path, remote_file_path)
                is_file_exist, file_obj = smb_check_file_exist(self.user_name, self.user_password, self.server_name, self.share_name, full_remote_file_path)
                if is_file_exist:
                    file_data = pd.read_excel(file_obj, sheet_name=sheet_name, dtype=str)
                else:
                    print(f'Cannot load file: {file_name} from remote folder: {remote_folder_path}')
            else:
                print('The query_value_input_method should be remote_file or local_file!')
        except:
            print(f'Cannot load file: {file_name} from remote folder: {remote_folder_path}')

        return is_file_exist, file_data

    def find_variant_by_name(self, variant_name):
        """ This function is used to find variant by name.

        Args:
            variant_name(str): This is the name of variant
        """
        self.web_rpa.click_or_input_by_css_selector(GET_VARIANT_CSS_SELECTOR, 'click')
        sleep(4)
        try:
            self.web_rpa.browser.find_element(By.CSS_SELECTOR, INITIALIZE_BUTTON_CSS_SELECTOR)
            self.web_rpa.click_or_input_by_css_selector(INITIALIZE_BUTTON_CSS_SELECTOR, 'click')
        except:
            self.web_rpa.input_variant_multiple_selection_with_index([], 3, 1, clear_section_data=True)
        sleep(2)
        self.web_rpa.input_variant_multiple_selection_with_index([variant_name], 1, 1, clear_section_data=True)
        sleep(2)
        self.web_rpa.click_or_input_by_css_selector(GET_VARIANT_EXECUTE_CSS_SELECTOR, 'click')
        sleep(1)
        self.web_rpa.wait_element_invisible_by_css_selector(GET_VARIANT_EXECUTE_CSS_SELECTOR)

    def find_abap_variant_by_name(self, variant_name):
        """ This function is used to find ABAP variant by name.

        Args:
            variant_name(str): This is the name of ABAP variant
        """
        self.web_rpa.select_abap_variant_name(variant_name)

    def find_organization_data_by_company_code(self, company_code):
        """ This function is used to find variant by name.

        Args:
            company_code(str): This is the company code
        """

        self.web_rpa.click_or_input_by_css_selector(ORGANIZATION_DATA_CSS_SELECTOR, 'click')
        sleep(2)
        self.web_rpa.wait_element_presence_by_css_selector(SALES_ORGANIZATION_INPUT_CSS_SELECTOR)
        # self.web_rpa.click_or_input_by_css_selector(ORGANIZATION_SEARCH_CSS_SELECTOR, 'click')
        self.web_rpa.press_keyboard_shortcut([Keys.F4])
        sleep(2)
        self.web_rpa.wait_element_presence_by_css_selector(ORGANIZATION_INPUT_CSS_SELECTOR)
        self.web_rpa.click_or_input_by_css_selector(ORGANIZATION_RESTRICTION_BUTTON_CSS_SELECTOR, 'click')
        sleep(2)
        input_element = self.web_rpa.browser.find_element(By.CSS_SELECTOR, ORGANIZATION_HIDDEN_INPUT_CSS_SELECTOR)
        self.web_rpa.move_to_and_click_element('', target_element=input_element)
        self.web_rpa.fill_input_field_with_single_value(company_code, '', True, False, False, '', input_element)
        sleep(2)
        self.click_button('Copy')
        sleep(2)
        self.web_rpa.wait_element_invisible_by_css_selector(ORGANIZATION_INPUT_CSS_SELECTOR)
        self.click_button('Continue (Enter)')
        sleep(2)
        self.web_rpa.wait_element_invisible_by_css_selector(SALES_ORGANIZATION_INPUT_CSS_SELECTOR)

    def click_payroll_button(self):
        """ This function is used to click payroll button
        """
        self.web_rpa.click_or_input_by_css_selector(PAYROLL_PERIOD_BUTTON_CSS_SELECTOR, 'click')
        sleep(2)

    def input_sap_info_set(self, info_set_name):
        """ This function is used to input info set name
        """
        sleep(2)
        self.web_rpa.wait_element_presence_by_css_selector(SAP_INFO_SET_INPUT_CSS_SELECTOR)
        self.web_rpa.move_to_and_click_element(SAP_INFO_SET_INPUT_CSS_SELECTOR)
        sleep(1)
        self.web_rpa.press_keyboard_shortcut([Keys.F4])
        sleep(2)
        self.web_rpa.click_element_by_key_word(SAP_INFO_SET_ROWS_TR_CSS_SELECTOR, SAP_INFO_SET_ROWS_SPAN_CSS_SELECTOR, info_set_name, click_type='double', click_method='element')
        sleep(2)
        self.click_button(SAP_INFO_SET_COPY_BUTTON_NAME)
        sleep(2)
        self.web_rpa.wait_element_invisible_by_css_selector(SAP_INFO_SET_ROWS_TR_CSS_SELECTOR)
        sleep(1)

    def back_to_home_page(self):
        """ This function is used to back to home page
        """
        sleep(2)
        try:
            self.web_rpa.browser.find_element(By.CSS_SELECTOR, LOG_OFF_CSS_SELECTOR)
        except:
            self.input_sap_t_code('/n')
            sleep(2)
            self.web_rpa.wait_element_presence_by_css_selector(LOG_OFF_CSS_SELECTOR)
            self.web_rpa.wait_invisibility_of_loading_window()
            sleep(1)
        else:
            pass

    def close_browser(self):
        """ This function is used to close browser.
        """
        self.web_rpa.quit_browser()

    def wait_invisibility_of_loading_window(self):
        """ This function is used to wait invisibility of loading window.
        """
        sleep(5)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(2)

    def expand_report_fully(self, shortcut_list, timeout=600):
        """This function is used to expand a report fully.

        Args:
            shortcut_list (list): Keyboard shortcut list
            timeout (int): Max wait time in seconds
        """
        sleep(1)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)
        self.web_rpa.press_keyboard_shortcut(shortcut_list)
        sleep(2)

        start_time = time.time()
        while True:
            print('Wait report to expand fully!')
            expand_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, EXPAND_REPORT_SECTION_ICON_CSS_SELECTOR)
            if not expand_elements:
                break
            if time.time() - start_time > timeout:
                raise TimeoutError("Report expansion took too long.")
            sleep(2)

    def select_y01k_report_left_menu_item(self, report_name):
        """ This function is used to select report left menu item.

        Args:
            report_name(str): This is the name of report left menu item
        """
        sleep(1)
        self.web_rpa.wait_invisibility_of_loading_window()
        sleep(1)
        self.web_rpa.wait_element_presence_by_css_selector("span[id^='tree'][role='button']")
        report_menu_items = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "span[id^='tree'][role='button']")
        for report_menu_item in report_menu_items:
            if report_name == report_menu_item.text.strip():
                self.web_rpa.move_to_and_click_element('', target_element=report_menu_item)
                sleep(3)
                self.web_rpa.wait_element_presence_by_css_selector(SAP_LOGO_CSS_SELECTOR)
                message_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "div[id$='contentdiv'][id^='userarealist'] div:first-child")
                if message_elements:
                    for message_element in message_elements:
                        if 'Report contains no data' in message_element.text.strip():
                            self.skip_download_process = True
                            print(f'No data found: {report_name}')
                            sleep(3)
                            break
                break
        else:
            raise ValueError(f'Cannot find report menu item: {report_name}')

    def drag_and_drop_y01k_split_element(self, split_element_order, y_offset):
        """ This function is used to drag and drop element.

        Args:
            split_element_order(int): This is the order of split element
            y_offset(int): This is the y offset of target element
        """
        split_element_order = int(split_element_order)
        y_offset = int(y_offset)
        y01k_split_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "td[title^='Resize split screen between horizontal pane']")
        for split_element_index, split_element in enumerate(y01k_split_elements):
            if split_element_index + 1 == split_element_order:
                self.web_rpa.drag_by_offset(split_element, 0, y_offset)
                sleep(3)
                break

    def input_sm35_session_name(self, input_index, session_name):
        """ This function is used to input SM35 session name.

        Args:
            input_index(int): This is the index of input field
            session_name(str): This is the name of session
        """
        input_index = int(input_index)
        sleep(1)
        self.web_rpa.wait_element_presence_by_css_selector(EXECUTION_BUTTON_CSS_SELECTOR)
        sleep(1)
        input_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "input.lsField__input[role='textbox']")
        for input_element_index, input_element in enumerate(input_elements):
            if input_element_index + 1 == input_index:
                self.web_rpa.move_to_and_click_element('', target_element=input_element)
                sleep(1)
                self.web_rpa.fill_input_field_with_single_value(session_name, '', True, False, False, '', input_element)
                sleep(1)
                break

    def click_importing_file_help_button(self, input_index):
        """ This function is used to click importing file help button.

        Args:
            input_index(int): This is the index of input field
        """
        input_index = int(input_index)
        input_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "input.lsField__input[role='textbox']")
        for input_element_index, input_element in enumerate(input_elements):
            if input_element_index + 1 == input_index:
                self.web_rpa.move_to_and_click_element('', target_element=input_element)
                sleep(1)
                self.web_rpa.wait_element_presence_by_css_selector('#ls-inputfieldhelpbutton')
                self.web_rpa.click_or_input_by_css_selector("#ls-inputfieldhelpbutton", 'click')
                sleep(3)
                try_times = 1
                while try_times <= 3:
                    try:
                        self.web_rpa.browser.find_element(By.CSS_SELECTOR, '#UpDownDialogChoose')
                    except:
                        sleep(1)
                        try_times += 1
                    else:
                        self.web_rpa.move_to_and_click_element('#UpDownDialogChoose')
                        break
                break

    def upload_file(self, upload_folder_path, upload_file_name, window_name='File Upload'):
        """ This function is used to upload file.

        Args:
            upload_folder_path(str): This is the path of upload folder
            upload_file_name(str): This is the name of upload file
            window_name(str): This is the name of window
        """
        remote_file_path = upload_folder_path + os.sep + upload_file_name
        local_file_path = self.web_rpa.save_folder_path + os.sep + upload_file_name

        smb_copy_file_remote_to_local(self.user_name, self.user_password, self.server_name, self.share_name, local_file_path, remote_file_path, self.port)
        screenshot_path_list = self.web_rpa.upload_files_in_popup_window(local_file_path, window_name, True)
        sleep(2)
        self.wait_importing_file_dialog_invisibility()
        sleep(1)

        remote_screenshot_folder_path = self.report_save_path + os.sep + 'Screenshots'
        is_folder_exist = smb_check_folder_exist(self.user_name, self.user_password, self.server_name, self.share_name, remote_screenshot_folder_path, self.port)
        if not is_folder_exist:
            smb_create_folder(self.user_name, self.user_password, self.server_name, self.share_name, remote_screenshot_folder_path)

        if self.browser_screenshot_tag:
            remote_screenshot_folder_path = remote_screenshot_folder_path + os.sep + self.browser_screenshot_tag
            is_folder_exist = smb_check_folder_exist(self.user_name, self.user_password, self.server_name, self.share_name, remote_screenshot_folder_path)
            if not is_folder_exist:
                smb_create_folder(self.user_name, self.user_password, self.server_name, self.share_name, remote_screenshot_folder_path)

        for screenshot_path in screenshot_path_list:
            remote_file_path = remote_screenshot_folder_path + os.sep + screenshot_path.split(os.sep)[-1]
            smb_copy_file_local_to_remote(self.user_name, self.user_password, self.server_name, self.share_name, screenshot_path, remote_file_path, self.port)

    def wait_importing_file_dialog_invisibility(self):
        """ This function is used to wait importing file dialog invisibility.
        """
        self.web_rpa.wait_element_invisible_by_css_selector('#UpDownDialogChoose')

    def process_sm35_session(self, session_name, session_created_by):
        """ This function is used to process SM35 session.

        Args:
            session_name(str): This is the name of session.
            session_created_by(str): This is the name of user who created the session.
        """
        self.input_field_single_value('Name of batch input session', 1, session_name, is_enter=True, is_tab=False, need_click_tip=False)
        self.input_field_single_value('Queue user ID / for historical reasons', 1, session_created_by, is_enter=True, is_tab=False, need_click_tip=False)
        sleep(2)
        status_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "table[id$='mrss-cont-none-content'] tbody tr")
        if status_elements:
            first_status_element = status_elements[0]
            try:
                # New / Errors / Processed
                session_new_element = first_status_element.find_element(By.CSS_SELECTOR, "span[title='New']")
            except NoSuchElementException:
                print(f'No new session found for {session_name} {session_created_by}!')
            else:
                tr_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "table[id$='mrss-cont-left-content'] tbody tr")
                first_tr_element = tr_elements[0]
                first_td = first_tr_element.find_element(By.CSS_SELECTOR, " td:first-child")
                self.web_rpa.move_to_and_click_element('', target_element=first_td)
                sleep(2)
                self.click_button('Process session (F8)')
                self.web_rpa.wait_element_presence_by_css_selector("span[title='Batch input, process in batch mode'][role='radio']")
                sleep(1)
                self.web_rpa.move_to_and_click_element("span[title='Batch input, process in batch mode'][role='radio']")
                sleep(1)
                self.click_button('Process (Enter)')
                sleep(1)
                self.web_rpa.wait_element_invisible_by_css_selector("span[title='Batch input, process in batch mode'][role='radio']")

    def check_sm35_session_status(self, session_name, session_created_by):
        """ This function is used to check SM35 session status.

        Args:
            session_name(str): This is the name of session.
            session_created_by(str): This is the name of user who created the session.
        """
        has_search_result = False
        self.input_field_single_value('Name of batch input session', 1, session_name, is_enter=True, is_tab=False, need_click_tip=False)
        self.input_field_single_value('Queue user ID / for historical reasons', 1, session_created_by, is_enter=True, is_tab=False, need_click_tip=False)
        sleep(2)
        tr_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "table[id$='mrss-cont-left-content'] tbody tr")
        if tr_elements:
            first_tr_element = tr_elements[0]
            try:
                session_name_element = first_tr_element.find_element(By.CSS_SELECTOR, "span[role='textbox']")
            except NoSuchElementException:
                pass
            else:
                if session_name_element.text.strip().upper() == session_name.upper():
                    has_search_result = True

        if has_search_result:
            try_times = 1
            while try_times <= 100:
                print('Checking SM35 session status, current try times: ', try_times)
                self.input_field_single_value('Name of batch input session', 1, session_name, is_enter=True, is_tab=False, need_click_tip=False)
                sleep(2)
                status_elements = self.web_rpa.browser.find_elements(By.CSS_SELECTOR, "table[id$='mrss-cont-none-content'] tbody tr")
                if status_elements:
                    first_status_element = status_elements[0]
                    try:
                        # Errors / Processed
                        session_error_element = first_status_element.find_element(By.CSS_SELECTOR, "span[title='Errors']")
                    except NoSuchElementException:
                        try:
                            session_processed_element = first_status_element.find_element(By.CSS_SELECTOR, "span[title='Processed']")
                        except NoSuchElementException:
                            sleep(1)
                            try_times += 1
                        else:
                            print(f'Session for {session_name} {session_created_by} has been processed without errors!')
                            break
                    else:
                        print(f'Session for {session_name} {session_created_by} has been processed with errors!')
                        break
                else:
                    print(f'No session found for {session_name} {session_created_by}!')
                    break
        else:
            print(f'No SM35 session found for {session_name} {session_created_by}!')

    def wait_in_seconds(self, wait_seconds):
        """ This function is used to wait for a specific number of seconds.

        Args:
            wait_seconds(int): The number of seconds to wait.
        """
        sleep(wait_seconds)
        self.web_rpa.wait_invisibility_of_loading_window()
