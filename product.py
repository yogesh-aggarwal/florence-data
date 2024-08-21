from pymongo import MongoClient
from faker import Faker
import random

# database connection
connectionString = "mongodb://localhost:27017"
client = MongoClient(connectionString)
db = client["florence"]

# create collection if not created.
allCollections = db.list_collection_names()

# collectionFound = False
# for collection in allCollections:
#     if (collection == "products"):
#         collectionFound = True

# if not collectionFound:
#     db.create_collection("products")

if "products" not in allCollections:
    db.create_collection("products")


def generateFlowerName():
    # List of possible flower name prefixes
    prefixes = ["sun", "moon", "star", "sky", "ocean", "forest", "river", "mountain"]
    # List of possible flower name suffixes
    suffixes = ["bloom", "petal", "blossom", "flower", "bud", "bloomer"]

    return (
        random.choice(prefixes).capitalize()
        + " "
        + random.choice(suffixes).capitalize()
    )


# generating fake description using faker
fake = Faker()

products = []
for i in range(0, 100):
    product = {}
    product["id"] = fake.uuid4()
    product["title"] = generateFlowerName()
    product["description"] = fake.text(1000)
    product["price"] = random.randint(300, 500)
    product["deliveryCharges"] = random.randint(30, 50)
    product["stock"] = random.randint(100, 500)
    product["discountInPercent"] = random.randint(0, 50)
    product["images"] = []
    for k in range(0, 4):
        product["images"].append("Image_" + str(random.randint(1, 924)) + ".jpg")
    product["starRatings"] = random.randint(0, 5)
    product["reviews"] = []
    for j in range(0, 8):
        product["reviews"].append(
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
    products.append(product)

# inserting data in database
print("✅ Generated products")
db["products"].insert_many(products)
print("✅ Stored products in database")
