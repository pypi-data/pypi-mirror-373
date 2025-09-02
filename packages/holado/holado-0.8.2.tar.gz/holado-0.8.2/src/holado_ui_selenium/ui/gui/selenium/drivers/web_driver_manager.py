#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
import re
from holado_ui_selenium.ui.gui.selenium.handlers.enums import BrowserTypes
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import tempfile
from holado_system.system.global_system import GlobalSystem, OSTypes
import packaging
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class WebDriverManager(object):
    """ Manager of web drivers.
    """
    chromedriver_download_url = "http://chromedriver.storage.googleapis.com"
    geckodriver_download_url = "https://github.com/mozilla/geckodriver/releases"
    
    def __init__(self, browser_type, path_manager):
        self.__browser_type = browser_type
        self.__browser_version = None
        self.__browser_driver_version = None
        self.__current_proxy = None
    
    @property
    def browser_type(self):
        """
        @return the browser type
        """
        return self.__browser_type
    
    @property
    def current_proxy(self):
        """
        @return Current proxy
        """
        return self.__current_proxy
    
    @current_proxy.setter
    def current_proxy(self, proxy):
        """
        Update current proxy
        @param proxy the proxy to set
        """
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"current proxy has changed ({self.currentProxy} -> {proxy})")
        self.__current_proxy = proxy
    
    @property
    def browser_version(self):
        if self.__browser_version is None:
            self.__browser_version = self.__extract_browser_version()
        
        return self.__browser_version
    
    @property
    def browser_driver_version(self):
        # if self.__browser_driver_version is None:
        #     b_version = self.browser_version
        #     bd_version = self.__get_browser_driver_version_from_db(self.browser_type, b_version)
        #     if bd_version is None:
        #         bd_version = self.__update_browser_driver_dependencies(self.browser_type, b_version)
        #     self.__browser_driver_version = bd_version
        
        return self.__browser_driver_version
    
    def __extract_browser_version(self):
        if GlobalSystem.get_os_type() == OSTypes.Linux:
            if self.browser_type == BrowserTypes.Chrome:
                cmd_res = GlobalSystem.execute_command("chromium --version", do_log_output=False, do_raise_on_stderr=True)
            elif self.browser_type == BrowserTypes.Firefox:
                cmd_res = GlobalSystem.execute_command("firefox --version", do_log_output=False, do_raise_on_stderr=True)
            else:
                raise TechnicalException(f"Unmanaged browser type '{self.browser_type}'")
            
            m = re.search(r"\d+\.[^ ]*", cmd_res.output)
            if m:
                return packaging.version.parse(m.group())
            else:
                raise TechnicalException(f"Failed to find Firefox version in [{cmd_res.output}]")
        else:
            raise TechnicalException(f"Unmanaged OS type '{GlobalSystem.get_os_type().name}'")
        
    # def __update_browser_driver_dependencies(self, browser_type, browser_version):
    #     res = None
    #
    #     # Extract all browser driver versions
    #     bd_versions = self.__extract_browser_driver_versions()
    #
    #     # Find browser driver version adapted to given browser version
    #     for ver in bd_versions:
    #         if browser_version == ver:
    #             res = ver
    #             break
    #         elif browser_version < ver:
    #             continue
    #         else:
    #             if res is None or res < ver:
    #                 res = ver
    #
    #     # Download driver
    #     File tempDir = PathManager.createTemporaryDirectory("webdriver")
    #     String filePath = downloadBrowserDriver(res, tempDir)
    #     String destPath = getPathManager().getChromedriverPath(res, false)
    #     PathManager.makeDirectoriesOfFile(destPath)
    #     PathManager.extractArchiveZip(new File(filePath), new File(destPath).getParentFile())
    #
    #     # Store version in DB
    #     setBrowserDriverVersionInDB(browser_type, browser_driver_version, res)
    #
    #     return res
    #
    #
    # def __downloadBrowserDriver(self, Version browserdriverVersion, File destDir):
    #     switch (browser_type):
    #     case Chrome:
    #         return downloadChromedriver(browserdriverVersion, destDir)
    #     default:
    #         raise TechnicalException(f"Unmanaged browser type '%s'", browser_type))
    #
    #
    #
    # def __downloadChromedriver(self, Version browserdriverVersion, File destDir):
    #     String hostname = getTestProperties().getProperty("browser.chromedriver.download.hostname", None)
    #     String archiveFileName = f"chromedriver_%s.zip", getPathManager().getChromedriverOSName())
    #     String url = f"http:#%s/%s/%s", hostname, browserdriverVersion.getVersion(), archiveFileName)
    #
    #     String res = PathManager.buildPath(destDir.toString(), archiveFileName)
    #     PathManager.makeDirectoriesOfFile(res)
    #     String parameters = f"-f -o \"%s\" %s", res, url)   
    #     CurlCommandResult cmdRes
    #     try:
    #         cmdRes = CommonSystem.executeCurl(parameters, None, None)
    #     } catch (FunctionalException e):
    #         raise TechnicalException(e)
    #
    #     if (cmdRes.hasError()):
    #         String errorMsg = f"Error when downloading file '%s': %s", url, cmdRes.getError())
    #         raise FunctionalException(errorMsg)
    #
    #
    #     return res
    #
    #
    # def __extract_browser_driver_versions(self, ):
    #     switch (browser_type):
    #     case Chrome:
    #         return extractChromedriverVersions()
    #     default:
    #         raise TechnicalException(f"Unmanaged browser type '%s'", browser_type))
    #
    #
    #
    # def __extractChromedriverVersions(self, ):
    #     List<String> res = new ArrayList<String>()
    #
    #     String hostname = getTestProperties().getProperty("browser.chromedriver.download.hostname", None)
    #     CommandResult cmdRes
    #     try:
    #         cmd_res = CommonSystem.execute_curl(f"--location {self.chromedriver_download_url}")
    #     } catch (FunctionalException e):
    #         raise TechnicalException(e)
    #
    #     if cmd_res.has_error:
    #         raise FunctionalException(f"Error when extracting all chrome driver versions with curl: {cmd_res.error}")
    #
    #     String osName = getPathManager().getChromedriverOSName()
    #     Pattern pattern = Pattern.compile(f"<Key>(\\d{2,}[^</]+)/chromedriver_%s.zip</Key>", osName))
    #     Matcher match = pattern.matcher(cmdRes.getOutput())
    #     while (match.find())
    #         res.add(match.group(1))
    #
    #     return res
    #
    #
    # def __get_browser_driver_version_from_db(self, BrowserTypes browser_type, Version browserVersion):
    #     String dbPath = getPathManager().getWebDriverDBPath()
    #     WebDriverDBDriver dbDriver = new WebDriverDBDriver(dbPath)
    #     dbDriver.connect()
    #     try:
    #         String result = dbDriver.getBrowserDriverVersion(browser_type.getValue(), browserVersion.getVersion())
    #         if result is None:
    #             return None
    #         else
    #             return new Version(result)
    #     } finally:
    #         dbDriver.disconnect()
    #
    #
    #
    # def __setBrowserDriverVersionInDB(self, BrowserTypes browser_type, Version browserVersion, Version browserDriverVersion):
    #     String dbPath = getPathManager().getWebDriverDBPath()
    #     WebDriverDBDriver dbDriver = new WebDriverDBDriver(dbPath)
    #     dbDriver.connect()
    #     try:
    #         dbDriver.setBrowserDriverVersion(browser_type.getValue(), browserVersion.getVersion(), browserDriverVersion.getVersion())
    #     } finally:
    #         dbDriver.disconnect()
        
    

    # """
    # @return New WebDriver instance 
    # """
    # def createWebDriver_WithRedo(self, ):
    #     Redo<WebDriver> redo = new Redo<WebDriver>("create web driver"):
    #         @Override
    #         def _process(self, ):
    #             return createWebDriver()
    #
    #
    #         @Override
    #         def _processAfterInterrupt(self, Thread thread):
    #             logger.warn("Creation of web driver has timed out  killing existing browser drivers and retry")
    #             # Kill existing browser driver
    #             try:
    #                 killBrowserDriver()
    #             } catch (FunctionalException exc):
    #                 Tools.logError(logger, "Failed to kill browser driver", exc, false)
    #
    #
    #
    #     }
    #     redo.withProcessTimeout(120, ChronoUnit.SECONDS)
    #     redo.withTimeout(600, ChronoUnit.SECONDS)
    #     return redo.execute()
    
    
    def create_web_driver(self):
        """
        @return New WebDriver instance 
        """
        return self.__create_web_driver(self.browser_type)
    
    def __create_web_driver(self, browser_type):
        if browser_type == BrowserTypes.Chrome:
            return self.__create_web_driver_chrome()
        elif browser_type == BrowserTypes.Firefox:
            return self.__create_web_driver_firefox()
        else:
            raise TechnicalException(f"Unmanaged browser type '{browser_type}'")
                
    def __create_web_driver_chrome(self):
        # For all possible parameters (official site): http://chromedriver.chromium.org/capabilities
        # For possible arguments of ChromeOptions.add_argument: https://peter.sh/experiments/chromium-command-line-switches/
        # For possible options: https://chromium.googlesource.com/chromium/src/+/master/chrome/common/chrome_switches.cc
        # For possible prefs: https://chromium.googlesource.com/chromium/src/+/master/chrome/common/pref_names.cc
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Creating chrome driver...")

        # Set chromedriver path
        driver_path = self._selenium_path_manager.get_chromedriver_path()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Using chromedrive path '{driver_path}'")
        service = webdriver.ChromeService(executable_path=driver_path)
        
        options = webdriver.ChromeOptions()
        preferences = {}
        
        options.unhandled_prompt_behavior = "ignore"
        
        # Set default page to blank page
        preferences["homepage_is_newtabpage"] = True
        preferences["homepage"] = "about:blank"
        
        # Set user profile
        profile_path = tempfile.mkdtemp(prefix="chrome_profile")
        options.add_argument("--user-data-dir=" + profile_path)
        
        # Disable info bar
        options.add_argument("--disable-infobars")
        
        # Adjust popup settings
        options.add_argument("--disable-popup-blocking")
        
        # Prompt for download
        preferences["download.prompt_for_download"] = True
        
        # Enable Flash
        preferences["profile.default_content_setting_values.plugins"] = 1
        preferences["profile.content_settings.plugin_whitelist.adobe-flash-player"] = 1
        preferences["profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player"] = 1
        
        options.add_experimental_option("prefs", preferences)
        
        res = webdriver.Chrome(options=options, service=service)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Created chrome driver.")
        
        return res
        
    def __create_web_driver_firefox(self):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Creating firefox driver...")

        # Set geckodriver path
        driver_path = self._selenium_path_manager.get_geckodriver_path()
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Using geckodriver path '{driver_path}'")
        service = webdriver.FirefoxService(executable_path=driver_path)
        
        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        options = webdriver.FirefoxOptions()
        options.set_preference("webdriver.log.file", "/dev/None")

        res = webdriver.Firefox(options=options, service=service)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug("Created firefox driver.")
        
        return res
    
    def kill_browser_driver(self):
        """
        Kill browser driver
        """
        self.__kill_browser_driver(self.browser_type)
    
    
    def __kill_browser_driver(self, browser_type):
#         switch (CommonSystem.getOSType()):
#         case Windows:
#             Map<Integer, String> processes = CommonSystem.getRunningProcesses()
#
#             switch (browser_type):
#             case Chrome:
#                 CommonSystem.closeProcessesForCommandPattern(processes, "chromedriver.exe", CloseParameters.kill())
#                 CommonSystem.closeProcessesForCommandPattern(processes, "chrome.exe", CloseParameters.kill())
#                 break
#
#             case Firefox:
#                 CommonSystem.closeProcessesForCommandPattern(processes, "geckodriver.exe", CloseParameters.kill())
#                 CommonSystem.closeProcessesForCommandPattern(processes, "firefox.exe", CloseParameters.kill())
#                 break
#
#             case IE:
#                 CommonSystem.closeProcessesForCommandPattern(processes, "IEDriverServer.exe", CloseParameters.kill())
#                 CommonSystem.closeProcessesForCommandPattern(processes, "iexplore.exe", CloseParameters.kill())
#                 break
#
#             default:
#                 raise TechnicalException(f"Unmanaged browser type '%s'", browser_type))
#
#             break
#
# #        case Linux:
# #            break
#
#         default:
#             raise NotImplementedException(f"Method not implemented for OS type '%s'", CommonSystem.getOSType().name()))
#
#
#         # Wait to let time for OS to release resources
#         Tools.sleep(10000)
    
    
    
    
    
    