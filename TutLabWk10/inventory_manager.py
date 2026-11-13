from abc import ABC, abstractmethod
import json
import os


class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


class Product(ABC):

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

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass


class PhysicalProduct(Product, CanBeShipped):

    def __init__(self, product_id: str, name: str, price: float, stock: int, weight: float):
        super().__init__(product_id, name, price, stock)
        self.weight = weight

    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.weight} kg")

    def get_fulfilment_info(self) -> str:
        return "Physical Product - Requires shipping"

    def calculate_shipping_cost(self) -> float:
        return self.weight * 5.0  # Example: $5 per kg


class DigitalProduct(Product):

    def __init__(self, product_id: str, name: str, price: float, stock: int, file_size: float):
        super().__init__(product_id, name, price, stock)
        self.file_size = file_size

    def display_information(self) -> None:
        super().display_information()
        print(f"File Size: {self.file_size} MB")

    def get_fulfilment_info(self) -> str:
        return "Digital Product - Instant download"


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
                print(f"Fulfilment: {product.get_fulfilment_info()}")
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
        result = {}
        for p_id, p in self.products.items():
            p_data = {
                "name": p.name,
                "price": p.price,
                "stock": p.stock,
            }
            if isinstance(p, PhysicalProduct):
                p_data["type"] = "physical"
                p_data["weight"] = p.weight
            elif isinstance(p, DigitalProduct):
                p_data["type"] = "digital"
                p_data["file_size"] = p.file_size
            result[p_id] = p_data
        return result

    @classmethod
    def from_dict(cls, data: dict):
        inventory = cls()
        for p_id, details in data.items():
            p_type = details.get("type", "physical")
            if p_type == "physical":
                prod = PhysicalProduct(
                    product_id=p_id,
                    name=details["name"],
                    price=float(details["price"]),
                    stock=int(details["stock"]),
                    weight=float(details.get("weight", 1.0))
                )
            elif p_type == "digital":
                prod = DigitalProduct(
                    product_id=p_id,
                    name=details["name"],
                    price=float(details["price"]),
                    stock=int(details["stock"]),
                    file_size=float(details.get("file_size", 100.0))
                )
            inventory.add_product(prod)
        return inventory


def load_inventory() -> Inventory:
    if os.path.exists("inventory.json"):
        try:
            with open("inventory.json", "r") as file:
                data = json.load(file)
                print("inventory.json found.")
                print("Inventory loaded successfully.")
                return Inventory.from_dict(data)
        except json.JSONDecodeError:
            print("inventory.json is corrupted. Starting with default inventory.")

    default_data = {
        "P001": {"type": "physical", "name": "Laptop", "price": 1200.00, "stock": 15, "weight": 2.5},
        "P002": {"type": "physical", "name": "Mouse", "price": 25.50, "stock": 40, "weight": 0.2},
        "P003": {"type": "digital", "name": "Keyboard Software", "price": 45.00, "stock": 25, "file_size": 150.0},
    }
    return Inventory.from_dict(default_data)


def save_inventory(inventory: Inventory) -> None:
    with open("inventory.json", "w") as file:
        json.dump(inventory.to_dict(), file, indent=4)
    print("Inventory saved successfully to inventory.json.")


def add_product_menu(inventory: Inventory) -> None:
    print("\nAdd New Product")
    print("1. Physical Product")
    print("2. Digital Product")
    choice = input("Select product type (1 or 2): ").strip()

    if choice not in ["1", "2"]:
        print("Invalid product type selection.")
        return

    new_id = inventory.generate_next_id()
    print(f"Product ID: {new_id}")

    product_name = input("Product Name: ").strip()
    if not product_name:
        print("Product name cannot be empty.")
        return

    try:
        price = float(input("Price: ").strip())
        stock = int(input("Stock Quantity: ").strip())
        if choice == "1":
            weight = float(input("Weight (kg): ").strip())
        else:
            file_size = float(input("File Size (MB): ").strip())
    except ValueError:
        print("Invalid input. Numeric values expected.")
        return

    if price < 0 or stock < 0 or (choice == "1" and weight < 0) or (choice == "2" and file_size < 0):
        print("Values cannot be negative.")
        return

    if choice == "1":
        new_product = PhysicalProduct(new_id, product_name, price, stock, weight)
    else:
        new_product = DigitalProduct(new_id, product_name, price, stock, file_size)

    inventory.add_product(new_product)
    print("\nProduct added successfully!")


def update_stock_menu(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    item_id = input("Enter Product ID: ").strip().upper()
    product = inventory.search_product(item_id)

    if not product:
        print("Product not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.name}")
    print(f"Current Stock: {product.stock}\n")

    try:
        new_stock = int(input("New Stock Quantity: ").strip())
        product.update_stock(new_stock)
        print("\nStock updated successfully!")
    except ValueError as e:
        print(f"Invalid stock value: {e}")


def search_product_menu(inventory: Inventory) -> None:
    print("\nSearch Product")
    query = input("Enter Product ID: ").strip().upper()
    product = inventory.search_product(query)

    if product:
        print("\nProduct Found")
        print("-" * 45)
        product.display_information()
        print(f"Fulfilment: {product.get_fulfilment_info()}")
        print("-" * 45)
    else:
        print("\nProduct not found.")


def main():
    print("========================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("========================================\n")
    inventory = load_inventory()

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

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product_menu(inventory)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            print("\nSaving inventory...")
            save_inventory(inventory)
        elif choice == "6":
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()