
import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SHOPIFY_ACCESS_TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN')
SHOPIFY_STORE_URL = os.environ.get('SHOPIFY_STORE_URL')

def get_shopify_data(endpoint, params=None):
    """Pobiera dane z API Shopify."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/{endpoint}"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych z Shopify: {e}")
        return None

def process_products(products):
    """Formatuje listę produktów dla Dialogflow."""
    if not products:
        return "Nie znaleziono żadnych produktów."

    product_list = "\n".join([f"- {p['title']} (ID: {p['id']})" for p in products])
    return f"Oto lista produktów:\n{product_list}"

def process_orders(orders):
    """Formatuje listę zamówień dla Dialogflow."""
    if not orders:
        return "Nie znaleziono żadnych zamówień."

    order_list = "\n".join([f"- Zamówienie ID: {o['id']}, Email: {o['email']}, Cena: {o['total_price']} {o['currency']}" for o in orders])
    return f"Oto lista zamówień:\n{order_list}"

@app.route("/", methods=['POST'])
def main():
    """Główna funkcja webhooka."""
    req = request.get_json(silent=True, force=True)
    intent_name = req.get('queryResult').get('intent').get('displayName')

    if intent_name == "GetProducts":
        products_data = get_shopify_data("products.json")
        if products_data and 'products' in products_data:
            response_text = process_products(products_data['products'])
        else:
            response_text = "Wystąpił problem z pobraniem listy produktów."

    elif intent_name == "GetOrders":
        orders_data = get_shopify_data("orders.json")
        if orders_data and 'orders' in orders_data:
            response_text = process_orders(orders_data['orders'])
        else:
            response_text = "Wystąpił problem z pobraniem listy zamówień."

    else:
        response_text = "Przepraszam, nie rozumiem. Spróbuj ponownie."

    fulfillment_text = {"fulfillmentText": response_text}
    return jsonify(fulfillment_text)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
