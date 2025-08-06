import requests
import os
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import json
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_wp_items(api_base, endpoint, per_page=25, max_retries=3):
    """
    Fetch all items from a WordPress REST API endpoint, handling pagination robustly.
    Stops when an empty list of items is returned.
    """
    url = f"{api_base.rstrip('/')}/{endpoint}"
    page = 1
    all_items = []

    while True:
        params = {'per_page': per_page, 'page': page}
        
        resp = None
        for attempt in range(max_retries):
            try:
                print(f"Fetching {endpoint} page {page} (attempt {attempt + 1}/{max_retries})...")
                timeout_config = (30, 60)
                resp = requests.get(url, params=params, timeout=timeout_config, headers=HEADERS)
                resp.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"[WARN] Failed to fetch {endpoint} page {page} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print(f"[ERROR] All retries failed for {endpoint} page {page}")
                    return all_items # Devuelve lo que ha podido recoger

        if resp is None:
            break # Si todas las peticiones fallaron

        data = None
        try:
            data = resp.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[WARN] Response for '{endpoint}' is not valid JSON. Attempting to clean it...")
            response_text = resp.text
            json_start_index = response_text.find('[')

            if json_start_index != -1:
                clean_json_str = response_text[json_start_index:]
                try:
                    data = json.loads(clean_json_str)
                    print(f"[INFO] Successfully cleaned and parsed JSON for '{endpoint}'.")
                except json.JSONDecodeError:
                    print(f"[ERROR] Failed to parse JSON for '{endpoint}' even after cleaning.")
                    break
            else:
                print(f"[ERROR] Could not find start of JSON array ('[') in the response for '{endpoint}'.")
                break

        # --- LÓGICA MEJORADA ---
        # Si la API devuelve algo que no es una lista, o una lista vacía, hemos terminado.
        if not isinstance(data, list) or not data:
            print(f"[INFO] Reached the end of content for {endpoint} at page {page}.")
            break

        all_items.extend(data)
        print(f"[INFO] Fetched {len(data)} items from {endpoint} page {page}")
        
        page += 1
        time.sleep(1) # Pausa entre páginas

    return all_items


def save_markdown(obj, folder, filename=None, front_matter=True):
    """
    Save a WordPress object dict to a Markdown file.
    """
    os.makedirs(folder, exist_ok=True)
    fname = filename or obj.get('slug') or str(obj.get('id', 'unknown_id'))
    filepath = os.path.join(folder, f"{fname}.md")

    lines = []
    if front_matter:
        lines.append("---")
        if title := obj.get('title', {}).get('rendered'):
            safe_title = title.replace('"', '\\"')
            lines.append(f'title: "{safe_title}"')
        if slug := obj.get('slug'):
            lines.append(f"slug: {slug}")
        if obj.get('id') is not None:
            lines.append(f"id: {obj['id']}")
        if date := obj.get('date'):
            lines.append(f"date: {date}")
        if modified := obj.get('modified'):
            lines.append(f"modified: {modified}")
        if link := obj.get('link'):
            lines.append(f"url: {link}")
        lines.append("---")

    raw_html = obj.get('content', {}).get('rendered', '')
    md_content = md(raw_html, heading_style="ATX")
    lines.append(md_content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


if __name__ == '__main__':
    site_url = os.getenv("WORDPRESS_SITE_URL", "https://chestertons-atomiun.com")
    api_base = f"{site_url.rstrip('/')}/wp-json/wp/v2"

    endpoints = {
        'posts': 'posts',
        'pages': 'pages',
    }

    for endpoint, folder in endpoints.items():
        print(f"Fetching {endpoint}...")
        items = fetch_wp_items(api_base, endpoint)
        if items:
            for item in items:
                save_markdown(item, folder)
            print(f"Saved {len(items)} items to ./{folder}/")
        else:
            print(f"No items found or failed to fetch for endpoint '{endpoint}'.")

    print("All done.")
