import os
import datetime
import re
import subprocess
from time import sleep
from typing import Tuple
import functools
import pyperclip
import tempfile
from threading import Thread
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, \
    MoveTargetOutOfBoundsException, InvalidSessionIdException, TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service

from .common_config import *
from .smb_functions import *


# from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


def get_sap_web_gui_functions():
    """This function is used to initial WebSapCommonFunctions

    """
    return WebSapCommonFunctions()


class WebSapCommonFunctions:
    """This class is used to design web sap common functions across different t-codes

    """

    def __init__(self):
        """This function is used to initial basic parameters

        """
        self.sap_system = 'poe'
        self.save_folder_path = ''
        self.stop_screenshot_thread = True
        self.thr = None
        self.time_interval = 15

    def handle_selenium_exceptions(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                self.stop_auto_get_browser_screenshots()
                raise

        return wrapper

    def apply_decorator_to_methods(self):
        for attr in dir(self):
            if callable(getattr(self, attr)) and not attr.startswith("__"):
                original_method = getattr(self, attr)
                decorated_method = self.handle_selenium_exceptions(original_method)
                setattr(self, attr, decorated_method)

    @staticmethod
    def clear_save_folder(save_folder_path: str):
        """This function is used to clear save folder

        Args:
            save_folder_path (str): This is the folder path to save downloaded files
        """
        if os.path.exists(save_folder_path):
            for file_name in os.listdir(save_folder_path):
                os.remove(save_folder_path + os.sep + file_name)

    @staticmethod
    def check_file_download_status(save_folder_path: str, file_name: str):
        """This function is used to check whether file has been downloaded successfully

        Args:
            file_name(str): This is the file name of file that will be saved in save folder
            save_folder_path(str): This is the folder path of save folder
        """
        save_file_path = save_folder_path + os.sep + file_name
        sleep(4)
        is_loop = True
        while is_loop:
            for current_file_name in os.listdir(save_folder_path):
                current_save_file_path = save_folder_path + os.sep + current_file_name
                if os.path.getsize(current_save_file_path) != 0 and file_name.upper().strip() in current_file_name.upper().strip():
                    try:
                        os.rename(save_folder_path + os.sep + current_file_name, save_file_path)
                    except:
                        pass
                    else:
                        is_loop = False
                        break
            sleep(4)

    def initial_browser(self, has_save_folder: bool = False, save_folder_path: str = '', has_proxy: bool = True, proxy_area: str = 'hk',
                        is_private: bool = False, is_headless=False, firefox_binary_location: str = '', geckodriver_binary_location: str = '',
                        timeout=1800, auto_get_screenshot=False, time_interval=15, browser_screenshot_tag='', remote_save=False, username='', password='', server_name='',
                        share_name='', remote_folder_path=''):
        """This function is used to initial FireFox browser

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
            remote_save(bool): This is the flag whether to save file to remote folder
            username(str): This is the username
            password(str): This is the password
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            remote_folder_path(str): This is the public folder path that file will be saved under share name folder
        Returns:
            Tuple[Firefox,WebDriverWait]: [self.browser, self.wait]

        """
        # add new tab setting
        opts = Options()

        opts.set_preference("browser.link.open_newwindow.restriction", 0)
        opts.set_preference("browser.link.open_newwindow", 3)

        # 降低 Firefox 子进程数量，节省资源
        opts.set_preference("dom.ipc.processCount", 1)
        # 禁用磁盘缓存，避免写 I/O 与临时目录锁问题
        opts.set_preference("browser.cache.disk.enable", False)
        # 禁用视频解码器（大部分自动化页面用不到）
        opts.set_preference("media.ffmpeg.enabled", False)
        # 使用唯一临时 profile，避免 profile.lock 竞争
        profile_dir = tempfile.mkdtemp(prefix="ffprof_")
        opts.set_preference("profile", profile_dir)

        # opts.headless = is_headless
        if is_headless:
            opts.add_argument("--headless")
        if firefox_binary_location:
            opts.binary_location = firefox_binary_location
        if is_private:
            opts.add_argument('-private')

        if has_proxy or has_save_folder:
            if has_proxy:
                opts.set_preference("network.proxy.type", 2)
                opts.set_preference("network.proxy.autoconfig_url", f'http://rbins-ap.bosch.com/{proxy_area}.pac')
            else:
                opts.set_preference("network.proxy.type", 0)

            # default download folder setting
            if has_save_folder:
                opts.set_preference("browser.download.folderList", 2)
                opts.set_preference("browser.download.manager.showWhenStarting", False)
                opts.set_preference("browser.download.dir", f'{save_folder_path}')
                opts.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
                self.save_folder_path = save_folder_path

        if geckodriver_binary_location:
            service = Service(executable_path=geckodriver_binary_location, log_path='geckodriver.log')
            self.browser = webdriver.Firefox(options=opts, service=service)
        else:
            self.browser = webdriver.Firefox(options=opts)
        self.wait = WebDriverWait(self.browser, timeout)

        if auto_get_screenshot:
            self.apply_decorator_to_methods()
            self.time_interval = time_interval
            self.stop_screenshot_thread = False
            self.thr = Thread(target=self.auto_get_browser_screenshots,
                              args=[save_folder_path, time_interval, browser_screenshot_tag, remote_save, username, password, server_name, share_name, remote_folder_path],
                              daemon=True)
            self.thr.start()

        return self.browser, self.wait

    def stop_auto_get_browser_screenshots(self):
        """ This function is used to stop auto get browser screenshots

        """
        if not self.stop_screenshot_thread:
            sleep(self.time_interval + 1)
            self.stop_screenshot_thread = True
            if self.thr is not None:
                self.thr.join()

    def auto_get_browser_screenshots(self, save_folder_path, time_interval=15, browser_screenshot_tag='', remote_save=False, username='', password='', server_name='',
                                     share_name='', remote_folder_path=''):
        """ This function is used to auto get browser screenshots

        Args:
            save_folder_path(str): This is the folder to save screenshots
            time_interval(int): This is the time interval to get screenshot
            browser_screenshot_tag(str): Tag in screenshot name
            remote_save(bool): This is the flag whether to save file to remote folder
            username(str): This is the username
            password(str): This is the password
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            remote_folder_path(str): This is the public folder path that file will be saved under share name folder
        """
        screenshot_folder_path = save_folder_path + os.sep + 'Screenshots'
        if not os.path.exists(screenshot_folder_path):
            os.mkdir(screenshot_folder_path)

        for file_name in os.listdir(screenshot_folder_path):
            os.remove(screenshot_folder_path + os.sep + file_name)

        while not self.stop_screenshot_thread:
            if time_interval < 5:
                sleep(5)
            else:
                sleep(time_interval)

            # current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_time = ''.join(re.findall('\d+', str(datetime.datetime.now())))
            if browser_screenshot_tag:
                screenshot_file_path = screenshot_folder_path + os.sep + f'{browser_screenshot_tag}_{current_time}.png'
            else:
                screenshot_file_path = screenshot_folder_path + os.sep + f'{current_time}.png'

            try:
                self.browser.save_screenshot(screenshot_file_path)
                sleep(1)
                if remote_save:
                    remote_screenshot_folder_path = remote_folder_path + os.sep + 'Screenshots'
                    is_folder_exist = smb_check_folder_exist(username, password, server_name, share_name, remote_screenshot_folder_path)
                    if not is_folder_exist:
                        smb_create_folder(username, password, server_name, share_name, remote_screenshot_folder_path)

                    if browser_screenshot_tag:
                        remote_screenshot_folder_path = remote_screenshot_folder_path + os.sep + browser_screenshot_tag
                        is_folder_exist = smb_check_folder_exist(username, password, server_name, share_name, remote_screenshot_folder_path)
                        if not is_folder_exist:
                            smb_create_folder(username, password, server_name, share_name, remote_screenshot_folder_path)

                    remote_file_path = remote_screenshot_folder_path + os.sep + screenshot_file_path.split(os.sep)[-1]
                    smb_copy_file_local_to_remote(username, password, server_name, share_name, screenshot_file_path, remote_file_path)
            except InvalidSessionIdException:
                break

    def wait_page_loaded(self):
        """This function is used to wait page loaded

        """
        is_loaded = False
        while not is_loaded:
            page_status = self.browser.execute_script("return document.readyState")
            print('page_status: ', page_status)
            if page_status == 'complete':
                is_loaded = True
            else:
                sleep(1)

    def create_and_switch_tab(self, web_link: str, tab_index: int, close_pre_tab: bool = False, pre_tab_index: int = 0):
        """This function is used to create new tab and switch to it

        Args:
            close_pre_tab(bool): This indicates whether to close history tab
            pre_tab_index(int): This is the history tab index
            web_link(str): This is the link where browser will navigate to
            tab_index(int): This is the index of tab whose index starts from 0. if close_pre_tab is True, this is the tab index after close history tab

        """
        self.browser.execute_script('window.open("","_blank");')
        if close_pre_tab:
            if pre_tab_index:
                self.browser.switch_to.window(self.browser.window_handles[pre_tab_index])
            self.browser.close()
        sleep(1)
        self.browser.switch_to.window(self.browser.window_handles[tab_index])
        self.browser.get(web_link)
        sleep(1)

    def wait_element_presence_by_css_selector(self, css_selector: str, by: By = By.CSS_SELECTOR):
        """This function is used to wait element by css selector

        Args:
            css_selector(str): This is the css selector of target element
            by(By): This is the By method to find element
        """
        self.wait.until(EC.presence_of_element_located((by, css_selector)))
        sleep(1)

    def wait_element_invisible_by_css_selector(self, css_selector: str, by: By = By.CSS_SELECTOR):
        """This function is used to wait element by css selector

        Args:
            css_selector(str): This is the css selector of target element
            by(By): This is the By method to find element
        """
        self.wait.until(EC.invisibility_of_element_located((by, css_selector)))
        sleep(1)

    def wait_invisibility_of_loading_window(self, wait_time_before_check: int = 2):
        """This function is used to wait loading window to disappear

        Args:
            wait_time_before_check(int):This is the wait time before check invisibility of loading window

        """
        sleep(wait_time_before_check)
        self.wait.until(EC.invisibility_of_element_located((By.ID, LOADING_WINDOW_ID_NAME)))
        sleep(2)

    def check_login_error(self):
        """This function is used to check whether password is correct

        """
        while True:
            sleep(2)
            try:
                self.browser.find_element(By.CSS_SELECTOR, ERROR_ICON_CSS_SELECTOR)
            except NoSuchElementException:
                try:
                    self.switch_iframe([IFRAME_CSS_SELECTOR])
                    sleep(1)
                    self.browser.find_element(By.CSS_SELECTOR, LOGIN_CONTINUE_BUTTON_CSS_SELECTOR)
                except NoSuchElementException:
                    try:
                        self.browser.find_element(By.CSS_SELECTOR, MAIN_PAGE_HEADER_CSS_SELECTOR)
                    except NoSuchElementException:
                        pass
                    else:
                        return True
                else:
                    self.click_or_input_by_css_selector(LOGIN_CONTINUE_BUTTON_CSS_SELECTOR, 'click')
                    sleep(2)
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_PAGE_HEADER_CSS_SELECTOR)))
                    sleep(2)
                    return True
            else:
                sleep(self.time_interval + 1)  # auto get one more screenshot
                self.stop_screenshot_thread = True
                return False

    def login_sap_with_password(self, sap_user: str = '', sap_password: str = ''):
        """This function is used to log in sap with username and password

        Args:
            sap_user(str): This is the username of current sap system
            sap_password(str):This is the password of sap user
        """
        while True:
            sleep(2)
            try:
                self.browser.find_element(By.CSS_SELECTOR, USERNAME_CSS_SELECTOR)
            except NoSuchElementException:
                try:
                    self.switch_iframe([IFRAME_CSS_SELECTOR])
                    sleep(1)
                    self.browser.find_element(By.CSS_SELECTOR, MAIN_PAGE_HEADER_CSS_SELECTOR)
                except NoSuchElementException:
                    try:
                        self.browser.find_element(By.CSS_SELECTOR, LOGIN_CONTINUE_BUTTON_CSS_SELECTOR)
                    except NoSuchElementException:
                        pass
                    else:
                        self.click_or_input_by_css_selector(LOGIN_CONTINUE_BUTTON_CSS_SELECTOR, 'click')
                        sleep(2)
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_PAGE_HEADER_CSS_SELECTOR)))
                        sleep(2)
                        return True
                else:
                    return True
            else:
                self.fill_input_field_with_single_value(sap_user, USERNAME_CSS_SELECTOR)
                sleep(1)
                self.fill_input_field_with_single_value(sap_password, PASSWORD_CSS_SELECTOR)
                sleep(1)
                self.click_or_input_by_css_selector(LOGIN_BUTTON_CSS_SELECTOR, 'click')
                sleep(3)
                return self.check_login_error()

    def login_web_sap(self, sap_system_name: str, sap_user: str, sap_password: str):
        """This function is used to wait sap web page loaded before input t-code

        sleep is the buffer time for assuring page loaded

        Args:
            sap_system_name(str): This is the sap system name
            sap_user(str): This is the username of current sap system
            sap_password(str):This is the password of sap user

        """
        self.browser.delete_all_cookies()
        sleep(2)
        self.browser.get(f'https://{sap_system_name}.wdisp.bosch.com/sap/bc/gui/sap/its/webgui?sap-client=011&sap-language=EN#')
        is_login = self.login_sap_with_password(sap_user, sap_password)
        if is_login:
            login_wait = WebDriverWait(self.browser, 180)
            try:
                self.browser.refresh()
            except TimeoutException:
                self.browser.get(f'https://{sap_system_name}.wdisp.bosch.com/sap/bc/gui/sap/its/webgui?sap-client=011&sap-language=EN#')

            try_times = 5
            while try_times > 0:
                try:
                    login_wait.until(EC.invisibility_of_element_located((By.ID, CENTER_BOX_ID)))
                    sleep(2)
                    login_wait.until(EC.invisibility_of_element_located((By.ID, INFO_BOX_ID)))
                    sleep(2)
                    login_wait.until(EC.invisibility_of_element_located((By.ID, LOADING_WINDOW_ID_NAME)))
                except TimeoutException:
                    try_times -= 1
                    self.browser.refresh()
                    sleep(2)
                else:
                    break

            # self.wait.until(EC.invisibility_of_element_located((By.ID, CENTER_BOX_ID)))
            # sleep(2)
            # self.wait.until(EC.invisibility_of_element_located((By.ID, INFO_BOX_ID)))
            # sleep(2)
            # self.wait_invisibility_of_loading_window()
            return True
        else:
            return False

    def switch_iframe(self, iframe_list: list, loop_check: bool = False, by: By = By.CSS_SELECTOR):
        """This function is used to switch iframe if there are iframes within html

        Args:
            loop_check(bool): Whether to loop check iframe exists
            iframe_list (list): This is the list of iframe css selectors or names
            by(By): This is the By method to find element
        """
        is_switch = False
        while not is_switch:
            self.browser.switch_to.default_content()
            for iframe in iframe_list:
                try:
                    iframe_element = self.browser.find_element(by, iframe)
                    self.browser.switch_to.frame(iframe_element)
                    is_switch = True
                except NoSuchElementException:
                    is_switch = False
            if not loop_check:
                is_switch = True
            sleep(1)

    def input_t_code(self, t_code: str, iframe_list=None):
        """This function is used to input t-code and click enter

        Args:
            iframe_list(list): This is the list of iframe name
            t_code(str): This is the t-code of task

        """
        if iframe_list is None:
            iframe_list = [IFRAME_CSS_SELECTOR]
        sleep(2)
        if iframe_list:
            self.switch_iframe(iframe_list)
            sleep(1)

        t_code_element = self.browser.find_element(By.CSS_SELECTOR, T_CODE_CSS_SELECTOR)
        t_code_element.clear()
        t_code_element.send_keys(t_code)
        t_code_element.send_keys(Keys.ENTER)

    def clear_single_input_field(self, css_selector: str, is_enter: bool = False, by: By = By.CSS_SELECTOR):
        """This function is used to clear single input field

        Args:
            is_enter(bool): This is the flag whether to press Enter key
            css_selector(str): This is the css selector of target input field
            by(By): This is the By method to find element
        """
        self.wait.until(EC.presence_of_element_located((by, css_selector)))
        sleep(1)
        target_element = self.browser.find_element(by, css_selector)
        target_element.clear()
        if is_enter:
            target_element.send_keys(Keys.ENTER)

    def fill_input_field_with_single_value(self, single_value: str, css_selector: str, is_enter: bool = False, is_tab=False, click_tip: bool = False,
                                           tip_css_selector='', target_element=None, by: By = By.CSS_SELECTOR):
        """This function is used to input single value to single input field

        Args:
            tip_css_selector(str): This is the css selector of target tip/suggestion
            is_enter(bool): This is the flag whether to press Enter key
            is_tab(bool): This is the flag whether to press Tab key
            single_value(str): This is the single value
            css_selector(str): This is the css selector of target input field
            click_tip(bool): Whether to wait and click opinion
            target_element(WebElement): This is the target element
            by(By): This is the By method to find element
        """
        if target_element is None:
            self.wait.until(EC.presence_of_element_located((by, css_selector)))
            sleep(1)
            target_element = self.browser.find_element(by, css_selector)
        target_element.clear()
        sleep(1)
        actions = ActionChains(self.browser)
        actions.click(target_element)
        actions.send_keys(single_value)
        actions.pause(1)
        actions.perform()
        actions.reset_actions()
        sleep(1)
        if click_tip:
            if not tip_css_selector:
                tip_css_selector = f"div[data-itemvalue1='{single_value}']"
            self.wait_element_presence_by_css_selector(tip_css_selector, by=by)
            sleep(1)
            self.click_or_input_by_css_selector(tip_css_selector, 'click', by=by)
            sleep(1)
        if is_enter:
            self.press_keyboard_shortcut([Keys.ENTER], by=by)
            sleep(1)
        if is_tab:
            self.press_keyboard_shortcut([Keys.TAB], by=by)
            sleep(1)
        return target_element

    def input_field_single_value(self, field_title, field_index, field_value, is_enter=False, is_tab=False, need_click_tip=False):
        """ This function is used to input single field value in SE16.

        Args:
            field_index(int): This is the index of field. e.g. 1,2
            is_enter(bool): This is the flag whether to press enter
            is_tab(bool): This is the flag whether to press tab
            need_click_tip(bool): This is the flag whether to click tip
            field_title(str): This is the title of field
            field_value(str): This is the value of field
        """
        target_input_element = self.find_input_element_by_title(field_title, field_index)
        if target_input_element is not None:
            self.move_to_and_click_element('', target_element=target_input_element)
            sleep(1)
            self.fill_input_field_with_single_value(field_value, '', is_enter, is_tab, need_click_tip, '', target_input_element)
            sleep(1)

    def click_radio_checkbox(self, radio_checkbox_title):
        """ This function is used to click radio or checkbox in SE16.

        Args:
            radio_checkbox_title(str): This is the title of radio or checkbox
        """
        self.click_or_input_by_css_selector(f"span[title='{radio_checkbox_title}']", 'click')

    def check_button_popup_and_click(self, button_title, try_times=10, by: By = By.CSS_SELECTOR):
        """ This function is used to check element exist and click.

        Args:
            button_title(str): This is the css selector of button
            try_times(int): This is the times to try
            by(By): This is the By method to find element
        """
        self.wait_invisibility_of_loading_window()
        button_css_selector = f"div[title='{button_title}']"
        try_time = 1
        while try_time <= try_times:
            print(f'try_time: {try_time}')
            try:
                print(f'try to find {button_css_selector}')
                self.browser.find_element(by, button_css_selector)
            except NoSuchElementException:
                sleep(1)
                try_time += 1
            else:
                self.click_or_input_by_css_selector(button_css_selector, 'click', by=by)
                sleep(1)
                self.wait_element_invisible_by_css_selector(button_css_selector, by=by)
                sleep(1)
                break

    def find_input_element_by_title(self, title: str, input_index):
        """This function is used to find input element by title

        Args:
            input_index(int):  This is the index of input element
            title(str): This is the title of input field
        """
        target_input_element = None
        target_input_elements = self.browser.find_elements(By.CSS_SELECTOR, f"input[title='{title}']")
        for index, input_element in enumerate(target_input_elements):
            if index + 1 == input_index:
                target_input_element = input_element
                break

        return target_input_element

    def input_layout(self, layout: str = ''):
        """This function is used to input layout name

        Args:
            layout(str): This is the name of layout
        """
        layout_element = self.browser.find_element(By.CSS_SELECTOR, LAYOUT_CSS_SELECTOR)
        layout_element.clear()
        layout_element.send_keys(layout)

    def click_execute_button(self):
        """This function is used to click execute button to load data page

        """
        self.click_by_selenium_webdriver(EXECUTION_BUTTON_CSS_SELECTOR)

    def press_keyboard_shortcut(self, keyboard_shortcut_list: list, wait_css_selector: str = '', target_css_selector: str = '', by: By = By.CSS_SELECTOR):
        """This function is used to press keyboard shortcut

        Args:
            target_css_selector(str): This is the css selector of target element who will receive key shortcut
            wait_css_selector(str): This is the css selector to wait before press shortcut keys
            keyboard_shortcut_list(list): This is the list of keyboard keys
            by(By): This is the By method to find element
        """
        if wait_css_selector:
            self.wait.until(EC.presence_of_element_located((by, wait_css_selector)))
        sleep(1)
        action_chains = ActionChains(self.browser)
        if target_css_selector:
            target_element = self.browser.find_element(by, target_css_selector)
            action_chains.click(target_element)
            sleep(0.5)
        for keyboard in keyboard_shortcut_list:
            action_chains.key_down(keyboard)
        for keyboard in keyboard_shortcut_list:
            action_chains.key_up(keyboard)
        action_chains.perform()
        sleep(1)
        action_chains.reset_actions()

    def activate_context_click(self, css_selector: str, by: By = By.CSS_SELECTOR):
        """This function is used to execute context click

        Args:
            css_selector(str): This is the css selector which will receive context click
            by(By): This is the By method to find element
        """
        self.wait_element_presence_by_css_selector(css_selector, by=by)
        target_element = self.browser.find_element(by, css_selector)
        action_chains = ActionChains(self.browser)
        action_chains.context_click(target_element).perform()
        sleep(1)
        action_chains.reset_actions()

    def activate_download_excel_file_window(self, wait_css_selector: str = DATA_PAGE_WAIT_CSS_SELECTOR):
        """This function is used to pop up download Excel file window

            Args:
                wait_css_selector(str): This is the css selector to wait before press shortcut keys
        """
        self.press_keyboard_shortcut([Keys.LEFT_SHIFT, Keys.F4], wait_css_selector)

    def select_sap_layout(self, layout_name: str, shortcut_list: list):
        """This function is used to select sap layout

        Args:
            layout_name(str): This is the name of layout
            shortcut_list(list): This is the list of shortcut keys that will activate select layout window

        """
        self.press_keyboard_shortcut(shortcut_list)
        self.wait_invisibility_of_loading_window()
        sleep(1)
        self.wait_element_presence_by_css_selector("#SAPMSSY0120_1-cntTD")
        sleep(1)
        self.click_or_input_by_css_selector("div[title='Find (Ctrl+F)']", 'click')
        sleep(1)
        self.wait_element_presence_by_css_selector("input[title='Search string in Find function in lists']")
        self.fill_input_field_with_single_value(layout_name,
                                                "input[title='Search string in Find function in lists']", is_enter=True)
        self.wait_element_presence_by_css_selector("#SAPMSSY0120_3-cnt")
        self.click_element_by_key_word('#SAPMSSY0120_3-cnt', "#SAPMSSY0120_3-cnt div.urColorTotalIntensifiedOff",
                                       layout_name)
        sleep(2)
        self.wait_invisibility_of_loading_window()
        self.click_or_input_by_css_selector("div[title='Copy (Enter)']", 'click')
        self.wait_element_invisible_by_css_selector("#SAPMSSY0120_1-cntTD")
        sleep(1)

    def select_sap_se16_layout(self, layout_name: str, shortcut_list: list):
        """This function is used to select sap layout

        Args:
            layout_name(str): This is the name of layout
            shortcut_list(list): This is the list of shortcut keys that will activate select layout window

        """
        self.press_keyboard_shortcut(shortcut_list)
        self.wait_invisibility_of_loading_window()
        sleep(1)
        self.wait_element_presence_by_css_selector(".urPWContentTableCellWorkaround")
        sleep(1)
        self.activate_context_click(".urPWContentTableCellWorkaround th[title='Layout']")
        sleep(2)
        self.click_or_input_by_css_selector("tr[aria-label='Find...']", 'click')
        sleep(2)
        self.fill_input_field_with_single_value(layout_name, "input[title='ALV Control: Cell Content']", is_enter=True)
        sleep(1)
        self.click_or_input_by_css_selector("div[title='OK (Enter)']", 'click')
        sleep(2)
        self.press_keyboard_shortcut([Keys.ESCAPE])
        sleep(2)
        self.wait_element_invisible_by_css_selector("input[title='ALV Control: Cell Content']")
        sleep(1)
        self.click_element_by_key_word('.urPWContentTableCellWorkaround',
                                       ".urPWContentTableCellWorkaround tbody[id$='-content'] tr[id*='mrss-cont-none-Row'] td:first-child span span",
                                       layout_name,
                                       )
        self.wait_element_invisible_by_css_selector(".urPWContentTableCellWorkaround")
        sleep(2)

    def remove_existed_file_with_file_name(self, file_name):
        """This function is used to remove files with incorrect file name

        Args:
            file_name(str): This is the file name of file that will be saved in save folder
        """
        for current_file_name in os.listdir(self.save_folder_path):
            if file_name.upper().strip() in current_file_name.upper().strip():
                os.remove(self.save_folder_path + os.sep + current_file_name)
        sleep(2)

    def check_cancel_by_user_status(self):
        """ This function is used to check whether user has cancelled the task

        """
        is_cancelled = False
        try_times = 5
        while try_times > 0:
            try:
                cancel_by_element = self.browser.find_element(By.CSS_SELECTOR, CANCEL_BY_USER_CSS_SELECTOR)
            except NoSuchElementException:
                try_times -= 1
                sleep(0.5)
            else:
                if cancel_by_element.text.strip() == 'Canceled by user':
                    is_cancelled = True
                    break
                else:
                    break
        return is_cancelled

    def input_download_excel_file_name(self, file_name: str, remote_save=False, username='', password='', server_name='', share_name='', remote_folder_path=''):
        """This function used to input excel download file name

        Args:
            file_name(str): This is the file name of Excel file
            remote_save(bool): This is the flag whether to save file to remote folder
            username(str): This is the username
            password(str): This is the password
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            remote_folder_path(str): This is the public folder path that file will be saved under share name folder
            by(By): This is the By method to find element
        """
        # save_file_path = self.save_folder_path + os.sep + file_name
        self.remove_existed_file_with_file_name(file_name)

        switch_result = self.check_window_switch_status(EXCEL_FILE_NAME_INPUT_CSS_SELECTOR, ALWAYS_EXCEL_CSS_SELECTOR)
        if not switch_result['switchResult']:
            self.click_or_input_by_css_selector(ALWAYS_EXCEL_CSS_SELECTOR, 'click')
            sleep(1)
            self.wait_element_presence_by_css_selector(EXCEL_CONTINUE_CSS_SELECTOR)
            ok_button = self.browser.find_element(By.CSS_SELECTOR, EXCEL_CONTINUE_CSS_SELECTOR)
            actions = ActionChains(self.browser)
            actions.click(ok_button)
            actions.perform()
            actions.reset_actions()
            sleep(2)
            try:
                self.browser.find_element(By.CSS_SELECTOR, EXCEL_CONTINUE_CSS_SELECTOR)
            except NoSuchElementException:
                pass
            else:
                self.click_or_input_by_css_selector(EXCEL_CONTINUE_CSS_SELECTOR, 'click')
                sleep(2)
            self.wait_invisibility_of_loading_window()

        is_cancelled = False
        while True:
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, EXCEL_FILE_NAME_INPUT_CSS_SELECTOR)))
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, EXCEL_FILE_NAME_INPUT_CSS_SELECTOR)))
                sleep(1)
                self.press_keyboard_shortcut([Keys.DELETE])

                file_name_input_element = self.browser.find_element(By.CSS_SELECTOR, EXCEL_FILE_NAME_INPUT_CSS_SELECTOR)
                actions = ActionChains(self.browser)
                actions.click(file_name_input_element)
                actions.perform()
                actions.reset_actions()
                sleep(1)
                actions = ActionChains(self.browser)
                actions.send_keys(file_name)
                actions.pause(2)
                actions.send_keys(Keys.ENTER)
                actions.perform()
                actions.reset_actions()
                is_cancelled = self.check_cancel_by_user_status()
                sleep(1)
                break
            except StaleElementReferenceException or ElementNotInteractableException:
                sleep(2)
        sleep(2)
        if not switch_result['switchResult']:
            self.wait_element_invisible_by_css_selector(ALWAYS_EXCEL_CSS_SELECTOR)
            sleep(1)

        if not is_cancelled:
            self.check_file_download_status(self.save_folder_path, file_name)
            if remote_save:
                remote_file_path = remote_folder_path + os.sep + file_name
                smb_copy_file_local_to_remote(username, password, server_name, share_name, self.save_folder_path + os.sep + file_name, remote_file_path)

        return is_cancelled

    def input_y01f_download_excel_file_name(self, file_name: str, remote_save=False, username='', password='', server_name='', share_name='', remote_folder_path=''):
        """This function used to input excel download file name

        Args:
            file_name(str): This is the file name of Excel file
            remote_save(bool): This is the flag whether to save file to remote folder
            username(str): This is the username
            password(str): This is the password
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            remote_folder_path(str): This is the public folder path that file will be saved under share name folder
        """
        # save_file_path = self.save_folder_path + os.sep + file_name
        self.remove_existed_file_with_file_name(file_name)

        while True:
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, Y01F_FILE_NAME_INPUT_CSS_SELECTOR)))
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, Y01F_FILE_NAME_INPUT_CSS_SELECTOR)))
                sleep(1)

                file_name_input_element = self.browser.find_element(By.CSS_SELECTOR, Y01F_FILE_NAME_INPUT_CSS_SELECTOR)
                actions = ActionChains(self.browser)
                actions.click(file_name_input_element)
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
                actions.send_keys(Keys.BACKSPACE)
                actions.perform()
                actions.reset_actions()
                sleep(1)
                actions = ActionChains(self.browser)
                actions.send_keys(file_name)
                actions.pause(2)
                actions.send_keys(Keys.ENTER)
                actions.perform()
                actions.reset_actions()
                sleep(1)
                break
            except StaleElementReferenceException or ElementNotInteractableException:
                sleep(2)
        sleep(2)
        self.wait_element_presence_by_css_selector(Y01F_DOWNLOAD_CONTINUE_BUTTON_CSS_SELECTOR)
        self.move_to_and_click_element(Y01F_DOWNLOAD_CONTINUE_BUTTON_CSS_SELECTOR)
        sleep(2)
        self.wait_invisibility_of_loading_window()
        self.wait_element_invisible_by_css_selector(Y01F_FILE_NAME_INPUT_CSS_SELECTOR)
        sleep(1)
        self.check_file_download_status(self.save_folder_path, file_name)
        if remote_save:
            remote_file_path = remote_folder_path + os.sep + file_name
            smb_copy_file_local_to_remote(username, password, server_name, share_name, self.save_folder_path + os.sep + file_name, remote_file_path)

    def determine_dynamic_selection_button_index(self, section_name: str, multi_selection_button_index: int):
        """This function is used to dynamically determine multiple selection button index according to user input

        Args:
            section_name(str): This the section name
            multi_selection_button_index(int): This is the index of multiple selection button in G/L account selection or other section
        """
        is_find = False
        div_elements = self.browser.find_elements(By.CSS_SELECTOR,
                                                  f"table[aria-label='{section_name}'] div.lsRasterLayout div")
        div_elements_length = len(div_elements)
        while not is_find and multi_selection_button_index <= div_elements_length:
            try:
                self.browser.find_element(By.CSS_SELECTOR,
                                          f"table[aria-label='{section_name}'] div.lsRasterLayout div:nth-child({multi_selection_button_index}) div[title='Multiple selection']").click()
            except NoSuchElementException:
                multi_selection_button_index += 1
            else:
                is_find = True

        return [is_find, multi_selection_button_index]

    def input_multiple_selection(self,
                                 value_list: list,
                                 tab_index: int = 1,
                                 section_name=SECTION_NAME,
                                 multi_selection_button_index: int = MULTIPLE_SECTION_BUTTON_INDEX,
                                 input_css_path: str = MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR,
                                 clear_section_data: bool = False,
                                 get_screenshot: bool = False,
                                 screenshot_folder_path: str = '',
                                 screenshot_file_name_tag: str = 'error_info',
                                 name_format: str = 'time',
                                 paste_method: str = 'clipboard',
                                 by: By = By.CSS_SELECTOR
                                 ):
        """This function is used to input multiple selection for company code, gl account and so on

        Args:
            paste_method(str): This is the copy and paste method for multiple input. e.g. clipboard or file
            tab_index(int): This is the tab index of multiple selection
            section_name(str): This the section name
            multi_selection_button_index(int): This is the index of multiple selection button in G/L account selection
            input_css_path(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            clear_section_data(bool): This is the indicator whether delete all section data before pasting new values
            get_screenshot(bool): This is the flag that indicates whether to save screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
            by(By): This is the By method to find element
        """
        # re-locate multiple selection button
        multiple_index_check_result, multi_selection_button_index = self.determine_dynamic_selection_button_index(
            section_name, multi_selection_button_index)
        if multiple_index_check_result:
            # click multiple selection button
            self.browser.find_element(By.CSS_SELECTOR,
                                      f"table[aria-label='{section_name}'] div.lsRasterLayout div:nth-child({multi_selection_button_index}) div[title='Multiple selection']").click()
            sleep(2)
            self.wait_invisibility_of_loading_window()
            self.wait.until(EC.presence_of_element_located((by, input_css_path)))
            if clear_section_data:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR)))
                sleep(1)
                self.click_or_input_by_css_selector(DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR, 'click')
                sleep(2)
            # click select ranges tab
            if tab_index == 2:
                sleep(3)
                self.click_or_input_by_css_selector(SELECT_RANGES_CSS_SELECTOR, 'click')

            self.wait_multiple_selection_switch(tab_index)
            self.wait.until(EC.presence_of_element_located((by, input_css_path)))
            if paste_method == 'clipboard':
                self.copy_paste_values(value_list, input_css_path, by=by)
            elif paste_method == 'file':
                # temp re-write for linux
                self.copy_paste_values(value_list, input_css_path, by=by)
                # upload_file_path = self.copy_paste_values_by_file(value_list)
                # os.remove(upload_file_path)

            if get_screenshot:
                self.get_screenshot(screenshot_folder_path, screenshot_file_name_tag, name_format)
                sleep(1)
            self.click_or_input_by_css_selector(COPY_BUTTON_CSS_SELECTOR, 'click')
            self.wait.until(EC.invisibility_of_element_located((by, input_css_path)))
            return True
        else:
            return False

    def input_multiple_selection_with_index(self,
                                            value_list: list,
                                            multiple_selection_index: int = 1,
                                            tab_index: int = 1,
                                            input_css_path: str = MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR,
                                            clear_section_data: bool = False,
                                            get_screenshot: bool = False,
                                            screenshot_folder_path: str = '',
                                            screenshot_file_name_tag: str = 'error_info',
                                            name_format: str = 'time',
                                            paste_method: str = 'clipboard',
                                            by: By = By.CSS_SELECTOR
                                            ):

        """This function is used to input multiple selection for company code, gl account and so on

        Args:
            paste_method(str): This is the copy and paste method for multiple input. e.g. clipboard or file
            tab_index(int): This is the tab index of multiple selection
            multiple_selection_index(int): This is the order of Multiple selection button which starts from 1
            input_css_path(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            clear_section_data(bool): This is the indicator whether delete all section data before pasting new values
            get_screenshot(bool): This is the flag that indicates whether to save screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
            by(By): This is the By method to find element
        """
        self.wait_element_presence_by_css_selector("div[title^='Multiple selection' i]")
        multiple_selection_buttons = self.browser.find_elements(By.CSS_SELECTOR, "div[title^='Multiple selection' i]")
        for button_index, multiple_selection_button in enumerate(multiple_selection_buttons):
            if button_index + 1 == multiple_selection_index:
                # self.click_or_input_by_element(multiple_selection_button, 'click')
                self.move_to_and_click_element('', target_element=multiple_selection_button, by=by)
                sleep(2)
                self.wait_invisibility_of_loading_window()
                self.wait.until(EC.presence_of_element_located((by, input_css_path)))
                if clear_section_data:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR)))
                    sleep(1)
                    self.click_or_input_by_css_selector(DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR, 'click')
                    sleep(2)
                # click select ranges tab
                if tab_index == 2:
                    sleep(3)
                    self.click_or_input_by_css_selector(SELECT_RANGES_CSS_SELECTOR, 'click')
                elif tab_index == 3:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_SINGLE_VALUES_CSS_SELECTOR, 'click')
                elif tab_index == 4:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_RANGES_CSS_SELECTOR, 'click')

                self.wait_multiple_selection_switch(tab_index)
                self.wait.until(EC.presence_of_element_located((by, input_css_path)))
                if paste_method == 'clipboard':
                    second_paste = tab_index in [2, 4]
                    self.copy_paste_values(value_list, input_css_path, second_paste=second_paste, by=by)
                # elif paste_method == 'file':
                #     upload_file_path = self.copy_paste_values_by_file(value_list)
                #     os.remove(upload_file_path)

                if get_screenshot:
                    self.get_screenshot(screenshot_folder_path, screenshot_file_name_tag, name_format)
                    sleep(1)
                self.click_or_input_by_css_selector(COPY_BUTTON_CSS_SELECTOR, 'click')
                self.wait.until(EC.invisibility_of_element_located((by, input_css_path)))
                return True

        return False

    def input_query_multiple_selection_with_index(self,
                                                  value_list: list,
                                                  multiple_selection_index: int = 1,
                                                  tab_index: int = 1,
                                                  input_css_path: str = MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR,
                                                  clear_section_data: bool = False,
                                                  get_screenshot: bool = False,
                                                  screenshot_folder_path: str = '',
                                                  screenshot_file_name_tag: str = 'error_info',
                                                  name_format: str = 'time',
                                                  paste_method: str = 'clipboard',
                                                  by: By = By.CSS_SELECTOR
                                                  ):

        """This function is used to input multiple selection for company code, gl account and so on

        Args:
            paste_method(str): This is the copy and paste method for multiple input. e.g. clipboard or file
            tab_index(int): This is the tab index of multiple selection
            multiple_selection_index(int): This is the order of Multiple selection button which starts from 1
            input_css_path(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            clear_section_data(bool): This is the indicator whether delete all section data before pasting new values
            get_screenshot(bool): This is the flag that indicates whether to save screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
            by(By): This is the By method to find element
        """
        self.wait_element_presence_by_css_selector("div[title^='Multiple selection' i]")
        multiple_selection_buttons = self.browser.find_elements(By.CSS_SELECTOR, "div[title^='Multiple selection' i]")
        for button_index, multiple_selection_button in enumerate(multiple_selection_buttons):
            if button_index + 1 == multiple_selection_index:
                self.move_to_and_click_element(f"tr[id$='mrss-cont-left-Row-{button_index}'] td div div.urST5SCMetricInner")
                sleep(2)
                # self.click_or_input_by_element(multiple_selection_button, 'click')
                self.move_to_and_click_element('', target_element=multiple_selection_button, by=by)
                sleep(2)
                self.wait_invisibility_of_loading_window()
                self.wait.until(EC.presence_of_element_located((by, input_css_path)))
                if clear_section_data:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR)))
                    sleep(1)
                    self.click_or_input_by_css_selector(DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR, 'click')
                    sleep(2)
                # click select ranges tab
                if tab_index == 2:
                    sleep(3)
                    self.click_or_input_by_css_selector(SELECT_RANGES_CSS_SELECTOR, 'click')
                elif tab_index == 3:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_SINGLE_VALUES_CSS_SELECTOR, 'click')
                elif tab_index == 4:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_RANGES_CSS_SELECTOR, 'click')

                self.wait_multiple_selection_switch(tab_index)
                self.wait.until(EC.presence_of_element_located((by, input_css_path)))
                if paste_method == 'clipboard':
                    second_paste = tab_index in [2, 4]
                    self.copy_paste_values(value_list, input_css_path, second_paste=second_paste, by=by)
                # elif paste_method == 'file':
                #     upload_file_path = self.copy_paste_values_by_file(value_list)
                #     os.remove(upload_file_path)

                if get_screenshot:
                    self.get_screenshot(screenshot_folder_path, screenshot_file_name_tag, name_format)
                    sleep(1)
                self.click_or_input_by_css_selector(COPY_BUTTON_CSS_SELECTOR, 'click')
                self.wait.until(EC.invisibility_of_element_located((by, input_css_path)))
                return True

        return False

    def input_variant_multiple_selection_with_index(self,
                                                    value_list: list,
                                                    multiple_selection_index: int = 1,
                                                    tab_index: int = 1,
                                                    input_css_path: str = MULTIPLE_WINDOW_FIRST_INPUT_CSS_SELECTOR,
                                                    clear_section_data: bool = False,
                                                    get_screenshot: bool = False,
                                                    screenshot_folder_path: str = '',
                                                    screenshot_file_name_tag: str = 'error_info',
                                                    name_format: str = 'time',
                                                    paste_method: str = 'clipboard',
                                                    by: By = By.CSS_SELECTOR
                                                    ):

        """This function is used to input multiple selection for company code, gl account and so on

        Args:
            paste_method(str): This is the copy and paste method for multiple input. e.g. clipboard or file
            tab_index(int): This is the tab index of multiple selection
            multiple_selection_index(int): This is the order of Multiple selection button which starts from 1
            input_css_path(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            clear_section_data(bool): This is the indicator whether delete all section data before pasting new values
            get_screenshot(bool): This is the flag that indicates whether to save screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
            by(By): This is the By method to find element
        """
        self.wait_element_presence_by_css_selector(".urPWContentTable div[title^='Multiple selection' i]")
        multiple_selection_buttons = self.browser.find_elements(By.CSS_SELECTOR, ".urPWContentTable div[title^='Multiple selection' i]")
        for button_index, multiple_selection_button in enumerate(multiple_selection_buttons):
            if button_index + 1 == multiple_selection_index:
                # self.click_or_input_by_element(multiple_selection_button, 'click')
                self.move_to_and_click_element('', target_element=multiple_selection_button, by=by)
                sleep(2)
                self.wait_invisibility_of_loading_window()
                self.wait.until(EC.presence_of_element_located((by, input_css_path)))
                if clear_section_data:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR)))
                    sleep(1)
                    self.click_or_input_by_css_selector(DELETE_ENTIRE_SELECTION_BUTTON_CSS_SELECTOR, 'click')
                    sleep(2)
                # click select ranges tab
                if tab_index == 2:
                    sleep(3)
                    self.click_or_input_by_css_selector(SELECT_RANGES_CSS_SELECTOR, 'click')
                elif tab_index == 3:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_SINGLE_VALUES_CSS_SELECTOR, 'click')
                elif tab_index == 4:
                    sleep(3)
                    self.click_or_input_by_css_selector(EXCLUDE_RANGES_CSS_SELECTOR, 'click')

                self.wait_multiple_selection_switch(tab_index)
                self.wait.until(EC.presence_of_element_located((by, input_css_path)))
                if paste_method == 'clipboard':
                    second_paste = tab_index in [2, 4]
                    self.copy_paste_values(value_list, input_css_path, second_paste=second_paste, by=by)
                # elif paste_method == 'file':
                #     upload_file_path = self.copy_paste_values_by_file(value_list)
                #     os.remove(upload_file_path)

                if get_screenshot:
                    self.get_screenshot(screenshot_folder_path, screenshot_file_name_tag, name_format)
                    sleep(1)
                self.click_or_input_by_css_selector(COPY_BUTTON_CSS_SELECTOR, 'click')
                self.wait.until(EC.invisibility_of_element_located((by, input_css_path)))
                return True

        return False

    def copy_paste_values(self, value_list: list, input_css_selector: str, wait_alert: bool = True, is_enter: bool = True, second_paste=False, by: By = By.CSS_SELECTOR):
        """This function is used to copy and paste values

        Args:
            wait_alert(bool): This indicates whether to click copy button and wait paster warning window pop up
            input_css_selector(str): This is the css selector to locate first input element
            value_list(list): This is the values need to be input
            is_enter(bool): Whether to press enter key
            second_paste(bool): Whether to paste values for the second time
            by(By): This is the By method to find element
        """

        value_list = [item for item in value_list if not pd.isna(item) and str(item).strip()]
        paste_values = '\r\n'.join(value_list)
        pyperclip.copy(paste_values)
        sleep(1)
        if wait_alert:
            self.press_keyboard_shortcut([Keys.SHIFT, Keys.F12], by=by)
            sleep(1)
            self.wait_element_presence_by_css_selector("#UpDownDialogDontAllow-cnt")
            sleep(1)

        self.press_keyboard_shortcut([Keys.CONTROL, 'v'], by=by)
        sleep(2)
        self.wait_element_invisible_by_css_selector("#UpDownDialogDontAllow-cnt")
        if second_paste:
            self.move_to_and_click_element(input_css_selector, by=by)
            sleep(3)
            self.press_keyboard_shortcut([Keys.CONTROL, 'v'], by=by)

        sleep(1)
        try:
            first_row_element = self.browser.find_element(by=by, value=input_css_selector)
            while not first_row_element.get_attribute('value'):
                sleep(1)
                first_row_element = self.browser.find_element(by=by, value=input_css_selector)
        except NoSuchElementException or StaleElementReferenceException:
            sleep(2)
        if is_enter:
            self.press_keyboard_shortcut([Keys.ENTER], by=by)
        sleep(2)

    def wait_multiple_selection_switch(self, tab_index: int):
        """This function is used to wait multiple selection tab switch complete

        Args:
            tab_index(int): This is the tab index of multiple selection
        """
        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, f'td.lsTbsPanel2 div:first-child div:nth-child({tab_index}) div[aria-selected="true"]')
            except NoSuchElementException:
                try:
                    self.browser.find_element(By.CSS_SELECTOR, f'td.lsTbsPanel2 div:first-child div[selected="true"]:nth-child({tab_index})')
                except NoSuchElementException:
                    sleep(2)
                else:
                    break
            else:
                break

    def click_or_input_by_css_selector(self, css_selector: str, action_type: str, content: str = '', by: By = By.CSS_SELECTOR):
        """Click or input element by using css selector to find it

        Args:
            css_selector(str): This is css selector
            action_type(str): click or input
            content(str): This is the content to be input
            by(By): This is the By method to find element
        """
        self.wait.until(EC.presence_of_element_located((by, css_selector)))
        element = self.browser.find_element(by, css_selector)
        if action_type == 'click':
            self.browser.execute_script("arguments[0].click();", element)
        elif action_type == 'input':
            self.browser.execute_script(f"arguments[0].value=arguments[1];", element, content)

    def move_to_and_click_element(self, css_selector: str, target_element=None, by: By = By.CSS_SELECTOR):
        """This function is used to move mouse to element and click

        Args:
            css_selector: This is css selector of element
            target_element(WebElement): This is the target element
            by(By): This is the By method to find element
        """
        actions = None
        try:
            if target_element is None:
                self.wait.until(EC.presence_of_element_located((by, css_selector)))
                target_element = self.browser.find_element(by, css_selector)
            actions = ActionChains(self.browser)

            self.browser.execute_script('arguments[0].scrollIntoView(true);', target_element)
            sleep(2)
            actions.move_to_element(target_element)
            actions.click()
            actions.perform()
            sleep(1)

        except StaleElementReferenceException:
            pass
        finally:
            if actions is not None:
                actions.reset_actions()

    def click_or_input_by_element(self, css_element: WebElement, action_type: str, content: str = ''):
        """Click or input element by using css selector to find it

        Args:
            css_element(WebElement): This is css element
            action_type(str): click or input
            content(str): This is the content to be input
        """
        if action_type == 'click':
            self.browser.execute_script("arguments[0].click();", css_element)
        elif action_type == 'input':
            self.browser.execute_script(f"arguments[0].value=arguments[1];", css_element, content)

    def click_element_by_key_word(self, wait_css_selector: str, target_elements_css_selector: str, key_word: str, click_type: str = 'single',
                                  search_method: str = 'accurate', click_method: str = 'css_selector', by: By = By.CSS_SELECTOR):
        """This function is used to click element by key word when there is no effective css selector

        Args:
            wait_css_selector(str): This is the css selector to wait before click target element
            target_elements_css_selector(str): This is the css selector for all siblings elements of target element(contains target element)
            key_word(str): This is the key word to identify target element
            click_type(str): single or double
            search_method(str): accurate or blur
            click_method(str):css_selector or element
            by(By): This is the By method to find element
        """
        is_find = False
        self.wait.until(EC.presence_of_element_located((by, wait_css_selector)))
        sleep(1)
        target_elements = self.browser.find_elements(by, target_elements_css_selector)
        correct_target_element = None
        element_index = 1
        for target_element in target_elements:
            if search_method == 'accurate' and target_element.text.strip() == key_word or search_method == 'blur' and key_word in target_element.text.strip():
                is_find = True
                if click_method == 'css_selector':
                    self.click_or_input_by_element(target_element, 'click')
                else:
                    self.move_to_and_click_element('', target_element, by=by)
                if click_type == 'double':
                    if click_method == 'css_selector':
                        self.click_or_input_by_element(target_element, 'click')
                    else:
                        self.move_to_and_click_element('', target_element, by=by)
                correct_target_element = target_element
                break
            element_index += 1
        sleep(1)
        return is_find, correct_target_element, element_index

    def click_by_selenium_webdriver(self, element_css_selector: str, by: By = By.CSS_SELECTOR):
        """This function is used to click element by selenium original click

        Args:
            element_css_selector(str): This the is css selector of target element
            by(By): This is the By method to find element
        """
        self.wait.until(EC.presence_of_element_located((by, element_css_selector)))
        target_element = self.browser.find_element(by, element_css_selector)
        target_element.click()

    def get_screenshot(self, screenshot_folder_path: str, screenshot_file_name_tag: str = 'error_info', name_format: str = 'time'):
        """This function is used to get screenshot of current webpage

        Args:
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            screenshot_folder_path(str): This is the folder path of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
        """
        if name_format == 'time':
            date_info = str(datetime.datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')
        else:
            date_info = str(datetime.datetime.now().date())
        screenshot_file_name = f'{screenshot_file_name_tag}_{date_info}.png'
        screen_file_path = screenshot_folder_path + os.sep + screenshot_file_name
        self.browser.save_screenshot(screen_file_path)
        return [screenshot_file_name, screen_file_path]

    def check_target_text_appearance(self, target_text: str, text_css_selector: str, after_text_css_selector: str,
                                     check_method: str = 'equal',
                                     text_tag: str = 'No Data',
                                     case_sensitive: bool = False,
                                     has_screenshot: bool = False,
                                     screenshot_folder_path: str = '',
                                     screenshot_file_name_tag: str = 'No Data',
                                     name_format: str = 'time',
                                     by: By = By.CSS_SELECTOR
                                     ):
        """

        Args:
            case_sensitive(bool): This indicates whether to consider the upper and lower case of text
            check_method(str): This is the method to check target text.  e.g. equal, contain, startswith, endswith
            text_tag(str): This is the status which is used to describe situation or result when target text occurs
            target_text(str): This is the target text to detect
            text_css_selector(str): This is the css selector of text element
            after_text_css_selector(str): This is the css selector of element if there is no target text
            has_screenshot(bool): Whether to save screenshot when target text occurs
            screenshot_folder_path(str): This is the folder path of screenshot when target text occurs
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            name_format(str): This indicates whether user date or datetime to name screenshot
            by(By): This is the By method to find element
        """
        check_result = self.check_window_switch_status(after_text_css_selector, text_css_selector, has_screenshot,
                                                       screenshot_folder_path, screenshot_file_name_tag, name_format)
        check_result['text_tag'] = text_tag
        if not check_result['switchResult']:
            text_element_content = self.browser.find_element(by, text_css_selector).text.strip()
            if not case_sensitive:
                target_text = target_text.upper()
                text_element_content = text_element_content.upper()

            if check_method == 'equal' and text_element_content == target_text:
                check_result['is_text'] = True
            elif check_method == 'contain' and target_text in text_element_content:
                check_result['is_text'] = True
            elif check_method == 'startswith' and text_element_content.startswith(target_text):
                check_result['is_text'] = True
            elif check_method == 'endswith' and text_element_content.endswith(target_text):
                check_result['is_text'] = True

        return check_result

    def check_window_switch_status(self, target_css_selector: str,
                                   before_target_css_selector: str = ERROR_ICON_CSS_SELECTOR,
                                   has_screenshot: bool = False,
                                   screenshot_folder_path: str = '',
                                   screenshot_file_name_tag: str = 'error_info',
                                   name_format: str = 'time'
                                   ):
        """This function is used to check whether there are temp elements before loading target element

        Args:
            has_screenshot(bool): Whether to save screenshot when there is an error window popping up
            screenshot_folder_path(str): This is the folder path of screenshot when there is an error occurred
            target_css_selector(str): This is the selector whose occurrence indicates data is loaded successfully
            before_target_css_selector(str): This is the selector whose occurrence indicates that there is temp element
            before loading target element
            name_format(str): This indicates whether user date or datetime to name screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
        """
        check_result = self.check_data_load_status(target_css_selector, before_target_css_selector, has_screenshot,
                                                   screenshot_folder_path, screenshot_file_name_tag, name_format)
        check_result['switchResult'] = not check_result['isError']
        return check_result

    def check_data_load_status(self, success_css_selector: str,
                               error_css_selector: str = ERROR_ICON_CSS_SELECTOR,
                               has_screenshot: bool = False,
                               screenshot_folder_path: str = '',
                               screenshot_file_name_tag: str = 'error_info',
                               name_format: str = 'time',
                               by: By = By.CSS_SELECTOR
                               ):
        """This function is used to check whether there are errors when loading data by clicking execution button

        Args:
            has_screenshot(bool): Whether to save screenshot when there is an error window popping up
            screenshot_folder_path(str): This is the folder path of screenshot when there is an error occurred
            success_css_selector(str): This is the selector whose occurrence indicates data loaded successfully
            error_css_selector(str): This is the selector whose occurrence indicates that there is an error or no data
            name_format(str): This indicates whether user date or datetime to name screenshot
            screenshot_file_name_tag(str):This is the first part file name of screenshot
            by(By): This is the By method to find element
        """
        check_result = {'isError': False, 'Screenshot Path': '', 'Screenshot Name': ''}
        is_loop = True
        sleep(3)
        self.wait_invisibility_of_loading_window()
        while is_loop:
            try:
                self.browser.find_element(by, success_css_selector)
            except NoSuchElementException:
                try:
                    self.browser.find_element(by, error_css_selector)
                except NoSuchElementException:
                    sleep(2)
                else:
                    check_result['isError'] = True
                    is_loop = False
            else:
                is_loop = False

        if has_screenshot:
            screenshot_file_name, screen_file_path = self.get_screenshot(screenshot_folder_path,
                                                                         screenshot_file_name_tag,
                                                                         name_format)
            check_result['Screenshot Path'] = screen_file_path
            check_result['Screenshot Name'] = screenshot_file_name

        return check_result

    def wait_file_upload_confirmation_dialog(self):
        """This function is used to wait file upload confirmation dialog window and click ok button

        """
        sleep(1)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, UPLOAD_CONFIRM_BUTTON_CSS_SELECTOR)))
        sleep(1)
        self.click_or_input_by_css_selector(UPLOAD_CONFIRM_BUTTON_CSS_SELECTOR, 'click')
        sleep(1)

    @staticmethod
    def get_popup_window_screenshot(screenshot_file_path):
        """This function is used to get screenshot of popup window

        Args:
            screenshot_file_path(str): This is the folder path of screenshot
        """
        if os.path.exists(screenshot_file_path):
            os.remove(screenshot_file_path)
        # get screenshot
        result = subprocess.run(["scrot", "-u", screenshot_file_path], capture_output=True, text=True)
        # check screenshot result
        if result.returncode == 0:
            print(f"Screenshot saved to {screenshot_file_path}")
        else:
            print(f"Error taking screenshot: {result.stderr}")

    def upload_files_in_popup_window(self, file_path, window_name='File Upload', has_screenshot=False, screenshot_folder_path=''):
        """This function is used to upload files in popup window

        Args:
            screenshot_folder_path(str): This is the folder path to save screenshot
            window_name(str): This is the window name
            file_path(str): This is the file path
            has_screenshot(bool): Whether to save screenshot when there is an error window popping up
        """
        screenshot_path_list = []
        try:
            # get window id
            try_times = 10
            window_id = None
            while try_times >= 0:
                result = subprocess.run(["xdotool", "search", "--name", window_name], stdout=subprocess.PIPE, text=True)
                window_id = result.stdout.strip()

                if not window_id:
                    print(f"No window with title '{window_name}' found.")
                    try_times -= 1
                    sleep(2)
                else:
                    print(f"Found window ID: {window_id}")
                    break

            if window_id is not None:

                if has_screenshot:
                    if not screenshot_folder_path:
                        screenshot_folder_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'Download_Folder' + os.sep + 'Screenshots'

                if not os.path.exists(screenshot_folder_path):
                    os.makedirs(screenshot_folder_path)

                # activate window
                subprocess.run(["xdotool", "windowfocus", window_id])
                sleep(2)

                file_name = file_path.split(os.sep)[-1]
                if has_screenshot:
                    window_image_file_path = screenshot_folder_path + os.sep + f'{file_name}_popup_window_1.png'
                    self.get_popup_window_screenshot(window_image_file_path)
                    screenshot_path_list.append(window_image_file_path)

                subprocess.run(["xdotool", "key", "ctrl+l"])
                sleep(2)
                # input file path
                subprocess.run(["xdotool", "type", file_path])
                sleep(2)

                if has_screenshot:
                    file_input_image_file_path = screenshot_folder_path + os.sep + f'{file_name}_popup_window_2.png'
                    self.get_popup_window_screenshot(file_input_image_file_path)
                    screenshot_path_list.append(file_input_image_file_path)

                # press enter key
                subprocess.run(["xdotool", "windowfocus", window_id])
                sleep(2)
                subprocess.run(["xdotool", "key", "Return"])
                sleep(2)

                if has_screenshot:
                    after_enter_image_file_path = screenshot_folder_path + os.sep + f'{file_name}_popup_window_3.png'
                    self.get_popup_window_screenshot(after_enter_image_file_path)
                    screenshot_path_list.append(after_enter_image_file_path)
            else:
                print(f"No window with title '{window_name}' found.")
            return screenshot_path_list

        except Exception as e:
            print(f"An error occurred: {e}")
            return screenshot_path_list

    def drag_by_offset(self, target_element, x_offset, y_offset):
        """
        Drag the specified element by a given pixel offset.

        Args:
            target_element (WebElement): The element to be dragged.
            x_offset: Horizontal offset in pixels (positive for right, negative for left).
            y_offset: Vertical offset in pixels (positive for down, negative for up).
        """
        try:
            actions = ActionChains(self.browser)
            actions.click_and_hold(target_element)
            actions.pause(0.2)
            actions.move_by_offset(x_offset, y_offset)
            actions.pause(0.1)
            actions.release().perform()
            actions.reset_actions()
        except MoveTargetOutOfBoundsException as e:
            print(f"[RPA Warning] Drag element is out of bounds: {e}")
        except Exception as e:
            print(f"[RPA Warning] An error occurred while dragging the element: {e}")

    def select_abap_variant_name(self, variant_name: str):
        """This function is used to select ABAP variant name

        Args:
            variant_name(str): This is the variant name to be selected
        """
        variant_name = variant_name.strip().upper()
        self.wait_element_presence_by_css_selector(EXECUTION_BUTTON_CSS_SELECTOR)
        sleep(1)
        self.press_keyboard_shortcut([Keys.SHIFT, Keys.F5])
        sleep(2)
        self.wait_element_presence_by_css_selector("div[id$='-mrss-cont-left']")
        tr_elements = self.browser.find_elements(By.CSS_SELECTOR, "tr[id*='mrss-cont-left-Row']")
        if tr_elements:
            for tr_element in tr_elements:
                first_td_element = tr_element.find_element(By.CSS_SELECTOR, "td:nth-child(1)")
                span_element = tr_element.find_element(By.CSS_SELECTOR, "td:nth-child(2) div span span")
                span_element_text = span_element.text.strip().upper()
                if span_element_text == variant_name:
                    self.move_to_and_click_element('', first_td_element)
                    sleep(1)
                    self.move_to_and_click_element("div[title='Choose (F2)']")
                    sleep(1)
                    self.wait_element_invisible_by_css_selector("div[id$='-mrss-cont-left']")
                    return

        print(f"Variant name '{variant_name}' not found in the list.")
        self.press_keyboard_shortcut([Keys.ESCAPE])
        self.wait_element_invisible_by_css_selector("div[id$='-mrss-cont-left']")

    def quit_browser(self):
        """This function is used to quit browser

        """
        if not self.stop_screenshot_thread:
            self.stop_screenshot_thread = True
            if self.thr is not None:
                self.thr.join()

        self.browser.quit()
