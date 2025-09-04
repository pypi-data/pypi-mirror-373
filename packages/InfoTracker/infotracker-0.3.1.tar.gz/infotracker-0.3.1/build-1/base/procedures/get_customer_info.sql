CREATE PROCEDURE get_customer_info
    @CustomerID INT
AS
BEGIN
    SELECT 
        c.CustomerID,
        c.FirstName,
        c.LastName,
        c.Email,
        c.Phone,
        o.OrderID,
        o.OrderDate,
        o.TotalAmount
    FROM 
        customers c
    LEFT JOIN 
        orders o ON c.CustomerID = o.CustomerID
    WHERE 
        c.CustomerID = @CustomerID;
END;