import pytest

from inventory_manager import (
    Supplier,
    PhysicalProduct,
    DigitalProduct,
    Inventory,
    Order,
    DiscountStrategy,
    NoDiscount,
    PercentageDiscount,
    BulkDiscount,
    StudentDiscount,
    ProductFactory,
    load_products_from_csv,
)


class FixedFiveDollarOff(DiscountStrategy):
    def apply_discount(self, total: float) -> float:
        return max(0.0, total - 5.0)


def test_order_strategy_and_set_discount():
    s = Supplier("S001", "Test Supplier", "test@example.com")
    p = PhysicalProduct("P001", "Item", 100.0, 10, 1.0, s)
    order = Order("O001", BulkDiscount(200, 20))
    order.add_order_line(p, 3)  # 300.0
    assert order.calculate_total() == 280.0

    order.set_discount(PercentageDiscount(10))
    assert order.calculate_total() == 270.0


def test_extend_strategy_without_modifying_order():
    s = Supplier("S001", "Test Supplier", "test@example.com")
    p = DigitalProduct("D001", "App", 50.0, 10, 200.0, s)
    order = Order("O002", FixedFiveDollarOff())
    order.add_order_line(p, 1)
    assert order.calculate_total() == 45.0


def test_factory_creates_products_and_rejects_unknown_type():
    s = Supplier("S001", "Test Supplier", "test@example.com")
    p = ProductFactory.create_product("physical", "P001", "Lamp", 25.0, 5, s, weight=1.5)
    assert isinstance(p, PhysicalProduct)

    with pytest.raises(ValueError, match="Unknown product type"):
        ProductFactory.create_product("service", "S001", "Setup", 30.0, 2, s)


def test_validation_rules():
    s = Supplier("S001", "Test Supplier", "test@example.com")
    with pytest.raises(ValueError):
        PhysicalProduct("P001", "Bad Price", 0.0, 5, 1.0, s)
    with pytest.raises(ValueError):
        PhysicalProduct("P002", "Bad Stock", 10.0, -1, 1.0, s)

    p = PhysicalProduct("P003", "Valid", 10.0, 5, 1.0, s)
    order = Order("O003", NoDiscount())
    with pytest.raises(ValueError):
        order.add_order_line(p, 0)


def test_load_products_missing_and_mixed_rows(tmp_path, capsys):
    s = Supplier("S001", "Test Supplier", "test@example.com")
    inv = Inventory()

    load_products_from_csv(str(tmp_path / "missing.csv"), inv, s)
    out_missing = capsys.readouterr().out
    assert "Products file not found" in out_missing
    assert "Load attempt finished." in out_missing

    csv_file = tmp_path / "products.csv"
    csv_file.write_text(
        "product_type,product_id,name,price,stock_quantity\n"
        "physical,P001,Desk Lamp,25.00,10\n"
        "service,S001,Installation,30.00,5\n"
        "physical,P002,Office Chair,abc,3\n",
        encoding="utf-8",
    )
    load_products_from_csv(str(csv_file), inv, s)
    out_mixed = capsys.readouterr().out
    assert "1 products loaded." in out_mixed
    assert "Load attempt finished." in out_mixed
    assert inv.search_product("P001") is not None