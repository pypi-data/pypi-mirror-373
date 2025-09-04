CREATE PROCEDURE get_customer_info
    @CustomerID INT
AS
BEGIN
    SELECT *
    FROM customers
    WHERE id = @CustomerID;
END;