from pymongo import MongoClient
import random
from bson.objectid import ObjectId

connectionString = "mongodb://localhost:27017"
client = MongoClient(connectionString)
db = client["florence"]

productsColl = db["products"]

allProducts = productsColl.find({})

allCategories = [
    "birthday",
    "sympathy",
    "romance",
    "anniversary",
    "celebration",
]
for product in allProducts:
    categories = set()
    for i in range(random.randint(3, 10)):
        categories.add(random.choice(allCategories))
    images = []
    for image in product["images"]:
        images.append(
            image.replace(
                "https://www.fnp.com/images/pr/s", "https://www.fnp.com/images/pr/x"
            )
        )
    productsColl.update_one(
        {"_id": ObjectId(product["_id"])},
        {"$set": {"categories": list(categories), "images": images}},
    )
