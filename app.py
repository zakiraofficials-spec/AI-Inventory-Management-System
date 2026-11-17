import os
from datetime import date
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from models import Product, PerishableProduct
from inventory import InventoryManager
from ai_helper import InventoryAI

load_dotenv()
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
inventory = InventoryManager()
ai = InventoryAI()

def product_payload(product):
    data = product.to_dict()
    data["total_value"] = product.total_value()
    data["stock_status"] = product.stock_status()
    return data

def read_product(data, product_id=None):
    required = ["name", "category", "price", "quantity"]
    for field in required:
        if field not in data or str(data[field]).strip() == "":
            raise ValueError(f"{field.replace('_', ' ').title()} is required.")
    name, category = str(data["name"]).strip(), str(data["category"]).strip()
    if len(name) > 100 or len(category) > 60:
        raise ValueError("Name or category is too long.")
    try:
        price = float(data["price"])
        quantity = int(data["quantity"])
        reorder = int(data.get("reorder_level", 5))
    except (TypeError, ValueError):
        raise ValueError("Price must be numeric; quantity and reorder level must be whole numbers.")
    if price < 0 or quantity < 0 or reorder < 0:
        raise ValueError("Price, quantity and reorder level cannot be negative.")
    if quantity > 10**9 or price > 10**12:
        raise ValueError("The supplied number is too large.")
    pid = str(product_id or data.get("product_id", "")).strip()
    if not pid:
        pid = "P" + str(int(__import__("time").time() * 1000))
    description = str(data.get("description", "")).strip()[:1000]
    if data.get("type") == "perishable":
        expiry = str(data.get("expiry_date", "")).strip()
        if expiry:
            try:
                date.fromisoformat(expiry)
            except ValueError:
                raise ValueError("Expiry date must use YYYY-MM-DD format.")
        return PerishableProduct(pid, name, category, price, quantity,
                                  reorder, description, expiry)
    return Product(pid, name, category, price, quantity, reorder, description)

@app.get("/")
def home():
    return render_template("index.html", ai_available=ai.available())

@app.get("/api/products")
def list_products():
    return jsonify([product_payload(p) for p in inventory.search(request.args.get("q", ""))])

@app.post("/api/products")
def create_product():
    try:
        product = read_product(request.get_json(silent=True) or {})
        inventory.add(product)
        return jsonify(product_payload(product)), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

@app.put("/api/products/<product_id>")
def edit_product(product_id):
    try:
        product = read_product(request.get_json(silent=True) or {}, product_id)
        inventory.update(product_id, product)
        return jsonify(product_payload(product))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

@app.delete("/api/products/<product_id>")
def remove_product(product_id):
    try:
        inventory.delete(product_id)
        return jsonify({"message": "Product deleted."})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

@app.get("/api/stats")
def stats():
    return jsonify(inventory.statistics())

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "ai_configured": ai.available()})

@app.post("/api/ai/<action>")
def ai_action(action):
    data = request.get_json(silent=True) or {}
    try:
        products = inventory.all_products()
        if action == "analysis":
            answer = ai.analyze(products)
        elif action == "reorder":
            answer = ai.reorder_suggestions(products)
        elif action == "assistant":
            question = str(data.get("question", "")).strip()
            if not question or len(question) > 500:
                return jsonify({"error": "Enter a question of up to 500 characters."}), 400
            answer = ai.assistant(question, products)
        elif action == "description":
            name = str(data.get("name", "")).strip()
            category = str(data.get("category", "")).strip()
            if not name or not category:
                return jsonify({"error": "Product name and category are required."}), 400
            answer = ai.description(name[:100], category[:60],
                                    data.get("price", "not supplied"),
                                    str(data.get("details", ""))[:500])
        else:
            return jsonify({"error": "Unknown AI action."}), 404
        return jsonify({"answer": answer})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found."}), 404
    return "Page not found", 404

@app.errorhandler(500)
def server_error(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "An unexpected server error occurred."}), 500
    return "An unexpected server error occurred.", 500

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes"))
