# Restaurant Order Management System

This is a RESTful API built with FastAPI for managing restaurant orders. It supports managing customers, menu items, and orders, including the ability to add, update, and delete data for customers, items, and orders.

## Features

- **Customer Management**: Add, update, delete, and retrieve customer details.
- **Menu Management**: Add, update, delete, and retrieve menu items.
- **Order Management**: Create, update, delete, and retrieve orders, including the associated items.

## Requirements

- Python 3.7+
- FastAPI
- SQLite3 (No need for external database setup)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. **Set up a virtual environment** (optional but recommended):
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. **Initialize the database**:
Run the following command to create the database schema and tables.
```
python init_db.py
```
## **Running the Application**

1. **Start the FastAPI server**:
   Run the following command to start the FastAPI server. The server will be running in development mode with hot reload enabled.

   ```bash
   uvicorn main:app --reload
   ```
2. **The API will be accessible at http://127.0.0.1:8000.
   Access the Swagger UI: FastAPI provides an auto-generated interactive API documentation. To access it, go to:

   ```bash
   http://127.0.0.1:8000/docs
   ```

## API Endpoints

### Customer Endpoints
- **POST** `/customers`: Create a new customer.
- **GET** `/customers/{id}`: Retrieve customer details by ID.
- **PUT** `/customers/{id}`: Update customer details.
- **DELETE** `/customers/{id}`: Delete a customer.

### Item Endpoints
- **POST** `/items`: Add a new item to the menu.
- **GET** `/items/{id}`: Get item details by ID.
- **PUT** `/items/{id}`: Update an existing item in the menu.
- **DELETE** `/items/{id}`: Delete an item from the menu.

### Order Endpoints
- **POST** `/orders`: Create a new order for a customer with one or more items.
- **GET** `/orders/{id}`: Get order details, including items.
- **PUT** `/orders/{id}`: Update an existing order.
- **DELETE** `/orders/{id}`: Delete an order.

## Database

This project uses an SQLite database (`db.sqlite`) with the following tables:

- **`customers`**: Stores customer details.  
  **Columns**:  
  - `id` (INTEGER, Primary Key)  
  - `name` (TEXT, Not Null)  
  - `phone` (TEXT, Unique, Not Null)  

- **`menu_items`**: Stores menu items.  
  **Columns**:  
  - `id` (INTEGER, Primary Key)  
  - `dish_name` (TEXT, Unique, Not Null)  
  - `price` (REAL, Not Null)  

- **`customer_orders`**: Stores order details.  
  **Columns**:  
  - `id` (INTEGER, Primary Key)  
  - `customer_id` (INTEGER, Foreign Key to `customers`)  
  - `order_notes` (TEXT)  
  - `timestamp` (INTEGER, Not Null)  

- **`ordered_items`**: Stores the items associated with each order.  
  **Columns**:  
  - `order_id` (INTEGER, Foreign Key to `customer_orders`)  
  - `menu_item_id` (INTEGER, Foreign Key to `menu_items`)  



