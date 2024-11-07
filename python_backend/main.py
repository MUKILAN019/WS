from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re

app = FastAPI()

# Allow requests from the frontend running at localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLData(BaseModel):
    url: str

@app.post("/scrape")
async def scrape_amazon(url_data: URLData):
    try:
        # Set up the WebDriver and ChromeDriver path
        service = Service("C:/Users/pavil/OneDrive/Documents/chromedriver-win64/chromedriver.exe")  # Replace with your ChromeDriver path
        driver = webdriver.Chrome(service=service)

        # Load the provided URL
        driver.get(url_data.url)
        time.sleep(7)

        # Scroll down to load more elements
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Get page content
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Define selectors and regex for handling variable title classes
        title_classes = ["a-size-medium a-color-base a-text-normal", 
                         "a-size-base-plus a-color-base a-text-normal"]
        title_pattern = re.compile(r'a-size-\w+-plus a-color-base a-text-normal')

        selectors = {
            "Rate": {"ele": "span", "class": "a-icon-alt"},
            "Symbol": {"ele": "span", "class": 'a-price-symbol'},
            "Price": {"ele": "span", "class": "a-price-whole"}
        }

        # Extract data
        titles, rates, prices = [], [], []
        for item in soup.find_all("div", {"data-component-type": "s-search-result"}):
            # Try each title class from the list
            title = None
            for cls in title_classes:
                title = item.find("span", class_=cls)
                if title:
                    break
            # Use regex if no title was found
            if not title:
                title = item.find("span", class_=title_pattern)

            rate = item.find(selectors["Rate"]["ele"], class_=selectors["Rate"]["class"])
            symbol = item.find(selectors["Symbol"]["ele"], class_=selectors["Symbol"]["class"])
            price = item.find(selectors["Price"]["ele"], class_=selectors["Price"]["class"])
            full_price = (symbol.get_text(strip=True) if symbol else "") + (price.get_text(strip=True) if price else "N/A")
            
            titles.append(title.get_text(strip=True) if title else "N/A")
            rates.append(rate.get_text(strip=True) if rate else "N/A")
            prices.append(full_price)

        # Close the WebDriver
        driver.quit()

        # Define file path within the python_backend directory
        file_path = os.path.join(os.path.dirname(__file__), "scraped_data.xlsx")

        # Create a DataFrame and save it as an Excel file
        df = pd.DataFrame({"Title": titles, "Rate": rates, "Price": prices})
        df.to_excel(file_path, index=False)

        # Serve the file as a response
        return FileResponse(path=file_path, filename="scraped_data.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
