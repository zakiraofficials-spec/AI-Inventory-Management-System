import os
from groq import Groq

class InventoryAI:
    """Optional Groq-powered inventory assistant."""
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()

    def available(self):
        return bool(self.api_key)

    def ask(self, prompt, inventory_context):
        if not self.available():
            raise RuntimeError("AI is not configured. Add GROQ_API_KEY to your .env file.")
        try:
            client = Groq(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content":
                     "You are a practical inventory analyst. Use only the supplied inventory data. "
                     "Be concise, explain assumptions, and do not invent sales or supplier data."},
                    {"role": "user", "content":
                     f"Inventory data:\n{inventory_context}\n\nRequest:\n{prompt}"}
                ],
                temperature=0.3,
                max_tokens=900
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"Groq request failed: {exc}") from exc

    def analyze(self, products):
        return self.ask(
            "Analyze stock health. Highlight low and out-of-stock products, unusual risks, "
            "and practical next steps. Do not assume sales velocity.",
            self._context(products)
        )

    def reorder_suggestions(self, products):
        return self.ask(
            "Suggest which products deserve a reorder review. Give a suggested quantity only "
            "as a clearly labelled estimate based on reorder level and current quantity; explain "
            "that actual demand and supplier lead time are not provided.",
            self._context(products)
        )

    def assistant(self, question, products):
        return self.ask(question, self._context(products))

    def description(self, name, category, price, details=""):
        return self.ask(
            f"Write a professional, factual product description (2-3 sentences) for "
            f"name={name}, category={category}, price={price}, supplied details={details!r}. "
            "Do not invent technical specifications or guarantees.",
            "No additional inventory context is needed."
        )

    @staticmethod
    def _context(products):
        if not products:
            return "No products are currently recorded."
        rows = []
        for p in products:
            rows.append({
                "id": p.product_id, "name": p.name, "category": p.category,
                "price": p.price, "quantity": p.quantity,
                "reorder_level": p.reorder_level, "status": p.stock_status(),
                "expiry_date": getattr(p, "expiry_date", None)
            })
        return str(rows)
