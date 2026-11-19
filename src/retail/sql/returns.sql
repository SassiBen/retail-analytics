SELECT
    -SUM(revenue)              AS returned_value,
    COUNT(DISTINCT invoice)    AS credit_notes
FROM returns;
