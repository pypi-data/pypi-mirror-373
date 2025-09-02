-- CTE for prices that fetch prices per product converted to USD
WITH prices AS (
    SELECT
        price.date AS date,
        price.instrument_id AS instrument_id,
        price.net_value AS net_value,
        price.net_value * (1 / fx.value) AS net_value_usd
    FROM wbfdm_instrumentprice AS price
    JOIN currency_currencyfxrates AS fx ON price.currency_fx_rate_to_usd_id = fx.id
    WHERE price.calculated = FALSE
),
-- CTE for claims, that fetches approved claims
claims AS (
    SELECT
        claim.shares,
        claim.date,
        claim.product_id,
        account.tree_id AS tree_id,
        trade.marked_as_internal AS marked_as_internal
    FROM wbportfolio_claim AS claim
    JOIN wbcrm_account AS account
        ON claim.account_id = account.id
    JOIN wbportfolio_trade AS trade
        ON claim.trade_id = trade.id
    WHERE claim.status = 'APPROVED'
),
-- CTE for claims, that fetches them with their shares and price at transaction date
claims_with_nav AS (
    SELECT
        claims.date,
        claims.shares,
        claims.product_id,
        nav.net_value_usd,
        accounts.tree_id AS tree_id,
        trade.marked_as_internal as marked_as_internal
    FROM wbportfolio_claim AS claims
   JOIN wbportfolio_trade AS trade
        ON claims.trade_id = trade.id
    LEFT JOIN wbcrm_account AS accounts
        ON claims.account_id = accounts.id
    LEFT JOIN LATERAL (
        SELECT
            price.net_value * (1 / cc.value) AS net_value_usd
        FROM wbfdm_instrumentprice AS price
        LEFT JOIN currency_currencyfxrates AS cc
            ON cc.id = price.currency_fx_rate_to_usd_id
        WHERE
            price.instrument_id = claims.product_id
            AND price.date <= claims.date
            AND claims.status = 'APPROVED'
            AND claims.account_id IS NOT NULL
            AND price.calculated = FALSE
        ORDER BY price.date DESC
        LIMIT 1
    ) AS nav ON TRUE
-- CTE to generate a series with year and month already extracted
), series AS (
    SELECT
        (DATE_TRUNC('month', dts) + INTERVAL '1 month - 1 day')::DATE AS val_date,
        EXTRACT(YEAR FROM dts) AS year,
        EXTRACT(MONTH FROM dts) AS month
    FROM GENERATE_SERIES('{{ from_date | identifier }}'::DATE, '{{ to_date | identifier }}'::DATE, '1 month'::INTERVAL) AS dts
)

SELECT
    series.year AS year,
    series.month AS month,
    SUM(NAV.net_value_usd * HOLDINGS.sum_shares) AS total_assets,
    SUM(COALESCE(NNM.nnm_usd, 0)) AS net_new_money

FROM series
-- Cartesian product with products, to get each item of the series
-- for each product
CROSS JOIN wbportfolio_product AS product

-- If there is not product_id it means we filter for all products
-- This means we have to filter out all products that are not
-- invested to avoid double accounting

-- Foreach product/date combination, get the last NAV date available
LEFT JOIN LATERAL (
    SELECT prices.net_value_usd
    FROM prices
    WHERE
        prices.date <= series.val_date
        AND prices.instrument_id = product.instrument_ptr_id
    ORDER BY prices.date DESC
    LIMIT 1
) AS NAV ON TRUE
-- For each product/date combination, get the number of shares
LEFT JOIN LATERAL (
    SELECT SUM(claims.shares) AS sum_shares
    FROM claims
    WHERE claims.date <= series.val_date
      AND claims.product_id = product.instrument_ptr_id
      {% if account_tree_id %}AND claims.tree_id={{ account_tree_id }}{% endif %}
      {% if not product_id %}AND claims.marked_as_internal=False{% endif %}
) AS HOLDINGS ON TRUE
-- For each product/date combination, get the NNM
LEFT JOIN LATERAL (
    -- Get the number of shares that were created in the month of date (from the series)
    SELECT
        SUM(claims.shares * claims.net_value_usd) AS nnm_usd,
        SUM(claims.shares) as shares
    FROM claims_with_nav as claims
    WHERE
        EXTRACT(YEAR FROM claims.date) = series.year
        AND EXTRACT(MONTH FROM claims.date) = series.month
        AND claims.product_id = product.instrument_ptr_id
        {% if account_tree_id %}AND claims.tree_id={{ account_tree_id }}{% endif %}
        {% if not product_id %}AND claims.marked_as_internal=False{% endif %}
    ) AS NNM ON TRUE

-- if we pass in the product_id, we only display the data for this particular product
{% if product_id %}
WHERE product.instrument_ptr_id = {{ product_id }}
{% endif %}

GROUP BY series.year, series.month
