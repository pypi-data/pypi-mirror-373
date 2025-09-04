# InfoTracker SQL Diff Demonstration

This project demonstrates the functionality of the SQL diff command in the InfoTracker tool. It contains two sets of SQL files: one representing the base state of the database schema and another representing the head state, which may include modifications.

## Directory Structure

- **build/base**: Contains the original SQL files representing the base schema.
  - **tables**: Definitions of the base tables.
    - `customers.sql`: Definition of the `customers` table.
    - `orders.sql`: Definition of the `orders` table.
    - `products.sql`: Definition of the `products` table.
  - **views**: Definitions of the base views.
    - `customer_orders.sql`: View aggregating data from `customers` and `orders`.
    - `sales_summary.sql`: View summarizing sales data from the `orders` table.
  - **procedures**: Definitions of the base stored procedures.
    - `get_customer_info.sql`: Procedure to retrieve customer information.
    - `update_order_status.sql`: Procedure to update order status.

- **build/head**: Contains the modified SQL files representing the head schema.
  - **tables**: Definitions of the head tables, including potential modifications.
    - `customers.sql`: Modified definition of the `customers` table.
    - `orders.sql`: Modified definition of the `orders` table.
    - `products.sql`: Modified definition of the `products` table.
    - `order_items.sql`: New table definition for `order_items`.
  - **views**: Definitions of the head views, unchanged from the base.
    - `customer_orders.sql`: Unchanged view from the base.
    - `sales_summary.sql`: Unchanged view from the base.
  - **procedures**: Definitions of the head stored procedures, unchanged from the base.
    - `get_customer_info.sql`: Unchanged procedure from the base.
    - `update_order_status.sql`: Unchanged procedure from the base.

## Usage

To demonstrate the diff functionality, you can run the following command:

```bash
infotracker diff --base build/base --head build/head --format text
```

This command will compare the SQL files in the `base` and `head` directories and output the differences, highlighting any changes in table definitions, views, and procedures.