CREATE PROCEDURE update_order_status
    @OrderID INT,
    @NewStatus VARCHAR(50)
AS
BEGIN
    UPDATE orders
    SET status = @NewStatus
    WHERE id = @OrderID;
END;