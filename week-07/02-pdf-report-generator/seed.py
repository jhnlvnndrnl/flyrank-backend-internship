"""Database Seed Script for Orders Data."""

import datetime
import random
from app.database import get_connection, init_db
from app.config import DATABASE_PATH

PRODUCTS = [
    ("Mechanical Keyboard", 119.99),
    ("Ergonomic Mouse", 49.50),
    ("4K Ultra HD Monitor", 289.00),
    ("USB-C Multiport Hub", 39.99),
    ("Noise-Cancelling Headphones", 149.00),
    ("Standing Desk Mat", 55.00),
]

CUSTOMERS = [
    "Alice Johnson", "Bob Smith", "Charlie Davis", "Diana Prince", "Ethan Hunt",
    "Fiona Gallagher", "George Clark", "Hannah Abbott", "Ian Malcolm", "Julia Roberts",
    "Kevin Flynn", "Laura Croft", "Michael Scott", "Nina Simone", "Oliver Queen",
    "Peter Parker", "Quinn Fabray", "Rachel Green", "Steve Rogers", "Tony Stark"
]


def seed_database(db_path: str = DATABASE_PATH, target_count: int = 200) -> int:
    """Seed the database with target_count sample orders. Safe to run repeatedly."""
    init_db(db_path)

    # Deterministic pseudo-random seed for reproducible development data
    rng = random.Random(42)
    now = datetime.datetime.now(datetime.timezone.utc)

    orders_to_insert = []
    for _ in range(target_count):
        customer = rng.choice(CUSTOMERS)
        product_name, base_price = rng.choice(PRODUCTS)
        # Small price variance (±10%)
        amount = round(base_price * rng.uniform(0.9, 1.1), 2)
        days_ago = rng.randint(0, 29)
        hours_ago = rng.randint(0, 23)
        minutes_ago = rng.randint(0, 59)
        order_date = (now - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")

        orders_to_insert.append((customer, product_name, amount, order_date))

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Clean before insert (Idempotent seed rule)
        cursor.execute("DELETE FROM orders;")
        cursor.executemany(
            """
            INSERT INTO orders (customer, product, amount, created_at)
            VALUES (?, ?, ?, ?);
            """,
            orders_to_insert,
        )
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM orders;")
        count = cursor.fetchone()[0]

    print(f"Successfully seeded {count} orders in {db_path}")
    return count


if __name__ == "__main__":
    seed_database()
