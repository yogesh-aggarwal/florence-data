import random
import time

from faker import Faker
from pymongo import MongoClient
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SOURCE_URLS = [
    # "https://www.fnp.com/carnations-lp",
    # "https://www.fnp.com/flowers/birthday-lp",
    # "https://www.fnp.com/flowers/love-n-romance-lp",
    # "https://www.fnp.com/flowers/anniversary-lp",
    # "https://www.fnp.com/flowers/congratulations-lp",
    # "https://www.fnp.com/flowers/sympathy-n-funeral-lp",
]


connectionString = "mongodb://localhost:27017"
client = MongoClient(connectionString)
db = client["florence"]

allCollections = db.list_collection_names()
if "products" not in allCollections:
    db.create_collection("products")

options = ChromeOptions()
options.headless = True
options.add_argument("--disable-gpu")
driver = Chrome("./chromedriver.exe", options=options)


for sourceURL in SOURCE_URLS:
    print(f"\n\n\n=== [{sourceURL}] ===\n\n\n")
    driver.get(sourceURL)

    grid = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="d-plp"]/div[1]/section/div[2]/div/div[1]/div')
        )
    )

    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(20):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    products = grid.find_elements(By.CLASS_NAME, "products")

    urls = []
    for product in products:
        try:
            urls.append(product.find_element(By.TAG_NAME, "a").get_attribute("href"))
        except:
            pass

    fake = Faker()

    for i, url in enumerate(urls):
        try:
            print(f"✅ [{i+1}/{len(urls)}] {url}")
            driver.get(url)
            title = driver.find_element(By.ID, "product-title").text
            price = driver.find_element(By.ID, "odometer").text.replace(",", "")
            infoSections = (
                driver.find_element(By.ID, "product-description")
                .find_element(By.TAG_NAME, "div")
                .find_elements(By.TAG_NAME, "div")
            )
            sections = {}
            for section in infoSections:
                try:
                    heading = section.find_element(By.TAG_NAME, "h4").text
                    sections[heading] = []
                    for i, item in enumerate(
                        section.find_elements(By.XPATH, "./*")
                    ):
                        if item.tag_name == "p":
                            sections[heading].append(
                                {"type": "para", "content": item.text}
                            )
                        elif item.tag_name == "ul":
                            listItems = map(
                                lambda x: x.text,
                                item.find_elements(By.TAG_NAME, "li"),
                            )
                            sections[heading].append(
                                {"type": "list", "content": list(listItems)}
                            )
                except:
                    pass
            imagesLen = len(
                driver.find_element(By.CLASS_NAME, "slick-track").find_elements(
                    By.CLASS_NAME, "slick-slide"
                )
            )
            images = []
            for i in range(imagesLen):
                try:
                    imageURL = driver.find_element(
                        By.ID, f"thumbnail_{i+1}"
                    ).get_attribute("src")
                    if imageURL.startswith("https"):
                        images.append(imageURL)
                except:
                    pass

            productData = {
                "title": title,
                "price": int(price),
                "images": images,
                "description": sections["Description"],
                "deliveryInfo": sections["Delivery Information"],
                "careInstructions": sections["Care Instructions"],
                "discountInPercent": random.randint(0, 50),
                "stock": random.randint(100, 500),
                "deliveryCharges": random.randint(30, 50),
                "starRatings": random.randint(0, 5),
            }
            productData["reviews"] = []
            for j in range(0, 8):
                productData["reviews"].append(
                    {
                        "id": fake.uuid4(),
                        "userID": "",
                        "starsGiven": random.randint(0, 5),
                        "review": fake.text(100),
                        "whenReviewed": str(
                            fake.date_between(start_date="-3y", end_date="-1y")
                        ),
                    }
                )
            db["products"].insert_one(productData)
        except:
            print(f"❌ [{i+1}/{len(urls)}] {url}")

