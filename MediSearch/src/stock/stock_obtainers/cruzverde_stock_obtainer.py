import requests
import json
import re
from playwright.sync_api import sync_playwright

# 🔐 Obtener cookie de sesión válida para la API
def get_cruzverde_cookie():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        # Visita una página cualquiera para obtener cookies válidas
        page.goto("https://www.cruzverde.cl/ibuprofeno-600-mg-20-comprimidos/273362.html", wait_until="networkidle")
        cookies = context.cookies()
        browser.close()
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

# 🔢 Extraer ID del producto desde la URL
def extract_product_id(url):
    match = re.search(r'/(\d+)\.html', url)
    return match.group(1) if match else None

# 🚀 Función principal compatible con stock_checker
def obtener_stock(url_producto: str, comuna: str) -> str:
    product_id = extract_product_id(url_producto)
    if not product_id:
        return "❌ No se pudo extraer el product_id desde la URL."

    comuna_formateada = comuna.strip().lower().replace(" ", "")
    api_url = f"https://api.cruzverde.cl/product-service/products/stores-stock?id={comuna_formateada}&productId={product_id}"

    cookie = get_cruzverde_cookie()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Cookie": cookie
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        stores = data.get("stores", [])
        if not stores:
            return "❌ No se encontraron tiendas o no hay stock en la comuna."

        resultado = f"📍 Stock en comuna: {comuna.capitalize()}\n"
        for store in stores:
            address = store.get("address", "Dirección desconocida")
            stock = store.get("stock", "?")
            resultado += f"{address} → Stock: {stock}\n"
        return resultado.strip()

    except Exception as e:
        return f"❌ Error al consultar la API: {e}"
