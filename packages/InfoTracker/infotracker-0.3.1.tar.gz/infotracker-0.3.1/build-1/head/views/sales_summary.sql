SELECT 
    o.order_id,
    c.customer_name,
    SUM(o.total_amount) AS total_sales,
    COUNT(o.order_id) AS total_orders
FROM 
    orders o
JOIN 
    customers c ON o.customer_id = c.customer_id
GROUP BY 
    o.order_id, c.customer_name;