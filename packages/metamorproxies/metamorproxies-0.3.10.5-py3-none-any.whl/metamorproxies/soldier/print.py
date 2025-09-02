from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
from kitano import puts
class PrintWeb:
    """
    A class to take a screenshot of a given website.
    """
    hight = 800
    width = 1200
    service = None
    
    def __init__(self, url, output_path="screenshot.png"):
        """
        Initializes the PrintWeb instance.

        Args:
            url (str): The URL of the website to capture.
            output_path (str, optional): The path where the screenshot will be saved. Defaults to "screenshot.png".
        """
        self.url = url
        self.output_path = output_path
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.options = options
        puts(f"Initialized PrintWeb with URL: {self.url} and output path: {self.output_path}")
    
    def set_path(self, output_path):
        """
        Updates the output path for saving the screenshot.

        Args:
            output_path (str): The new file path where the screenshot should be saved.
        """
        self.output_path = output_path
    
    def set_window_size(self, width, height):
        """
        Sets the window size for the screenshot.

        Args:
            width (int): The width of the window.
            height (int): The height of the window.
        """
        self.width = width
        self.hight = height
        puts(f"Window size set to {self.width}x{self.hight}")
    
    def add_argument(self, argument):
        """
        Adds an argument to the Chrome options.

        Args:
            argument (str): The argument to add to the Chrome options.
        """
        self.options.add_argument(argument)
        puts(f"Added argument: '{argument}' to Chrome options")
    
    
    def set_service(self, service):
        """
        Sets a custom service for the Chrome WebDriver.

        Args:
            service (str or Service): The path to the ChromeDriver executable or a Service instance.
        """
        if isinstance(service, str):
            service = Service(service)
        self.service = service
        puts(f"Custom service set: {self.service.path if hasattr(self.service, 'path') else 'No path available'}")
    
    
    def setup_driver(self,service=None):
        """
        Configura e retorna uma instância do Chrome WebDriver em modo headless.
        """
        
        # Cria um diretório temporário exclusivo para o user-data-dir
        temp_dir = tempfile.mkdtemp()
        options = self.options
        options.add_argument(f"--user-data-dir={temp_dir}")
        options.add_argument(f"--window-size={self.width},{self.hight}")
        
        if service:
            if isinstance(service, str):
                service = Service(service)
            puts(f"Using custom service path: {service.path}")
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        puts("Using ChromeDriverManager to install the driver")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver


    def take_screenshot(self):
        """
        Captures a screenshot of the specified website and saves it as a PNG file.
        """
        if not self.service:
            puts("No service specified, using default ChromeDriverManager")
            self.service = Service(ChromeDriverManager().install())
        else:
            puts(f"Using custom service: {self.service.path if hasattr(self.service, 'path') else 'No path available'}")
        driver = self.setup_driver(service=self.service)
        driver.get(self.url)
        driver.save_screenshot(self.output_path)
        driver.quit()
        print(f"Screenshot site saved as {self.output_path}")


    def kill_driver(self):
        """
        Kills the Chrome WebDriver process.
        """
        if self.driver:
            self.driver.quit()
            puts("Chrome WebDriver process killed")

# Example usage
