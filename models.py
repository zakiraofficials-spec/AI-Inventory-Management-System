from datetime import date

class Product:
    """Represents a standard inventory product."""
    def __init__(self, product_id, name, category, price, quantity,
                 reorder_level=5, description=""):
        self.product_id = str(product_id).strip()
        self.name = str(name).strip()
        self.category = str(category).strip()
        self.price = float(price)
        self.quantity = int(quantity)
        self.reorder_level = int(reorder_level)
        self.description = str(description).strip()

    def total_value(self):
        return round(self.price * self.quantity, 2)

    def stock_status(self):
        if self.quantity <= 0:
            return "Out of Stock"
        if self.quantity <= self.reorder_level:
            return "Low Stock"
        return "In Stock"

    def to_dict(self):
        return {
            "type": "standard", "product_id": self.product_id,
            "name": self.name, "category": self.category,
            "price": self.price, "quantity": self.quantity,
            "reorder_level": self.reorder_level,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        if data.get("type") == "perishable":
            return PerishableProduct(
                data["product_id"], data["name"], data["category"],
                data["price"], data["quantity"], data.get("reorder_level", 5),
                data.get("description", ""), data.get("expiry_date", "")
            )
        return cls(data["product_id"], data["name"], data["category"],
                   data["price"], data["quantity"],
                   data.get("reorder_level", 5), data.get("description", ""))


class PerishableProduct(Product):
    """Product with an expiry date."""
    def __init__(self, product_id, name, category, price, quantity,
                 reorder_level=5, description="", expiry_date=""):
        super().__init__(product_id, name, category, price, quantity,
                         reorder_level, description)
        self.expiry_date = str(expiry_date).strip()

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "perishable"
        data["expiry_date"] = self.expiry_date
        return data
