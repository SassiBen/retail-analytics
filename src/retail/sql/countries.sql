SELECT
    country,
    SUM(revenue)                  AS revenue,
    COUNT(DISTINCT invoice)       AS orders,
    COUNT(DISTINCT customer_id)   AS customers
FROM sales
GROUP BY country
ORDER BY revenue DESC;
