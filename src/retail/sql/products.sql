SELECT
    stock_code,
    mode(description)   AS description,
    SUM(revenue)        AS revenue,
    SUM(quantity)       AS quantity,
    COUNT(DISTINCT invoice) AS orders
FROM sales
GROUP BY stock_code
ORDER BY revenue DESC;
