CREATE VIEW sales_summary AS
SELECT 
    o.order_id,
    SUM(o.total_amount) AS total_sales,
    COUNT(o.order_id) AS total_orders,
    MAX(o.order_date) AS last_order_date
FROM 
    orders o
GROUP BY 
    o.order_id;