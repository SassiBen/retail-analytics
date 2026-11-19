SELECT
    SUM(revenue)                              AS revenue,
    COUNT(DISTINCT invoice)                   AS orders,
    COUNT(DISTINCT customer_id)               AS customers,
    SUM(revenue) / COUNT(DISTINCT invoice)    AS avg_order_value,
    COUNT(DISTINCT stock_code)                AS products,
    COUNT(DISTINCT country)                   AS countries,
    MIN(invoice_date)                         AS first_date,
    MAX(invoice_date)                         AS last_date
FROM sales;
