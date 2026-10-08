import os

def load_inventory_data():
    total_inventory = 0
    last_id = 1000 
    inventory_dict = {} 

    try:
        with open("inventory.txt", "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        parts = line.split(',')
                        current_id = int(parts[0].strip())
                        product_name = parts[1].strip()
                        qty = int(parts[2].strip())
                        price = float(parts[3].strip())
                        stock = int(parts[4].strip())

                        if current_id > last_id:
                            last_id = current_id

                        inventory_dict[current_id] = {
                            "name": product_name,
                            "quantity": qty,
                            "price": price,
                            "stock": stock
                        }
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        pass

    return inventory_dict, last_id

def save_inventory_data(inventory_dict):
    with open("inventory.txt", "w") as file:
        for item_id, details in inventory_dict.items():
            file.write(f"{item_id},{details['name']},{details['quantity']},{details['price']:.2f},{details['stock']}\n")

def display_all(inventory_dict):
    print("\n--- Current Inventory ---\n")
    if not inventory_dict:
        print("Inventory is currently empty.")
        return

    for item_id, details in inventory_dict.items():
        print(f"ID: {item_id} | Product: {details['name']} | Qty: {details['quantity']} | Price: ${details['price']:.2f} | Stock: {details['stock']}")
    print()

def add_product(inventory_dict, last_id):
    product_name = input("Enter Product Name: ").strip()
    if not product_name:
        print("Product name cannot be empty.")
        return last_id

    try:
        qty = int(input("Enter Quantity: ").strip())
        price = float(input("Enter Price ($): ").strip())
        stock = int(input("Enter Current Stock Count: ").strip())
    except ValueError:
        print("Invalid input. Quantity, Price, and Stock must be numeric.")
        return last_id

    if qty <= 0:
        print("Entry rejected due to negative or zero quantity.")
        return last_id

    last_id += 1
    inventory_dict[last_id] = {
        "name": product_name,
        "quantity": qty,
        "price": price,
        "stock": stock
    }

    save_inventory_data(inventory_dict)
    print(f"\nNew Product Added -> ID: {last_id} | Product: {product_name} | Qty: {qty} | Price: ${price:.2f} | Stock: {stock}")
    print("Inventory successfully saved to inventory.txt\n")
    return last_id

def update_stock(inventory_dict):
    try:
        item_id = int(input("Enter Product ID to update stock: ").strip())
    except ValueError:
        print("Invalid ID format.")
        return

    if item_id not in inventory_dict:
        print(f"Product ID: {item_id} not found.")
        return

    try:
        new_stock = int(input(f"Enter new stock count for {inventory_dict[item_id]['name']}: ").strip())
    except ValueError:
        print("Invalid stock value.")
        return

    if new_stock < 0:
        print("Stock count cannot be negative.")
        return

    inventory_dict[item_id]["stock"] = new_stock
    save_inventory_data(inventory_dict)
    print(f"Stock for ID: {item_id} ({inventory_dict[item_id]['name']}) updated to {new_stock}.")

def search_product(inventory_dict):
    query = input("Enter Product ID or Product Name to search: ").strip().lower()
    found = False

    for item_id, details in inventory_dict.items():
        if str(item_id) == query or details["name"].lower() == query:
            print(f"\nFound -> ID: {item_id} | Product: {details['name']} | Qty: {details['quantity']} | Price: ${details['price']:.2f} | Stock: {details['stock']}")
            found = True

    if not found:
        print("No matching product found.")

def main():
    inventory_dict, last_id = load_inventory_data()

    while True:
        print("\n=== Inventory Management Menu ===")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Quit")

        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            display_all(inventory_dict)
        elif choice == '2':
            last_id = add_product(inventory_dict, last_id)
        elif choice == '3':
            update_stock(inventory_dict)
        elif choice == '4':
            search_product(inventory_dict)
        elif choice == '5':
            print("\nExiting inventory application...")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

if __name__ == "__main__":
    main()