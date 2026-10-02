import os

def load_inventory_data():
    total_inventory = 0
    last_id = 1000 
    history = [] 

    try:
        with open("inventory.txt", "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    history.append(line)

                    try:
                        parts = line.split(',')
                        current_id = int(parts[0].strip())
                        if current_id > last_id:
                            last_id = current_id
                        qty = int(parts[-1].strip())
                        total_inventory += qty
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        pass

    return total_inventory, history, last_id

def save_inventory_data(history):
    with open("inventory.txt", "w") as file:
        for entry in history:
            file.write(f"{entry}\n")


def collect_user_entry():
    item_name = input("Enter Product Name (Enter quit to leave application): ").strip()
    if item_name.lower() == 'quit':
        return 'quit', None
    quantity_input = input("Enter Quantity: ").strip()
    try:
        return item_name, int(quantity_input)
    except ValueError:
        print("Invalid input. Please enter a valid integer for quantity.")
        return item_name, None


def handle_inventory_addition(current_sum, new_quantity):
    if new_quantity <= 0:
        return current_sum, False
    else:
        return current_sum + new_quantity, True


def compute_tax(amount):
    return amount * 0.10


def display_summary(total_processed, rejected_count):
    print("\n==== Final Inventory Report ====")
    print(f"Total Deliveries Processed: {total_processed}")
    print(f"Number of Failed/Rejected Entries: {rejected_count}")


def main():
    inventory_count, history, last_id = load_inventory_data()
    total_delivery_processed = len(history)
    failed_attempts = 0

    print("Current Inventory:\n")
    if history:
        for inventory in history:
            print(inventory)
        print()

    while True:
        product, quantity = collect_user_entry()

        if product == 'quit':
            print("\nExiting inventory entry...")
            break
        elif quantity is None:
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

                new_inventory_record = f"{last_id},{product},{quantity}"
                history.append(new_inventory_record)

                print("\nNew Inventory Added:")
                print(new_inventory_record)

                save_inventory_data(history)
                print("\nInventory successfully saved to inventory.txt\n")

                tax_amount = compute_tax(quantity)
                print(f"Delivery accepted. Tax for this delivery: {tax_amount:.2f}\n")

    display_summary(total_delivery_processed, failed_attempts)


if __name__ == "__main__":
    main()