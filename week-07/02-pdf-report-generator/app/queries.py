"""SQL Aggregation and Reporting Queries."""

from typing import Any
from .database import get_connection
from .config import DATABASE_PATH


def get_report_data(db_path: str = DATABASE_PATH) -> dict[str, Any]:
    """
    Execute SQL aggregations on orders dataset to build report data object.
    Includes totals, top products, daily breakdowns, and full order records.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Total Orders & Total Revenue
        cursor.execute("SELECT COUNT(*) AS total_orders, COALESCE(SUM(amount), 0.0) AS total_revenue, COALESCE(AVG(amount), 0.0) AS avg_order_value FROM orders;")
        totals_row = cursor.fetchone()
        total_orders = totals_row["total_orders"]
        total_revenue = round(totals_row["total_revenue"], 2)
        avg_order_value = round(totals_row["avg_order_value"], 2)

        # 2. Top 5 Products by Revenue
        cursor.execute(
            """
            SELECT 
                product,
                COUNT(*) AS units_sold,
                ROUND(SUM(amount), 2) AS revenue,
                ROUND(AVG(amount), 2) AS avg_price
            FROM orders
            GROUP BY product
            ORDER BY revenue DESC
            LIMIT 5;
            """
        )
        top_products = [dict(row) for row in cursor.fetchall()]

        # 3. Orders per Day (Last 7 Days)
        cursor.execute(
            """
            SELECT 
                date(created_at) AS order_date,
                COUNT(*) AS order_count,
                ROUND(SUM(amount), 2) AS daily_revenue
            FROM orders
            WHERE created_at >= date('now', '-7 days')
            GROUP BY date(created_at)
            ORDER BY order_date ASC;
            """
        )
        daily_trends = [dict(row) for row in cursor.fetchall()]

        # 4. Full Orders (for the comprehensive document ledger across pages)
        cursor.execute(
            """
            SELECT id, customer, product, amount, created_at
            FROM orders
            ORDER BY created_at DESC;
            """
        )
        all_orders = [dict(row) for row in cursor.fetchall()]

    return {
        "metrics": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
        },
        "top_products": top_products,
        "daily_trends": daily_trends,
        "all_orders": all_orders,
    }
