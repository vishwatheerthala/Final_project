from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

app = FastAPI()

# -------------------- Database Configuration --------------------
DB_PATH = "restaurant_data.db"  # Updated DB path

# -------------------- Utility Function --------------------
def execute_sql(query: str, params: tuple = (), single_result: bool = False, all_results: bool = False):
    """Execute SQL queries and return results."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if single_result:
            return cursor.fetchone()
        if all_results:
            return cursor.fetchall()
        return cursor.lastrowid

# -------------------- Pydantic Models --------------------
class Customer(BaseModel):
    full_name: str
    contact_number: str


class MenuItem(BaseModel):
    dish_name: str
    cost: float


class OrderDetails(BaseModel):
    customer_id: int
    items: List[MenuItem]
    order_notes: Optional[str] = None


# -------------------- Helper Functions --------------------
def does_record_exist(table: str, record_id: int):
    """Check if a record exists in the specified table."""
    query = f"SELECT * FROM {table} WHERE id = ?"
    return execute_sql(query, (record_id,), single_result=True)

# -------------------- Customer Endpoints --------------------
@app.post("/customers")
def create_customer(customer: Customer):
    try:
        query = "INSERT INTO customers (full_name, contact_number) VALUES (?, ?)"
        customer_id = execute_sql(query, (customer.full_name, customer.contact_number))
        return {"id": customer_id, "message": "Customer created successfully."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Customer with this contact number already exists.")


@app.get("/customers/{id}")
def get_customer(id: int):
    customer = does_record_exist("customers", id)
    if customer:
        return {"id": customer[0], "full_name": customer[1], "contact_number": customer[2]}
    raise HTTPException(status_code=404, detail="Customer not found.")


@app.put("/customers/{id}")
def update_customer(id: int, customer: Customer):
    if not does_record_exist("customers", id):
        raise HTTPException(status_code=404, detail="Customer not found.")

    query = "UPDATE customers SET full_name = ?, contact_number = ? WHERE id = ?"
    execute_sql(query, (customer.full_name, customer.contact_number, id))
    return {"message": "Customer updated successfully."}


@app.delete("/customers/{id}")
def delete_customer(id: int):
    if not does_record_exist("customers", id):
        raise HTTPException(status_code=404, detail="Customer not found.")

    query = "DELETE FROM customers WHERE id = ?"
    execute_sql(query, (id,))
    return {"message": "Customer deleted successfully."}


# -------------------- Menu Item Endpoints --------------------
@app.post("/menu-items")
def create_menu_item(item: MenuItem):
    query = "INSERT INTO menu_items (dish_name, cost) VALUES (?, ?)"
    item_id = execute_sql(query, (item.dish_name, item.cost))
    return {"id": item_id, "message": "Menu item added successfully."}


@app.get("/menu-items/{id}")
def get_menu_item(id: int):
    item = does_record_exist("menu_items", id)
    if item:
        return {"id": item[0], "dish_name": item[1], "cost": item[2]}
    raise HTTPException(status_code=404, detail="Menu item not found.")


@app.put("/menu-items/{id}")
def update_menu_item(id: int, item: MenuItem):
    if not does_record_exist("menu_items", id):
        raise HTTPException(status_code=404, detail="Menu item not found.")

    query = "UPDATE menu_items SET dish_name = ?, cost = ? WHERE id = ?"
    execute_sql(query, (item.dish_name, item.cost, id))
    return {"message": "Menu item updated successfully."}


@app.delete("/menu-items/{id}")
def delete_menu_item(id: int):
    if not does_record_exist("menu_items", id):
        raise HTTPException(status_code=404, detail="Menu item not found.")

    query = "DELETE FROM menu_items WHERE id = ?"
    execute_sql(query, (id,))
    return {"message": "Menu item deleted successfully."}


# -------------------- Order Endpoints --------------------
@app.post("/orders")
def create_order(order: OrderDetails):
    # Check if customer exists
    if not does_record_exist("customers", order.customer_id):
        raise HTTPException(status_code=404, detail="Customer not found.")

    # Create the order entry
    query = "INSERT INTO customer_orders (customer_id, order_notes, order_time) VALUES (?, ?, strftime('%s', 'now'))"
    order_id = execute_sql(query, (order.customer_id, order.order_notes or ""))

    # Add ordered items
    price_changes = []
    for menu_item in order.items:
        item_data = execute_sql("SELECT id, cost FROM menu_items WHERE dish_name = ?", (menu_item.dish_name,), single_result=True)
        if not item_data:
            raise HTTPException(status_code=404, detail=f"Menu item '{menu_item.dish_name}' not found.")
        
        item_id, correct_cost = item_data
        if menu_item.cost != correct_cost:
            price_changes.append(f"Menu item '{menu_item.dish_name}' cost updated from {menu_item.cost} to {correct_cost}.")
        execute_sql("INSERT INTO ordered_items (order_id, menu_item_id) VALUES (?, ?)", (order_id, item_id))

    response = {"id": order_id, "message": "Order created successfully."}
    if price_changes:
        response["price_changes"] = price_changes
    return response


@app.get("/orders/{id}")
def get_order(id: int):
    order = execute_sql("SELECT id, customer_id, order_notes FROM customer_orders WHERE id = ?", (id,), single_result=True)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    items = execute_sql(
        "SELECT m.dish_name, m.cost FROM ordered_items oi JOIN menu_items m ON oi.menu_item_id = m.id WHERE oi.order_id = ?",
        (id,),
        all_results=True,
    )
    return {
        "id": order[0],
        "customer_id": order[1],
        "order_notes": order[2],
        "items": [{"dish_name": item[0], "cost": item[1]} for item in items],
    }

@app.put("/orders/{id}")
def update_order(id: int, order: OrderDetails):
    # Check if the order exists
    if not does_record_exist("customer_orders", id):
        raise HTTPException(status_code=404, detail="Order not found.")

    # Update the order's customer_id and notes
    query = "UPDATE customer_orders SET customer_id = ?, order_notes = ? WHERE id = ?"
    execute_sql(query, (order.customer_id, order.order_notes or "", id))

    # Remove old items from the order and add the new ones
    execute_sql("DELETE FROM ordered_items WHERE order_id = ?", (id,))

    price_changes = []
    for menu_item in order.items:
        item_data = execute_sql("SELECT id, cost FROM menu_items WHERE dish_name = ?", (menu_item.dish_name,), single_result=True)
        if not item_data:
            raise HTTPException(status_code=404, detail=f"Menu item '{menu_item.dish_name}' not found.")

        item_id, correct_cost = item_data
        if menu_item.cost != correct_cost:
            price_changes.append(f"Menu item '{menu_item.dish_name}' cost updated from {menu_item.cost} to {correct_cost}.")
        execute_sql("INSERT INTO ordered_items (order_id, menu_item_id) VALUES (?, ?)", (id, item_id))

    response = {"id": id, "message": "Order updated successfully."}
    if price_changes:
        response["price_changes"] = price_changes
    return response


@app.delete("/orders/{id}")
def delete_order(id: int):
    # Check if the order exists
    if not does_record_exist("customer_orders", id):
        raise HTTPException(status_code=404, detail="Order not found.")

    # Delete the associated items in the order
    execute_sql("DELETE FROM ordered_items WHERE order_id = ?", (id,))

    # Delete the order itself
    execute_sql("DELETE FROM customer_orders WHERE id = ?", (id,))
    
    return {"message": "Order deleted successfully."}
