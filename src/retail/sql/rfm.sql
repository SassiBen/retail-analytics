-- Segmentation RFM : récence, fréquence, montant, notés de 1 à 5.
--
-- La note vient du rang centile (percent_rank) et non de NTILE : NTILE coupe la
-- population en cinq parts égales et répartit arbitrairement les ex-aequo entre
-- deux parts. Ici, un tiers des clients n'a passé qu'une commande ; avec NTILE,
-- deux exécutions donnaient des segments différents. Avec percent_rank, deux
-- clients identiques reçoivent toujours la même note.
WITH ref AS (
    SELECT CAST(MAX(invoice_date) AS DATE) + 1 AS day FROM sales
),
customers AS (
    SELECT
        customer_id,
        date_diff('day', CAST(MAX(invoice_date) AS DATE), (SELECT day FROM ref)) AS recency,
        COUNT(DISTINCT invoice)   AS frequency,
        SUM(revenue)              AS monetary
    FROM sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
scored AS (
    SELECT
        *,
        LEAST(5, 1 + FLOOR(5 * PERCENT_RANK() OVER (ORDER BY recency DESC)))::INTEGER AS r,
        LEAST(5, 1 + FLOOR(5 * PERCENT_RANK() OVER (ORDER BY frequency)))::INTEGER    AS f,
        LEAST(5, 1 + FLOOR(5 * PERCENT_RANK() OVER (ORDER BY monetary)))::INTEGER     AS m
    FROM customers
)
SELECT
    *,
    CASE
        WHEN r >= 4 AND f >= 4 THEN 'champions'
        WHEN r >= 3 AND f >= 3 THEN 'fideles'
        WHEN r >= 4 AND f <= 2 THEN 'nouveaux'
        WHEN r <= 2 AND f >= 3 THEN 'a_risque'
        WHEN r <= 2 AND f <= 2 THEN 'endormis'
        ELSE 'a_relancer'
    END AS segment
FROM scored;
