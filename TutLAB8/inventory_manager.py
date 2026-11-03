import os
import json



class Product:

  def __init__(self, product_id: str, name: str, price: float, stock: int):
    self._product_id = product_id
    self.name = name
    self._price = price
    self.stock = stock

  @property
  def product_id(self):
    return self._product_id

  @property
  def price(self):
    return self._price

  def update_stock(self, quantity: int) -> None:
    if quantity < 0:
      raise ValueError("Stock count cannot be negative.")
    self.stock = quantity

  def display_information(self) -> None:
    print(
        f"ID: {self._product_id} | Name: {self.name} | Price:"
        f" ${self._price:.2f} | Stock: {self.stock}"
    )



class Inventory:

  def __init__(self):
    self.products = {}

  def add_product(self, product: Product) -> None:
    self.products[product.product_id] = product

  def search_product(self, product_id: str) -> Product | None:
    return self.products.get(product_id.upper())

  def display_all(self) -> None:
    print("\nCurrent Inventory")
    print("-" * 45)
    if not self.products:
      print("Inventory is currently empty.")
    else:
      for product in self.products.values():
        product.display_information()
    print("-" * 45)

  def generate_next_id(self) -> str:
    existing_ids = [
        int(p_id[1:])
        for p_id in self.products.keys()
        if p_id.startswith("P") and p_id[1:].isdigit()
    ]
    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"P{next_num:03d}"

  def to_dict(self) -> dict:
    return {
        p_id: {
            "name": p.name,
            "price": p.price,
            "stock": p.stock,
        }
        for p_id, p in self.products.items()
    }

  @classmethod
  def from_dict(cls, data: dict):
    inventory = cls()
    for p_id, details in data.items():
      prod = Product(
          product_id=p_id,
          name=details["name"],
          price=float(details["price"]),
          stock=int(details["stock"]),
      )
      inventory.add_product(prod)
    return inventory



def load_inventory():
    if os.path.exists("inventory.json"):
        try:
            with open("inventory.json", "r") as file:
                inventory = json.load(file)
                print("inventory.json found.")
                print("Inventory loaded successfully.")
                return inventory
        except json.JSONDecodeError:
            print("inventory.json is corrupted. Starting with default inventory.")
    
    # Default initial inventory if file does not exist[cite: 1]
    return {
        "P001": {"name": "Laptop", "price": 1200.00, "stock": 15},
        "P002": {"name": "Mouse", "price": 25.50, "stock": 40},
        "P003": {"name": "Keyboard", "price": 45.00, "stock": 25}
    }

def save_inventory(inventory_dict):
    with open("inventory.json", "w") as file:
        json.dump(inventory_dict, file, indent=4)
    print("Inventory saved successfully to inventory.json.")

def display_all(inventory_dict):
    print("\nCurrent Inventory")
    print("-" * 45)
    if not inventory_dict:
        print("Inventory is currently empty.")
    else:
        for item_id, details in inventory_dict.items():
            print(f"ID: {item_id} | Name: {details['name']} | Price: ${details['price']:.2f} | Stock: {details['stock']}")
    print("-" * 45)

def add_product(inventory_dict):
    print("\nAdd New Product")
    
    # Auto-generate next Product ID (e.g., P004)[cite: 2]
    existing_ids = [int(p_id[1:]) for p_id in inventory_dict.keys() if p_id.startswith('P') and p_id[1:].isdigit()]
    next_num = max(existing_ids) + 1 if existing_ids else 1
    new_id = f"P{next_num:03d}"
    print(f"Product ID: {new_id}")

    product_name = input("Product Name: ").strip()
    if not product_name:
        print("Product name cannot be empty.")
        return

    try:
        price = float(input("Price: ").strip())
        stock = int(input("Stock Quantity: ").strip())
    except ValueError:
        print("Invalid input. Price and Stock must be numeric.")
        return

    if price < 0 or stock < 0:
        print("Price and stock cannot be negative.")
        return

    inventory_dict[new_id] = {
        "name": product_name,
        "price": price,
        "stock": stock
    }

    print("\nProduct added successfully!")

def update_stock(inventory_dict):
    print("\nUpdate Stock")
    item_id = input("Enter Product ID: ").strip().upper()

    if item_id not in inventory_dict:
        print("Product not found.")
        return

    product = inventory_dict[item_id]
    print("\nProduct Found:")
    print(f"Name: {product['name']}")
    print(f"Current Stock: {product['stock']}\n")

    try:
        new_stock = int(input("New Stock Quantity: ").strip())
    except ValueError:
        print("Invalid stock value.")
        return

    if new_stock < 0:
        print("Stock count cannot be negative.")
        return

    inventory_dict[item_id]["stock"] = new_stock
    print("\nStock updated successfully!")

def search_product(inventory_dict):
    print("\nSearch Product")
    query = input("Enter Product ID: ").strip().upper()

    if query in inventory_dict:
        details = inventory_dict[query]
        print("\nProduct Found")
        print("-" * 45)
        print(f"ID: {query}")
        print(f"Name: {details['name']}")
        print(f"Price: ${details['price']:.2f}")
        print(f"Stock: {details['stock']}")
        print("-" * 45)
    else:
        print("\nProduct not found.")

def main():
    print("========================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("========================================\n")

    inventory_dict = load_inventory()

    while True:
        print("\n----------- MENU -----------")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")
        print("----------------------------")

        choice = input("Enter option: ").strip()

        if choice == '1':
            display_all(inventory_dict)
        elif choice == '2':
            add_product(inventory_dict)
        elif choice == '3':
            update_stock(inventory_dict)
        elif choice == '4':
            search_product(inventory_dict)
        elif choice == '5':
            print("\nSaving inventory...")
            save_inventory(inventory_dict)
        elif choice == '6':
            print("\nSaving inventory before exit...")
            save_inventory(inventory_dict)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    main()