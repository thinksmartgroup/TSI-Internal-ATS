from browser_use import BrowserConfig
import asyncio
import logging
import json
from dataclasses import dataclass, field
from typing import Optional, Any, List

logger = logging.getLogger(__name__)

@dataclass
class BrowserState:
    """
    A class to represent the state of the browser.
    """
    url: Optional[str] = None
    title: Optional[str] = None
    current_page: Optional[Any] = None
    element_tree: Optional[Any] = None
    cache_clickable_elements_hashes: Optional[Any] = None
    tabs: List[Any] = field(default_factory=list)
    screenshot: Optional[Any] = None
    clickable_elements: List[Any] = field(default_factory=list)
    visible_elements: List[Any] = field(default_factory=list)
    html: Optional[str] = None
    browser_context: Optional[Any] = None  # Add browser context to track the browser instance

class SimpleBrowserConfig(BrowserConfig):
    """
    Simple browser configuration that handles manual captcha verification.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the browser configuration.
        """
        super().__init__(*args, **kwargs)
        self._state = BrowserState()
        self._headless = False  # Always show the browser window

    async def setup_browser_context(self, playwright, browser_context):
        """
        Set up the browser context (called when browser is first initialized).
        
        Args:
            playwright: The Playwright instance
            browser_context: The browser context
        """
        # Store the browser context for later use
        self._state.browser_context = browser_context
        logger.info("Browser context set up successfully")
        
    async def handle_captcha(self, page):
        """
        Handle captcha verification by waiting for user input.
        
        Args:
            page: The Playwright page object
        """
        try:
            # Check for common captcha selectors
            captcha_selectors = [
                "iframe[src*='captcha']",
                "iframe[src*='recaptcha']",
                "iframe[src*='hcaptcha']",
                "form#challenge-form",
                "div#cf-challenge-running",
                "div.captcha",
                "div.recaptcha",
                "div.hcaptcha"
            ]
            
            for selector in captcha_selectors:
                if await page.query_selector(selector):
                    logger.info("Captcha verification detected. Waiting for manual verification...")
                    print("\n" + "="*50)
                    print("CAPTCHA VERIFICATION DETECTED")
                    print("Please complete the verification in the browser window.")
                    print("The system will continue automatically after verification.")
                    print("="*50 + "\n")
                    
                    # Wait for the captcha to be completed (this is a simple approach)
                    # In a real implementation, you might want to wait for a specific element
                    # that indicates the captcha has been completed
                    await asyncio.sleep(30)  # Wait for 30 seconds
                    logger.info("Captcha verification completed.")
                    print("\nCaptcha verification completed. Continuing...\n")
                    return
        except Exception as e:
            logger.error(f"Error handling captcha verification: {e}")
            print("\nError handling captcha verification. Please try again.\n")
    
    async def before_navigation(self, page):
        """
        Hook that runs before navigation.
        
        Args:
            page: The Playwright page object
        """
        await self.handle_captcha(page)
    
    async def after_navigation(self, page):
        """
        Hook that runs after navigation.
        
        Args:
            page: The Playwright page object
        """
        await self.handle_captcha(page)
        # Update the current page, URL, and title in the state
        self._state.current_page = page
        self._state.url = page.url
        self._state.title = await page.title()
        
        # Take a screenshot and update the state
        try:
            self._state.screenshot = await page.screenshot(type="jpeg", quality=30)
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            self._state.screenshot = None
        
        # Update HTML content
        try:
            self._state.html = await page.content()
        except Exception as e:
            logger.error(f"Error getting HTML content: {e}")
            self._state.html = None
        
        # Update tabs if needed
        if page not in self._state.tabs:
            self._state.tabs.append(page)

    async def get_state(self, cache_clickable_elements_hashes=None):
        """
        Return the current state of the browser configuration.
        
        Args:
            cache_clickable_elements_hashes: Optional argument to handle caching of clickable elements.
        
        Returns:
            The current state object.
        """
        # Update the state with the provided cache_clickable_elements_hashes
        if cache_clickable_elements_hashes is not None:
            self._state.cache_clickable_elements_hashes = cache_clickable_elements_hashes
        
        # Return the state object
        return self._state
    
    def to_json(self):
        """
        Convert the state to a JSON string.
        
        Returns:
            A JSON string representation of the state.
        """
        return json.dumps({
            "url": self._state.url,
            "title": self._state.title,
            "current_page": str(self._state.current_page) if self._state.current_page else None,
            "element_tree": str(self._state.element_tree) if self._state.element_tree else None,
            "cache_clickable_elements_hashes": self._state.cache_clickable_elements_hashes,
            "tabs": [str(tab) for tab in self._state.tabs] if self._state.tabs else [],
            "has_screenshot": self._state.screenshot is not None,
            "html_length": len(self._state.html) if self._state.html else 0,
            "clickable_elements_count": len(self._state.clickable_elements) if self._state.clickable_elements else 0,
            "visible_elements_count": len(self._state.visible_elements) if self._state.visible_elements else 0
        })
        
    async def get_current_page(self):
        """
        Get the current page.
        
        Returns:
            The current page object.
        """
        return self._state.current_page
    
    async def open_new_tab(self, url=None):
        """
        Open a new tab in the same browser window.
        
        Args:
            url: Optional URL to navigate to in the new tab
            
        Returns:
            The new page object
        """
        try:
            if not self._state.browser_context:
                logger.error("Browser context not available")
                return None
                
            # Create a new page in the same context
            new_page = await self._state.browser_context.new_page()
            self._state.tabs.append(new_page)
            self._state.current_page = new_page
            
            # Navigate to the URL if provided
            if url:
                await new_page.goto(url)
                await self.after_navigation(new_page)
                
            logger.info(f"Opened new tab with URL: {url if url else 'about:blank'}")
            return new_page
        except Exception as e:
            logger.error(f"Error opening new tab: {e}")
            return None
    
    async def switch_to_tab(self, index_or_title):
        """
        Switch to a different tab by index or title.
        
        Args:
            index_or_title: The index (0-based) or title of the tab to switch to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._state.tabs:
                logger.error("No tabs available")
                return False
                
            if isinstance(index_or_title, int):
                # Switch by index
                if 0 <= index_or_title < len(self._state.tabs):
                    self._state.current_page = self._state.tabs[index_or_title]
                    await self._state.current_page.bring_to_front()
                    logger.info(f"Switched to tab at index {index_or_title}")
                    return True
                else:
                    logger.error(f"Tab index out of range: {index_or_title}")
                    return False
            else:
                # Switch by title
                for page in self._state.tabs:
                    title = await page.title()
                    if index_or_title.lower() in title.lower():
                        self._state.current_page = page
                        await page.bring_to_front()
                        logger.info(f"Switched to tab with title containing '{index_or_title}'")
                        return True
                
                logger.error(f"No tab found with title containing '{index_or_title}'")
                return False
        except Exception as e:
            logger.error(f"Error switching tabs: {e}")
            return False
        
    def clickable_elements_to_string(self):
        """
        Convert clickable elements to a string representation.
        
        Returns:
            A string representation of the clickable elements.
        """
        if not self._state.clickable_elements:
            return "No clickable elements"
        
        elements_str = []
        for i, element in enumerate(self._state.clickable_elements):
            if hasattr(element, 'as_dict'):
                element_dict = element.as_dict()
                elements_str.append(f"{i+1}. {element_dict.get('text', '')} ({element_dict.get('tag_name', '')})")
            else:
                elements_str.append(f"{i+1}. {str(element)}")
        
        return "\n".join(elements_str) 