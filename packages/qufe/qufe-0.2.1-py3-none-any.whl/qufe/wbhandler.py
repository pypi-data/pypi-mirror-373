"""
Web Browser Automation Handler

This module provides enhanced browser automation capabilities using SeleniumBase
with custom timeout configurations, network monitoring, and interactive element discovery.

Classes:
    Browser: Base class for browser automation with common functionality
    Chrome: Chrome browser implementation (placeholder for future development)
    FireFox: Firefox browser implementation with profile management
"""

import os
import sys
import json
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional, Union

# Configure SeleniumBase timeout settings before import
import seleniumbase.config.settings as sb_settings

# Custom timeout configurations (extended from defaults)
sb_settings.MINI_TIMEOUT = 5         # Default 2s → 5s
sb_settings.SMALL_TIMEOUT = 20       # Default 7s → 20s
sb_settings.LARGE_TIMEOUT = 40       # Default 10s → 40s
sb_settings.EXTREME_TIMEOUT = 80     # Default 30s → 80s
sb_settings.PAGE_LOAD_TIMEOUT = 180  # Default 120s → 180s

from seleniumbase import SB
from selenium.webdriver.support.ui import WebDriverWait


class Browser:
    """
    Base browser automation class with enhanced functionality.
    
    Provides network monitoring, element discovery, and automation utilities
    built on top of SeleniumBase framework.
    
    Attributes:
        sb: SeleniumBase instance for browser automation
    """
    
    def __init__(
        self,
        private_mode: bool = True,
        mobile_mode: bool = False,
        use_selenium_wire: bool = False,
    ):
        """
        Initialize browser instance.
        
        Args:
            private_mode: Enable private/incognito browsing mode
            mobile_mode: Enable mobile device emulation
            use_selenium_wire: Enable network request interception
        """
        self._private_mode = private_mode
        self._mobile_mode = mobile_mode
        self._sa = None
        self._init_webdriver(use_selenium_wire)
        self.sb = SB
        self._start_driver()

    def _init_webdriver(self, use_selenium_wire: bool) -> None:
        """Initialize webdriver with specified configuration."""
        raise NotImplementedError("Subclasses must implement _init_webdriver method")

    def wait_for_ajax(self, timeout: int = 20) -> None:
        """
        Wait for AJAX requests to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        WebDriverWait(self.sb.driver, timeout).until(
            lambda drv: drv.execute_script(
                "return window.jQuery ? jQuery.active == 0 : true"
            )
        )

    def _start_driver(self) -> None:
        """
        Start the browser driver.
        
        Note: SeleniumBase requires context manager entry for proper initialization.
        """
        self.sb = self._sa.__enter__()

    def quit_driver(self) -> None:
        """Clean up and quit the browser driver."""
        self._sa.__exit__(None, None, None)

    def inject_network_capture(self) -> None:
        """
        Inject JavaScript to capture fetch/XHR network requests.
        
        Creates a global __selenium_logs array that stores network request details
        including URL, status, method, request body, and response.
        """
        inject_script = """
        window.__selenium_logs = [];
        (function() {
          const origFetch = window.fetch;
          window.fetch = function(...args) {
            return origFetch(...args).then(res => {
              const clone = res.clone();
              clone.text().then(body => {
                window.__selenium_logs.push({
                  type: 'fetch', url: clone.url,
                  status: clone.status,
                  method: args[1]?.method||'GET',
                  request: args[1]?.body||null,
                  response: body
                });
              });
              return res;
            });
          };
          
          const _open = XMLHttpRequest.prototype.open;
          XMLHttpRequest.prototype.open = function(m,u) {
            this._m=m; this._u=u; return _open.apply(this, arguments);
          };
          
          const _send = XMLHttpRequest.prototype.send;
          XMLHttpRequest.prototype.send = function(b) {
            this.addEventListener('load', () => {
              window.__selenium_logs.push({
                type: 'xhr', url: this._u,
                status: this.status, method: this._m,
                request: b||null, response: this.responseText
              });
            });
            return _send.apply(this, arguments);
          };
        })();
        """
        
        self.sb.driver.execute_script(inject_script)
        print('Network capture script injected successfully.')

    def get_network_logs(self) -> List[Dict[str, Any]]:
        """
        Retrieve captured network requests.
        
        Returns:
            List of network request dictionaries containing type, URL, status,
            method, request body, and response data.
        """
        # Ensure page is fully loaded before retrieving logs
        self.sb.wait_for_ready_state_complete()
        self.wait_for_ajax()
        self.sb.sleep(1)
        
        logs = self.sb.driver.execute_script("return window.__selenium_logs;")
        return logs or []

    @staticmethod
    def extract_url_parameters(
        url: str, 
        param: str, 
        split_char: str = ''
    ) -> List[List[str]]:
        """
        Extract parameter values from URL query string.
        
        Args:
            url: URL to parse
            param: Parameter name to extract ('get_all' returns all parameters)
            split_char: Character to split parameter values on
            
        Returns:
            List of parameter value lists
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        if param == 'get_all':
            return query_params
    
        parsed_params = query_params.get(param, [''])
        param_count = len(parsed_params)
        
        if param_count > 1:
            if split_char:
                return [value.split(split_char) for value in parsed_params]
            else:
                return [[value] for value in parsed_params]
        elif param_count == 1:
            value = parsed_params[0]
            return [value.split(split_char)] if split_char else [[value]]
        else:
            return []

    def find_element_info(self, selector: str, concat_text: bool = False) -> None:
        """
        Find and display information about elements matching the selector.
        
        Args:
            selector: CSS or XPath selector
            concat_text: If True, concatenate element text; if False, show detailed info
        """
        elements = self.sb.find_elements(selector)
        
        if not elements:
            print(f'No elements found with selector: {selector}')
            return
            
        for element in elements:
            if not concat_text:
                print(f'outerHTML: {element.get_attribute("outerHTML")}')
                print(f'class: {element.get_attribute("class")}')
                print(f'value: {element.get_attribute("value")}')
                print(f'text: {element.text.strip()}', end='\n\n')
            else:
                print(f"'{element.text.strip()}'", end=', ')

    @staticmethod
    def generate_text_selectors(
        texts: List[str],
        element_type: str,
    ) -> List[str]:
        """
        Generate XPath selectors for elements containing specific text.
        
        Args:
            texts: List of text content to match
            element_type: HTML element type (e.g., 'a', 'span', 'button')
            
        Returns:
            List of XPath selectors
            
        Example:
            generate_text_selectors(['Home', 'About'], 'a')
            # Returns: ["//a[normalize-space(.)='Home']", "//a[normalize-space(.)='About']"]
        """
        return [f"//{element_type}[normalize-space(.)='{text}']" for text in texts]
    
    def find_common_attribute(
        self, 
        selectors: List[str], 
        attribute: str, 
        verbose: bool = False
    ) -> str:
        """
        Find the most common attribute value among elements matched by selectors.
        
        This method helps discover common patterns in element attributes,
        useful for building robust selectors when class names might change.
        
        Args:
            selectors: List of CSS or XPath selectors
            attribute: Attribute name to analyze (e.g., 'class', 'id')
            verbose: Print detailed information if True
            
        Returns:
            Most frequently occurring attribute value
            
        Example:
            regions = ['Seoul', 'Busan', 'Daegu']
            selectors = [f"//label[normalize-space(text())='{region}']" for region in regions]
            common_class = browser.find_common_attribute(selectors, 'class')
        """
        attribute_counts = {}

        for selector in selectors:
            elements = self.sb.find_elements(selector)
            for element in elements:
                attr_value = element.get_attribute(attribute)
                if attr_value:
                    attribute_counts[attr_value] = attribute_counts.get(attr_value, 0) + 1
        
        if not attribute_counts:
            return ''
            
        most_common = max(attribute_counts, key=attribute_counts.get)
        
        if verbose:
            print(f'Most common {attribute}: {most_common}')
            print(f'Attribute distribution: {attribute_counts}')

        return most_common


class Chrome(Browser):
    """Chrome browser implementation (placeholder for future development)."""
    
    def _init_webdriver(self, use_selenium_wire: bool) -> None:
        """Initialize Chrome webdriver."""
        # TODO: Implement Chrome-specific configuration
        # This is a placeholder for future Chrome browser implementation
        pass


class Firefox(Browser):
    """Firefox browser implementation with profile management and private browsing."""
    
    def _init_webdriver(self, use_selenium_wire: bool) -> None:
        """
        Initialize Firefox webdriver with profile detection and private browsing.
        
        Args:
            use_selenium_wire: Enable network request interception
        """
        profile_path = self._find_firefox_profile()
        
        firefox_args = []
        if self._private_mode:
            firefox_args.append('-private')
            
        if profile_path:
            firefox_args.extend(['-profile', profile_path])

        firefox_prefs = None
        if self._private_mode:
            firefox_prefs = 'browser.privatebrowsing.autostart:True,network.proxy.type:0'

        self._sa = SB(
            headless=False,
            use_wire=use_selenium_wire,
            browser='firefox',
            window_position='0, 25',
            window_size='1920, 1055',
            firefox_arg=','.join(firefox_args) if firefox_args else None,
            firefox_pref=firefox_prefs,
        )

    @staticmethod
    def _find_firefox_profile() -> Optional[str]:
        """
        Find Firefox default profile path across different operating systems.
        
        Returns:
            Path to Firefox profile directory or None if not found
        """
        try:
            if sys.platform == "darwin":  # macOS
                profile_dir = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/")
            elif sys.platform == "win32":  # Windows
                profile_dir = os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles/")
            else:  # Linux and other Unix-like systems
                profile_dir = os.path.expanduser("~/.mozilla/firefox/")

            if os.path.exists(profile_dir):
                profiles = [
                    d for d in os.listdir(profile_dir) 
                    if d.endswith('.default-release')
                ]
                if profiles:
                    return os.path.join(profile_dir, profiles[0])
        except Exception:
            # Silently fail if profile detection fails
            pass
        return None
