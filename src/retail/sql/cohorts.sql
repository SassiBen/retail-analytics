-- Rétention mensuelle par cohorte : un client appartient à la cohorte du mois
-- de son premier achat, puis on compte, mois après mois, qui revient.
WITH firsts AS (
    SELECT customer_id, date_trunc('month', MIN(invoice_date)) AS cohort
    FROM sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT
        s.customer_id,
        f.cohort,
        date_diff('month', f.cohort, date_trunc('month', s.invoice_date)) AS month_offset
    FROM sales s
    JOIN firsts f USING (customer_id)
)
SELECT
    strftime(cohort, '%Y-%m')   AS cohort,
    month_offset,
    COUNT(*)                    AS customers
FROM activity
GROUP BY ALL
ORDER BY cohort, month_offset;
