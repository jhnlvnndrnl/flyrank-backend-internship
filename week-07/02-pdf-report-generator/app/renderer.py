"""HTML Template and Playwright PDF Renderer."""

import datetime
from typing import Any
from playwright.async_api import async_playwright


def generate_html_report(data: dict[str, Any], title: str = "Sales & Revenue Performance Report") -> str:
    """Generate professional HTML document with print styling and CSS page-break rules."""
    metrics = data.get("metrics", {})
    top_products = data.get("top_products", [])
    daily_trends = data.get("daily_trends", [])
    all_orders = data.get("all_orders", [])
    report_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %d, %Y - %H:%M:%S UTC")

    # Render Top 5 rows
    top_products_rows = "".join(
        f"""
        <tr>
            <td style="font-weight: 600;">{p['product']}</td>
            <td style="text-align: center;">{p['units_sold']}</td>
            <td style="text-align: right;">${p['avg_price']:.2f}</td>
            <td style="text-align: right; font-weight: 600; color: #0f766e;">${p['revenue']:.2f}</td>
        </tr>
        """
        for p in top_products
    )

    # Render Daily trends rows
    daily_rows = "".join(
        f"""
        <tr>
            <td>{d['order_date']}</td>
            <td style="text-align: center;">{d['order_count']}</td>
            <td style="text-align: right; font-weight: 600;">${d['daily_revenue']:.2f}</td>
        </tr>
        """
        for d in daily_trends
    ) if daily_trends else "<tr><td colspan='3' style='text-align: center; color: #64748b;'>No data available for last 7 days</td></tr>"

    # Render Master Orders Table rows (designed to span multiple pages cleanly)
    order_rows = "".join(
        f"""
        <tr>
            <td style="color: #64748b; font-size: 11px;">#{o['id']}</td>
            <td style="white-space: nowrap;">{o['created_at']}</td>
            <td>{o['customer']}</td>
            <td>{o['product']}</td>
            <td style="text-align: right; font-weight: 600;">${o['amount']:.2f}</td>
        </tr>
        """
        for o in all_orders
    )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm 15mm 18mm 15mm;
            @bottom-right {{
                content: counter(page) " / " counter(pages);
                font-size: 10px;
                color: #94a3b8;
            }}
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            background-color: #ffffff;
            font-size: 13px;
            line-height: 1.5;
            padding: 20px;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #0f172a;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}

        .header-title h1 {{
            font-size: 22px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.5px;
        }}

        .header-title p {{
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }}

        .badge {{
            display: inline-block;
            background-color: #f1f5f9;
            color: #0f172a;
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
        }}

        /* Metric Cards Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }}

        .metric-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px 18px;
        }}

        .metric-card .label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
        }}

        .metric-card .value {{
            font-size: 24px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 6px;
        }}

        .section-title {{
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 24px;
            margin-bottom: 12px;
            border-left: 4px solid #0284c7;
            padding-left: 8px;
        }}

        /* Table styles with print page-break management */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
            font-size: 12px;
            page-break-inside: auto;
        }}

        thead {{
            display: table-header-group; /* Repeats table headers on each printed page */
        }}

        tr {{
            break-inside: avoid;
            page-break-inside: avoid; /* Prevents rows from being sliced in half */
        }}

        th {{
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 700;
            text-align: left;
            padding: 10px 12px;
            border-bottom: 1px solid #cbd5e1;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}

        td {{
            padding: 8px 12px;
            border-bottom: 1px solid #f1f5f9;
            color: #334155;
        }}

        tr:nth-child(even) td {{
            background-color: #fafafa;
        }}

        .footer-note {{
            margin-top: 30px;
            padding-top: 14px;
            border-top: 1px solid #e2e8f0;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            <h1>{title}</h1>
            <p>Generated on {report_date}</p>
        </div>
        <div>
            <span class="badge">FlyRank Analytics Engine</span>
        </div>
    </div>

    <!-- Summary KPI Cards -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="label">Total Orders Processed</div>
            <div class="value">{metrics.get('total_orders', 0):,}</div>
        </div>
        <div class="metric-card">
            <div class="label">Total Gross Revenue</div>
            <div class="value" style="color: #0f766e;">${metrics.get('total_revenue', 0.0):,.2f}</div>
        </div>
        <div class="metric-card">
            <div class="label">Average Order Value</div>
            <div class="value">${metrics.get('avg_order_value', 0.0):,.2f}</div>
        </div>
    </div>

    <!-- Top 5 Products -->
    <div class="section-title">Top 5 Products by Gross Revenue</div>
    <table>
        <thead>
            <tr>
                <th>Product Description</th>
                <th style="text-align: center;">Units Sold</th>
                <th style="text-align: right;">Average Unit Price</th>
                <th style="text-align: right;">Gross Revenue</th>
            </tr>
        </thead>
        <tbody>
            {top_products_rows}
        </tbody>
    </table>

    <!-- 7-Day Revenue Trend -->
    <div class="section-title">Daily Order Velocity (Recent Days)</div>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th style="text-align: center;">Order Volume</th>
                <th style="text-align: right;">Day Revenue</th>
            </tr>
        </thead>
        <tbody>
            {daily_rows}
        </tbody>
    </table>

    <!-- Master Transaction Ledger across pages -->
    <div class="section-title">Master Orders Ledger (All {len(all_orders)} Records)</div>
    <table>
        <thead>
            <tr>
                <th>Order ID</th>
                <th>Timestamp</th>
                <th>Customer</th>
                <th>Product</th>
                <th style="text-align: right;">Amount</th>
            </tr>
        </thead>
        <tbody>
            {order_rows}
        </tbody>
    </table>

    <div class="footer-note">
        This document was automatically generated by the FlyRank PDF Report Pipeline. All data is verified from SQLite report.db.
    </div>
</body>
</html>
"""
    return html_content


async def render_pdf_from_data(data: dict[str, Any], output_path: str) -> str:
    """Render HTML to PDF using Playwright headless Chromium."""
    html_content = generate_html_report(data)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "18mm", "left": "15mm", "right": "15mm"},
        )
        await browser.close()

    return output_path
