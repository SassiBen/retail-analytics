SELECT
    strftime(date_trunc('month', invoice_date), '%Y-%m')  AS month,
    SUM(revenue)                                           AS revenue,
    COUNT(DISTINCT invoice)                                AS orders,
    COUNT(DISTINCT customer_id)                            AS customers
FROM sales
GROUP BY 1
ORDER BY 1;
