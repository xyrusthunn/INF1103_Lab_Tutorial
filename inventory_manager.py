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

                        total_inventory += qty
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        pass

    return total_inventory, inventory_dict, last_id


def save_inventory_data(inventory_dict):
    with open("inventory.txt", "w") as file:
        for item_id, details in inventory_dict.items():
            file.write(f"{item_id},{details['name']},{details['quantity']},{details['price']:.2f},{details['stock']}\n")


def collect_user_entry():
    item_name = input("Enter Product Name (Enter quit to leave application): ").strip()
    if item_name.lower() == 'quit':
        return 'quit', None, None, None

    quantity_input = input("Enter Quantity: ").strip()
    price_input = input("Enter Price ($): ").strip()
    stock_input = input("Enter Current Stock Count: ").strip()

    try:
        qty = int(quantity_input)
        price = float(price_input)
        stock = int(stock_input)
        return item_name, qty, price, stock
    except ValueError:
        print("Invalid input. Please enter valid numbers for quantity, price, and stock count.")
        return item_name, None, None, None

def main():
    inventory_count, inventory_dict, last_id = load_inventory_data()
    total_delivery_processed = len(inventory_dict)
    failed_attempts = 0

    print("Current Inventory:\n")
    if inventory_dict:
        for item_id, details in inventory_dict.items():
            print(f"ID: {item_id} | Product: {details['name']} | Qty: {details['quantity']} | Price: ${details['price']:.2f} | Stock: {details['stock']}")
        print()

    while True:
        product, quantity, price, stock = collect_user_entry()

        if product == 'quit':
            print("\nExiting inventory entry...")
            break
        elif quantity is None or price is None or stock is None:
            failed_attempts += 1
            continue
        else: 
            updated_inventory_count, is_successful = handle_inventory_addition(inventory_count, quantity)

            if not is_successful: 
                failed_attempts += 1
                print("\nDelivery rejected due to negative stock quantity or zero quantity.\n")
            else:
                inventory_count = updated_inventory_count
                total_delivery_processed += 1
                last_id += 1

                inventory_dict[last_id] = {
                    "name": product,
                    "quantity": quantity,
                    "price": price,
                    "stock": stock
                }

                print("\nNew Inventory Added:")
                print(f"ID: {last_id} | Product: {product} | Qty: {quantity} | Price: ${price:.2f} | Stock: {stock}")

                save_inventory_data(inventory_dict)
                print("\nInventory successfully saved to inventory.txt\n")



if __name__ == "__main__":
    main()