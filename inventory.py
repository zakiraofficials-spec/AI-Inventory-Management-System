import json
import os
from pathlib import Path
from models import Product

class InventoryManager:
    """Handles inventory CRUD, persistence, search and statistics."""
    def __init__(self, data_file=None):
        default_file = Path(__file__).parent / "data" / "products.json"
        self.data_file = Path(data_file or os.getenv("INVENTORY_DATA_FILE", default_file))
        self.products = []
        self.load()

    def load(self):
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.data_file.exists():
                self.products = []
                self.save()
                return
            with self.data_file.open("r", encoding="utf-8") as file:
                records = json.load(file)
            self.products = [Product.from_dict(item) for item in records]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.products = []

    def save(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.data_file.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump([p.to_dict() for p in self.products], file, indent=2)
        temporary.replace(self.data_file)

    def all_products(self):
        return sorted(self.products, key=lambda p: p.name.lower())

    def get(self, product_id):
        return next((p for p in self.products if p.product_id == str(product_id)), None)

    def add(self, product):
        if self.get(product.product_id):
            raise ValueError("A product with this ID already exists.")
        self.products.append(product)
        self.save()
        return product

    def update(self, product_id, updated_product):
        old = self.get(product_id)
        if not old:
            raise ValueError("Product not found.")
        updated_product.product_id = str(product_id)
        self.products[self.products.index(old)] = updated_product
        self.save()
        return updated_product

    def delete(self, product_id):
        product = self.get(product_id)
        if not product:
            raise ValueError("Product not found.")
        self.products.remove(product)
        self.save()

    def search(self, query):
        query = str(query).lower().strip()
        if not query:
            return self.all_products()
        return [p for p in self.all_products()
                if query in p.product_id.lower()
                or query in p.name.lower()
                or query in p.category.lower()]

    def low_stock(self):
        return [p for p in self.all_products()
                if 0 < p.quantity <= p.reorder_level]

    def out_of_stock(self):
        return [p for p in self.all_products() if p.quantity <= 0]

    def statistics(self):
        return {
            "total_products": len(self.products),
            "total_units": sum(p.quantity for p in self.products),
            "inventory_value": round(sum(p.total_value() for p in self.products), 2),
            "low_stock": len(self.low_stock()),
            "out_of_stock": len(self.out_of_stock())
        }
