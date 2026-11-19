# Retail Analytics

Analyse des ventes d'un vrai e-commerçant, de la donnée brute aux décisions :
nettoyage justifié ligne à ligne, SQL analytique, segmentation des clients,
rétention par cohorte, analyse de panier, puis restitution lisible par
quelqu'un qui n'a jamais ouvert un tableur.

Les résultats sont publiés sur [falakion.com/da](https://falakion.com/fr/da).

![Architecture](docs/architecture.svg)

Le document complet est dans [docs/retail-analytics.pdf](docs/retail-analytics.pdf).

## Les données

[Online Retail II](https://doi.org/10.24432/C5CG6D) (UCI Machine Learning
Repository, licence CC BY 4.0) : 1 067 371 lignes de facture d'un
e-commerçant britannique d'objets de décoration et de cadeaux, de décembre 2009
à décembre 2011, avec ses clients particuliers et grossistes de 43 pays.

C'est un jeu réel, donc sale : doublons, factures d'annulation, frais de port
mêlés aux articles, prix nuls, clients non identifiés.

## Ce qui en sort

| Indicateur | Valeur |
|---|---|
| Chiffre d'affaires analysé | 19,6 M£ sur 39 516 commandes |
| Panier moyen | 497 £ |
| Clients identifiés | 5 852 |
| Taux de retour (en valeur) | 7,4 % |

- **Saisonnalité** : de septembre à décembre, l'activité concentre 44 % du
  chiffre d'affaires de 2010 ; novembre en pèse 15 % à lui seul.
- **Concentration** : 21 % des références font 80 % des ventes.
- **Clients** : les « champions » (achats récents et fréquents) sont 24 % des
  clients et 68 % du chiffre d'affaires.
- **Fidélisation** : en moyenne, 20 % des nouveaux clients reviennent le mois
  suivant leur premier achat.
- **Paniers** : les variantes de couleur d'un même article s'achètent ensemble,
  jusqu'à 137 fois plus souvent que le hasard. Il y a là une offre « lot ».

Les phrases ci-dessus sont produites par le code à partir des chiffres
(`export.py`), pas écrites à la main : si les règles de nettoyage changent, le
texte suit.

## Nettoyage

| Règle | Lignes retirées |
|---|---|
| doublons exacts | 34 335 |
| factures d'annulation (gardées à part comme retours) | 19 104 |
| frais de port, ajustements, opérations hors catalogue | 4 790 |
| quantité ou prix nul ou négatif | 5 928 |
| **lignes de vente retenues** | **1 003 214** |

## Démarrage

```bash
pip install -e .
retail download        # 45 Mo, converti une fois en Parquet
retail build           # nettoyage, analyses, export JSON et rapport HTML
```

`export/retail.json` est ce que consomme la page web ; `reports/rapport.html`
est un rapport Plotly autonome. Pour explorer :

```bash
pip install -e ".[dashboard]"
streamlit run app/dashboard.py
```

## Analyses

Chaque analyse est une requête SQL lisible dans `src/retail/sql/`, exécutée
par DuckDB directement sur les données en mémoire.

| Fichier | Question |
|---|---|
| `kpis.sql` | combien, et pour qui ? |
| `monthly.sql` | comment l'activité évolue-t-elle dans l'année ? |
| `countries.sql` | d'où viennent les ventes ? |
| `cohorts.sql` | les nouveaux clients reviennent-ils ? |
| `rfm.sql` | quels clients soigner, relancer, laisser partir ? |
| `products.sql` | quelles références portent le chiffre d'affaires ? |
| `heatmap.sql` | quand les commandes arrivent-elles ? |
| `basket.sql` | quels articles s'achètent ensemble ? |

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Les tests tournent sur un petit jeu construit à la main dont on connaît les
réponses : nombre de lignes retirées par règle, matrice de rétention, lift
d'une paire d'articles.

## Licence

Code sous licence MIT. Données : Chen, D. (2019), Online Retail II, UCI
Machine Learning Repository, CC BY 4.0.
