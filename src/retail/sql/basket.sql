-- Paires d'articles achetés ensemble, classées par lift : combien de fois plus
-- souvent ils sont dans le même panier que si les achats étaient indépendants.
WITH baskets AS (
    SELECT invoice
    FROM sales
    GROUP BY invoice
    -- Les très gros paniers sont des commandes de grossistes : ils associent
    -- tout avec tout et noient les vraies affinités.
    HAVING COUNT(DISTINCT stock_code) BETWEEN 2 AND 60
),
lines AS (
    SELECT DISTINCT invoice, stock_code
    FROM sales
    WHERE invoice IN (SELECT invoice FROM baskets)
),
singles AS (
    SELECT stock_code, COUNT(*) AS baskets
    FROM lines
    GROUP BY stock_code
    HAVING COUNT(*) >= $min_together
),
kept AS (
    SELECT l.* FROM lines l JOIN singles USING (stock_code)
),
pairs AS (
    SELECT a.stock_code AS a, b.stock_code AS b, COUNT(*) AS together
    FROM kept a
    JOIN kept b ON a.invoice = b.invoice AND a.stock_code < b.stock_code
    GROUP BY ALL
    HAVING COUNT(*) >= $min_together
),
total AS (SELECT COUNT(*) AS n FROM baskets)
SELECT
    p.a,
    p.b,
    p.together,
    CAST(p.together AS DOUBLE) / total.n                          AS support,
    CAST(p.together AS DOUBLE) / sa.baskets                        AS confidence,
    CAST(p.together AS DOUBLE) * total.n / (sa.baskets * sb.baskets) AS lift
FROM pairs p
CROSS JOIN total
JOIN singles sa ON sa.stock_code = p.a
JOIN singles sb ON sb.stock_code = p.b
ORDER BY lift DESC
LIMIT $limit;
