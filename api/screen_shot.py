from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api


# Cloudinary Configuration
# IMPORTANT: Set these environment variables in your system before running the script:
# export CLOUDINARY_CLOUD_NAME="your_cloud_name"
# export CLOUDINARY_API_KEY="your_api_key"
# export CLOUDINARY_API_SECRET="your_api_secret"
cloudinary.config(
    cloud_name="dhgwksjv7",
    api_key="291716115323572",
    api_secret="JFFhaohKmFTqAtZqa2GqRv-i-pU",
    secure=True  # Ensures HTTPS URLs are returned
)


def take_screenshot(chart_url):
    cloudinary_urls = []  # Initialize list to store Cloudinary URLs
    # Extract symbol name from URL
    symbol_name = chart_url.split('symbol=')[-1].split('&')[0].replace('%3A', '_')
    # Define different timeframes
    timeframes = {
        'hourly': '1H',
        'daily': '1D',
        'weekly': '1W',
        'monthly': '1M',
    }

    # Function to take screenshots for different timeframes
    def capture_chart_timeframes(base_url, timeframes):
        screenshots = []
        
        for name, interval in timeframes.items():
            # Append timeframe parameter to URL
            timeframe_url = f"{base_url}&interval={interval}"
            print(f"Capturing {name} chart from: {timeframe_url}")
            screenshots.append((name, timeframe_url))
        
        return screenshots

    # Prepare URLs for different timeframes
    chart_screenshots = capture_chart_timeframes(chart_url, timeframes)

    # Set up Chrome options
    options = Options()
    # Run in headless mode (no visible browser window)
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280,800')

    # Import time at the top level
    import time

    # Initialize the Chrome driver with options
    driver = webdriver.Chrome(options=options)

    # Ensure ScreenShot directory exists
    screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ScreenShot')
    os.makedirs(screenshot_dir, exist_ok=True)

    # Loop through each timeframe and take screenshots
    for name, url in chart_screenshots:
        print(f"Loading: {url}")
        driver.get(url)
        
        # Wait for the chart to load (increase sleep if needed)
        time.sleep(10)  # Increased to ensure chart loads completely
        
        # Take screenshot with symbol name and timeframe
        screenshot_file = os.path.join(screenshot_dir, f'{symbol_name}_{name}.png')
        driver.save_screenshot(screenshot_file)
        print(f"Screenshot saved: {screenshot_file}")
        try:
                # Construct a unique public_id for Cloudinary
                # This helps in organizing and managing images in your Cloudinary account
                cloudinary_public_id = f"mcp_screenshots/{symbol_name}_{name}"
                
                upload_response = cloudinary.uploader.upload(
                    screenshot_file,
                    public_id=cloudinary_public_id,
                    overwrite=True  # Overwrites if an image with the same public_id already exists
                )
                uploaded_url = upload_response.get('secure_url')
                if uploaded_url:
                    print(f"Uploaded to Cloudinary: {uploaded_url}")
                    cloudinary_urls.append(uploaded_url)
                else:
                    print("Uploaded to Cloudinary, but URL not available in response.")
        except Exception as e:
            print(f"Cloudinary upload failed for {screenshot_file}: {e}")

    # Close the browser when done
    driver.quit()
    print("All screenshots captured successfully!")
    return cloudinary_urls
