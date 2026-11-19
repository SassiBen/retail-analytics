SELECT
    isodow(invoice_date)      AS weekday,
    hour(invoice_date)        AS hour,
    COUNT(DISTINCT invoice)   AS orders
FROM sales
GROUP BY ALL
ORDER BY ALL;
