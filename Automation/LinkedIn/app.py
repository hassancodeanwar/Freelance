import os
import time
import logging
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('linkedin_login.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInBot:
    def __init__(self, username, password):
        """
        Initialize the LinkedIn automation bot
        
        :param username: LinkedIn login email or phone
        :param password: LinkedIn login password
        """
        self.username = username
        self.password = password
        
        # Setup Chrome options for more robust automation
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize webdriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def validate_credentials(self):
        """
        Validate email/phone and password format
        
        :return: Boolean indicating credential validity
        """
        # Modified to allow phone number or email
        email_phone_pattern = r'^(\+?\d{10,14}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$'
        
        if not re.match(email_phone_pattern, self.username):
            logger.error("Invalid email or phone number format")
            return False
        
        if len(self.password) < 8:
            logger.error("Password too short")
            return False
        
        return True
    
    def login(self):
        """
        Automate LinkedIn login process
        
        :return: Boolean indicating login success
        """
        try:
            # Validate credentials first
            if not self.validate_credentials():
                return False
            
            # Navigate to LinkedIn login page
            self.driver.get('https://www.linkedin.com/login')
            logger.info("Navigated to LinkedIn login page")
            
            # Wait and input username using name attribute
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'session_key'))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            logger.info("Username entered")
            
            # Input password using name attribute
            password_field = self.driver.find_element(By.NAME, 'session_password')
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("Password entered")
            
            # Click sign in button using data-litms-control-urn and type
            login_button = self.driver.find_element(
                By.XPATH, '//button[@data-litms-control-urn="login-submit" and @type="submit"]'
            )
            login_button.click()
            logger.info("Sign in button clicked")
            
            # Wait for login to complete or challenge
            WebDriverWait(self.driver, 20).until(
                EC.url_contains('feed') or 
                EC.presence_of_element_located((By.ID, 'challenge'))
            )
            
            # Check if login was successful
            if 'feed' in self.driver.current_url:
                logger.info("Successfully logged in!")
                return True
            else:
                logger.warning("Login may require additional verification")
                return False
        
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def close(self):
        """
        Close browser and end session
        """
        if self.driver:
            self.driver.quit()
        logger.info("Browser session closed")
    
def main():
    # Securely input credentials (consider using environment variables)
    USERNAME = os.getenv('LINKEDIN_USERNAME', 'your_email_or_phone')
    PASSWORD = os.getenv('LINKEDIN_PASSWORD', 'your_password')
    
    bot = None
    try:
        bot = LinkedInBot(USERNAME, PASSWORD)
        login_success = bot.login()
        
        if login_success:
            # Add post-login actions here if needed
            time.sleep(10)  # Example: stay logged in for 10 seconds
        else:
            logger.warning("Login unsuccessful or requires additional verification")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    finally:
        if bot:
            bot.close()

if __name__ == '__main__':
    main()
