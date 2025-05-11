import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Define product categories and sample products
categories = {
    'Baby Gear': ['Walker', 'Stroller', 'Car Seat'],
    'Furniture': ['Cradle', 'High Chair', 'Study Table'],
    'Battery Operated': ['Car', 'Bike', 'Jeep'],
    'Baby Safety': ['Safety Gate', 'Bed Rail'],
    'Toys': ['Scooter', 'Ride-on']
}

# Generate synthetic reviews
data = []
for i in range(10000):
    category = random.choice(list(categories.keys()))
    product = random.choice(categories[category])
    product_id = f"{category[:2].upper()}_{i:05d}"
    review_text = fake.sentence(nb_words=20)
    review_date = fake.date_between(start_date='-1y', end_date='today')
    rating = random.randint(1, 5)
    data.append([product_id, product, category, review_text, review_date, rating])

# Create DataFrame
df = pd.DataFrame(data, columns=['Product_ID', 'Product_Name', 'Category', 'Review_Text', 'Review_Date', 'Rating'])

# Save to Excel
df.to_excel('synthetic_reviews.xlsx', index=False)


