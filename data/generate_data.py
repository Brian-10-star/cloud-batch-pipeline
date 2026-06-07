import logging
import pandas as pd
import numpy as np
import os
from faker import Faker
from datetime import datetime, timedelta
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

fake = Faker()
random.seed(42)
np.random.seed(42)

KENYAN_COUNTIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
    "Thika", "Malindi", "Kitale", "Garissa", "Nyeri",
    "Machakos", "Meru", "Embu", "Kericho", "Bomet",
    "Kakamega", "Bungoma", "Siaya", "Homa Bay", "Migori",
    "Kisii", "Nyamira", "Narok", "Kajiado", "Muranga",
    "Kirinyaga", "Nyandarua", "Laikipia", "Samburu", "Trans Nzoia",
    "Uasin Gishu", "Elgeyo Marakwet", "Nandi", "Baringo", "Turkana",
    "West Pokot", "Isiolo", "Marsabit", "Mandera", "Wajir",
    "Tana River", "Lamu", "Taita Taveta", "Kwale", "Kilifi",
    "Vihiga", "Busia", "Makueni", "Kitui", "Tharaka Nithi"
]

PRODUCT_CATEGORIES = [
    "Electronics", "Clothing", "Food & Beverage", "Household",
    "Mobile Phones", "Furniture", "Cosmetics", "Stationery"
]

SHOP_NAMES = [
    "Naivas Supermarket", "Quickmart", "Carrefour Kenya", "Tuskys",
    "Chandarana Foodplus", "Eastmatt", "Mulleys Supermarket", "Game Stores",
    "Uchumi Supermarket", "Shoprite Kenya", "Cleanshelf Supermarket", "Mathai Supermarket",
    "Mega Supermarket", "Tumaini Supermarket", "Ebrahim Stores", "Kamakis Supermarket",
    "Jumia Kenya", "Kilimall", "Masoko by Safaricom", "Copia Kenya",
    "Hotpoint Appliances", "Furniture Palace", "Deacons Kenya", "Mr. Price Kenya",
    "Woolworths Kenya", "LC Waikiki", "Bata Kenya", "Shoe Express",
    "Healthy U Pharmacy", "Goodlife Pharmacy", "Haltons Pharmacy", "Portal Pharmacy",
    "Zucchini Greengrocers", "Maasai Market", "Gikomba Market", "Toi Market",
    "Nakumatt", "Agip Convenience Store", "Total Energies Shop", "Shell Select"
]

PAYMENT_METHODS = ["M-Pesa", "Cash", "Card", "Bank Transfer"]


def generate_month_data(year, month, num_rows=500):
    records = []

    for _ in range(num_rows):
        day = random.randint(1, 28)
        hour = random.randint(7, 21)
        minute = random.randint(0, 59)
        transaction_date = datetime(year, month, day, hour, minute)

        amount = round(random.uniform(50, 150000), 2)
        quantity = random.randint(1, 20)
        unit_price = round(amount / quantity, 2)

        payment_method = random.choice(PAYMENT_METHODS)
        mpesa_ref = f"MP{random.randint(10000000, 99999999)}" if payment_method == "M-Pesa" else None

        record = {
            "transaction_id": f"TXN-{year}{month:02d}-{random.randint(100000, 999999)}",
            "transaction_date": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "shop_name": random.choice(SHOP_NAMES),
            "county": random.choice(KENYAN_COUNTIES),
            "product_category": random.choice(PRODUCT_CATEGORIES),
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": amount,
            "payment_method": payment_method,
            "mpesa_ref": mpesa_ref,
            "customer_phone": f"07{random.randint(10000000, 99999999)}",
        }
        records.append(record)

    return pd.DataFrame(records)


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))

    months = [(2026, 1), (2026, 2), (2026, 3)]

    for year, month in months:
        df = generate_month_data(year, month)
        filename = f"sales_{year}_{month:02d}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Generated {filename} with {len(df)} rows")


if __name__ == "__main__":
    main()