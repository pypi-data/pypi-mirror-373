"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
import shutil
import time
import boto3
import platform
from ..aws import S3
from ..cfg import Configuration

def __enable_download_in_headless_chrome(driver, downloadDirectory):
    """
    This function was pulled from
    https://github.com/shawnbutton/PythonHeadlessChrome/blob/master/driver_builder.py#L44
    There is currently a "feature" in chrome where
    headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481
    Specifically this comment ( https://bugs.chromium.org/p/chromium/issues/detail?id=696481#c157 )
    saved the day by highlighting that download wasn't working because it was opening up in another tab.
    This method is a hacky work-around until the official chromedriver support for this.
    Requires chrome version 62.0.3196.0 or above.
    """
    driver.execute_script(
        "var x = document.getElementsByTagName('a'); var i; for (i = 0; i < x.length; i++) { x[i].target = '_self'; }")
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior',
              'params': {'behavior': 'allow', 'downloadPath': downloadDirectory}}  # 'util/selenium'
    command_result = driver.execute("send_command", params)
    print("response from browser:")
    for key in command_result:
        print("result:" + key + ":" + str(command_result[key]))

def _init_bin(executable_name):
    BIN_DIR = "/tmp/bin"
    CURR_BIN_DIR = "/opt/python/bin"
    currfile = os.path.join(CURR_BIN_DIR, executable_name)
    newfile = os.path.join(BIN_DIR, executable_name)
    if not os.path.isfile(newfile):
        start = time.time()
        if not os.path.exists(BIN_DIR):
            print("Creating bin folder")
            os.makedirs(BIN_DIR)
        print("Copying binaries for " + executable_name + " in /tmp/bin")
        shutil.copy2(currfile, newfile)
        print("Giving new binaries permissions for lambda")
        os.chmod(newfile, 0o775)
        elapsed = time.time() - start
        print(executable_name + " ready in " + str(elapsed) + "s.")

def _init_bin_s3(executable_name):
    BIN_DIR = "/tmp/bin"
    s3Filepath = 'lambda_layers/bin/'
    objectFilepath = os.path.join(s3Filepath, executable_name)
    newfile = os.path.join(BIN_DIR, executable_name)
    if not os.path.isfile(newfile):
        if not os.path.exists(BIN_DIR):
            print("Creating bin folder")
            os.makedirs(BIN_DIR)
        client = boto3.client('s3')
        client.download_file('bfi-cfg', objectFilepath, newfile)
        print('{} downloaded!'.format(executable_name))
        print("Giving new binaries permissions for lambda")
        os.chmod(newfile, 0o775)

def getDriverLinux(downloadDirectory=os.getcwd(), detach=False):
    ## Slowness:
    # https://github.com/codeceptjs/CodeceptJS/issues/561
    # https://stackoverflow.com/questions/49032878/disable-proxy-via-python-for-selenium-with-headless-chrome
    # https://stackoverflow.com/questions/62898801/selenium-headless-chrome-runs-much-slower
    ##
    # _init_bin_s3("headless-chromium")
    # _init_bin_s3("chromedriver")
    # Permissions
    # os.chmod("util/selenium/bin/chromedriver", 0o775)
    # os.chmod("util/selenium/bin/headless-chromium", 0o775)
    chrome_options = webdriver.ChromeOptions()
    if detach:
        chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280,720')
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("enable-automation")
    # chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument('--user-data-dir={}'.format(downloadDirectory))
    # chrome_options.add_argument('--hide-scrollbars')
    # chrome_options.add_argument('--enable-logging')
    # chrome_options.add_argument('--log-level=0')
    # chrome_options.add_argument('--v=99')
    # chrome_options.add_argument('--single-process')
    # chrome_options.add_argument('--data-path={}'.format(downloadDirectory))
    # chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--homedir={}'.format(downloadDirectory))
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--disk-cache-dir={}'.format(downloadDirectory))
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36')
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--proxy-server=")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    # chrome_options.binary_location = "/usr/bin/chromium-browser"
    # don't tell chrome that it is automated
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option('useAutomationExtension', False)
    prefs = {'download.default_directory': downloadDirectory,
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': False,
             'safebrowsing.disable_download_protection': True,
             'profile.default_content_setting_values.automatic_downloads': 1,
             "plugins.always_open_pdf_externally": True} #,
             # 'profile.managed_default_content_settings.images': 2}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)  # , executable_path="util/selenium/bin/chromedriver", service_log_path='util/selenium/chromedriver.log')
    # __enable_download_in_headless_chrome(driver, downloadDirectory)
    return driver

def getDriverWindows(downloadDirectory=os.getcwd(), detach=False):
    chrome_options = webdriver.ChromeOptions()
    if detach:
        chrome_options.add_experimental_option("detach", True)
    # chrome_options.add_argument("enable-automation")
    prefs = {'download.default_directory': downloadDirectory,
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': False,
             'safebrowsing.disable_download_protection': True,
             'profile.default_content_setting_values.automatic_downloads': 1,
             "plugins.always_open_pdf_externally": True}
    chrome_options.add_experimental_option('prefs', prefs)
    # pacificoBots = 'Pacifico-Bots'
    # chromedriverPath = os.getcwd().replace("\\", '/').split(pacificoBots)[0] + pacificoBots + '/pacifico_devel/util/selenium/binWindows/chromedriver'
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)
    return driver

def getDriverMac(downloadDirectory=os.getcwd(), detach=False):
    chrome_options = webdriver.ChromeOptions()
    if detach:
        chrome_options.add_experimental_option("detach", True)
    prefs = {'download.default_directory': downloadDirectory,
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': False,
             'safebrowsing.disable_download_protection': True,
             'profile.default_content_setting_values.automatic_downloads': 1,
             "plugins.always_open_pdf_externally": True}
    chrome_options.add_experimental_option('prefs', prefs)
    return webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

def getDriverLinuxChromium(downloadDirectory, detach=False):
    chromedriverPath = r'/usr/bin/chromedriver_legacy'  # os.getcwd().replace("\\", '/') + '/pacifico_devel/util/selenium/binLinux/chromedriver'
    # os.chmod(chromedriverPath, 0o775)
    headlessChromiumPath = r'/usr/bin/headless-chromium'  # os.getcwd().replace("\\", '/') + '/pacifico_devel/util/selenium/binLinux/headless-chromium'
    # os.chmod(headlessChromiumPath, 0o775)
    # _init_bin_s3("headless-chromium")
    # _init_bin_s3("chromedriver")
    chrome_options = webdriver.ChromeOptions()
    if detach:
        chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir={}'.format(downloadDirectory))
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path={}'.format(downloadDirectory))
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir={}'.format(downloadDirectory))
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disk-cache-dir={}'.format(downloadDirectory))
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36')
    chrome_options.binary_location = headlessChromiumPath
    prefs = {'download.default_directory': downloadDirectory,
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': False,
             'safebrowsing.disable_download_protection': True,
             'profile.default_content_setting_values.automatic_downloads': 1}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chromedriverPath, chrome_options=chrome_options, service_log_path=downloadDirectory)
    __enable_download_in_headless_chrome(driver)
    return driver

def getDriver(downloadDirectory=os.getcwd(), chromium=False, detach=False):
    try:
        if chromium:
            return getDriverLinuxChromium(downloadDirectory, detach)
        elif 'mac' in platform.platform():
            return getDriverMac(downloadDirectory, detach)
        elif 'Linux' in platform.platform():
            return getDriverLinux(downloadDirectory, detach)
        else:
            return getDriverWindows(downloadDirectory, detach)
    except Exception as e:
        import traceback
        import sys
        traceback.print_exc()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        x = ''.join('!! ' + line for line in lines)
        awsAccessKey = Configuration.get('AWS_ACCESS_KEY')
        awsSecretKey = Configuration.get('AWS_SECRET_KEY')
        S3.writeToBucket(str(e) + str(x), "selenium.txt", awsAccessKey=awsAccessKey, awsSecretKey=awsSecretKey)

