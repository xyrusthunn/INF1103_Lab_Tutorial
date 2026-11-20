from abc import ABC, abstractmethod
import json
import os
import csv





class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str):
        self.supplier_id: str = supplier_id
        self.name: str = name
        self.contact_email: str = contact_email

    def display_information(self) -> None:
        print(f"Supplier ID: {self.supplier_id} | Name: {self.name} | Contact Info: {self.contact_email}")


class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


class Product(ABC):

    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier):
        if price <= 0:
            raise ValueError("Price must be a positive value.")
        if stock < 0:
            raise ValueError("Stock count cannot be negative.")
        self._product_id = product_id
        self.name = name
        self._price = price
        self.stock = stock
        self.supplier: Supplier = supplier

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
        print(f"ID: {self._product_id} | Name: {self.name} | Price: ${self._price:.2f} | Stock: {self.stock}")
        self.supplier.display_information()

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass


class PhysicalProduct(Product, CanBeShipped):

    def __init__(self, product_id: str, name: str, price: float, stock: int, weight: float, supplier: Supplier):
        super().__init__(product_id, name, price, stock, supplier)
        self.weight = weight

    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.weight} kg")

    def get_fulfilment_info(self) -> str:
        return "Physical Product - Requires shipping"

    def calculate_shipping_cost(self) -> float:
        return self.weight * 5.0  # Example: $5 per kg


class DigitalProduct(Product):

    def __init__(self, product_id: str, name: str, price: float, stock: int, file_size: float, supplier: Supplier):
        super().__init__(product_id, name, price, stock, supplier)
        self.file_size = file_size

    def display_information(self) -> None:
        super().display_information()
        print(f"File Size: {self.file_size} MB")

    def get_fulfilment_info(self) -> str:
        return "Digital Product - Instant download"


class ProductFactory:
    @staticmethod
    def create_product(product_type: str, product_id: str, name: str, price: float, stock: int, supplier: Supplier, weight: float = 1.0, file_size: float = 100.0) -> Product:
        normalized_type = product_type.strip().lower()
        if normalized_type == "physical":
            return PhysicalProduct(product_id, name, price, stock, weight, supplier)
        elif normalized_type == "digital":
            return DigitalProduct(product_id, name, price, stock, file_size, supplier)
        else:
            raise ValueError(f"Unknown product type: {product_type}")


class Inventory:

    def __init__(self):
        self.products: dict[str, Product] = {}

    def add_product(self, product: Product) -> None:
        self.products[product.product_id] = product


    def remove_product(self, product_id: str) -> None:
        if product_id.upper() in self.products:
            del self.products[product_id]
        else:
            print(f"Product ID {product_id} not found in inventory.")

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



class DiscountStrategy(ABC):
    @abstractmethod
    def apply_discount(self, total: float) -> float:
        pass

class NoDiscount(DiscountStrategy):
    def apply_discount(self, total: float) -> float:
        return total

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def apply_discount(self, total: float) -> float:
        return total * (1 - self.percentage / 100)

class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, discount_amount: float):
        self.threshold = threshold
        self.discount_amount = discount_amount

    def apply_discount(self, total: float) -> float:
        if total >= self.threshold:
            return total - self.discount_amount
        return total

class StudentDiscount(DiscountStrategy):
    def apply_discount(self, total: float) -> float:
        return total * 0.95  # 5% discount for students


class OrderLine:
    def __init__(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        self.product: Product = product
        self.quantity: int = quantity

    def calculate_subtotal(self) -> float:
        return self.product.price * self.quantity


class Order:
    def __init__(self, order_id: str, discount: DiscountStrategy = None):
        self.order_id: str = order_id
        self.order_lines: list[OrderLine] = []
        self.discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self.order_lines.append(order_line)

    def calculate_total(self) -> float:
        total = 0.0
        for line in self.order_lines:
            total += line.calculate_subtotal()
        return self.discount.apply_discount(total)


def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt).strip())
            if value <= 0:
                print("Value cannot be zero or negative. Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def load_products_from_csv(file_path: str, inventory: Inventory, supplier: Supplier) -> None:
    loaded_count = 0
    try:
        file = open(file_path, mode='r', newline='', encoding='utf-8')
    except FileNotFoundError:
        print(f"Products file not found: {file_path}.")
    else:
        with file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header row
            for row_num, row in enumerate(reader, start=2):
                if not row:
                    continue  # Skip empty rows
                try:
                    product_type = row[0].strip().lower()
                    product_id = row[1].strip()
                    name = row[2].strip()
                    price = float(row[3].strip())
                    stock = int(row[4].strip())
                    product = ProductFactory.create_product(
                        product_type=product_type,
                        product_id=product_id,
                        name=name,
                        price=price,
                        stock=stock,
                        supplier=supplier
                    )
                    inventory.add_product(product)
                    loaded_count += 1
                except (ValueError, IndexError) as e:
                    print(f"Skipping invalid row {row_num} ({row}): {e}")
            print(f"{loaded_count} products loaded.")
    finally:
        print("Load attempt finished.")



def load_inventory() -> Inventory:
    default_supplier = Supplier("S001", "Micron Technologies", "contact@micron.com")

    if os.path.exists("inventory.json"):
        try:
            with open("inventory.json", "r") as file:
                data = json.load(file)
                print("inventory.json found.")
                print("Inventory loaded successfully.")
                inventory = Inventory()
                for p_id, details in data.items():
                    p_type = details.get("type", "physical")
                    prod = ProductFactory.create_product(
                            product_type=p_type,
                            product_id=p_id,
                            name=details["name"],
                            price=float(details["price"]),
                            stock=int(details["stock"]),
                            weight=float(details.get("weight", 1.0)),
                            file_size=float(details.get("file_size", 100.0)),
                            supplier=default_supplier
                        )
                    inventory.add_product(prod)
                return inventory
        except json.JSONDecodeError:
            print("inventory.json is corrupted. Starting with default inventory.")

    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.00, 15, 2.5, default_supplier))
    inventory.add_product(PhysicalProduct("P002", "Mouse", 25.50, 40, 0.2, default_supplier))
    inventory.add_product(DigitalProduct("P003", "Keyboard Software", 45.00, 25, 150.0, default_supplier))
    return inventory


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

    weight = 1.0
    file_size = 100.0

    try:
        price = get_positive_float("Price: ")
        stock = int(input("Stock Quantity: ").strip())
        supplier_id = input("Supplier ID: ").strip()
        supplier_name = input("Supplier Name: ").strip()
        supplier_email = input("Supplier Contact Info: ").strip()
        supplier = Supplier(supplier_id, supplier_name, supplier_email)

        if choice == "1":
            weight = get_positive_float("Weight (kg): ")
        else:
            file_size = get_positive_float("File Size (MB): ")
    except ValueError:
        print("Invalid input. Please enter numeric values for price, stock, weight, and file size.")
        return


    if price < 0 or stock < 0 or (choice == "1" and weight < 0) or (choice == "2" and file_size < 0):
        print("Values cannot be negative.")
        return

    product_type = "physical" if choice == "1" else "digital"
    new_product = ProductFactory.create_product(
        product_type=product_type,
        product_id=new_id,
        name=product_name,
        price=price,
        stock=stock,
        supplier=supplier,
        weight=weight,
        file_size=file_size
    )
    
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