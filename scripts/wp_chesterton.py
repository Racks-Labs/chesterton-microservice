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

def fetch_wp_items(api_base, endpoint, per_page=50, max_retries=3):
    """
    Fetch all items from a WordPress REST API endpoint, handling pagination.
    Returns a list of item dicts.
    """
    url = f"{api_base.rstrip('/')}/{endpoint}"
    page = 1
    all_items = []

    while True:
        params = {'per_page': per_page, 'page': page}
        
        # Reintentos con backoff exponencial
        for attempt in range(max_retries):
            try:
                print(f"Fetching {endpoint} page {page} (attempt {attempt + 1}/{max_retries})...")
                
                # Timeouts más largos y configurables
                timeout_config = (30, 60)  # (connect_timeout, read_timeout)
                resp = requests.get(url, params=params, timeout=timeout_config, headers=HEADERS)
                resp.raise_for_status()
                break  # Si llegamos aquí, la petición fue exitosa
                
            except requests.exceptions.Timeout as e:
                print(f"[WARN] Timeout on {endpoint} page {page} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Backoff exponencial: 1, 2, 4 segundos
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"[ERROR] All retries failed for {endpoint} page {page}")
                    return all_items
                    
            except requests.RequestException as e:
                print(f"[WARN] Failed to fetch {endpoint} page {page} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"[ERROR] All retries failed for {endpoint} page {page}")
                    break

        data = None

        try:
            # Intento normal primero
            data = resp.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[WARN] Response for '{endpoint}' is not valid JSON. Attempting to clean it...")
            # El servidor envía HTML antes del JSON. Vamos a buscar el inicio del JSON.
            response_text = resp.text
            json_start_index = response_text.find('[')

            if json_start_index != -1:
                # Se encontró el inicio de un array JSON. Intentamos decodificar desde ahí.
                clean_json_str = response_text[json_start_index:]
                try:
                    data = json.loads(clean_json_str)
                    print(f"[INFO] Successfully cleaned and parsed JSON for '{endpoint}'.")
                except json.JSONDecodeError:
                    print(f"[ERROR] Failed to parse JSON for '{endpoint}' even after cleaning.")
                    print(f"Status Code: {resp.status_code}")
                    print(f"Response Text (first 500 chars): {resp.text[:500]}...")
                    break
            else:
                # No se encontró ni siquiera un '['. La respuesta es irreparable.
                print(f"[ERROR] Could not find start of JSON array ('[') in the response for '{endpoint}'.")
                print(f"Status Code: {resp.status_code}")
                print(f"Response Text (first 500 chars): {resp.text[:500]}...")
                break

        if not isinstance(data, list) or not data:
            print(f"[INFO] No more data for {endpoint} (page {page})")
            break

        all_items.extend(data)
        print(f"[INFO] Fetched {len(data)} items from {endpoint} page {page}")

        if 'X-WP-TotalPages' not in resp.headers:
            print("[WARN] 'X-WP-TotalPages' header not found. Assuming single page.")
            break
            
        total_pages = int(resp.headers.get('X-WP-TotalPages', 0))
        if page >= total_pages:
            print(f"[INFO] Reached last page ({total_pages}) for {endpoint}")
            break
        page += 1
        
        # Pausa entre páginas para no sobrecargar el servidor
        time.sleep(1)

    return all_items


def save_markdown(obj, folder, filename=None, front_matter=True):
    """
    Save a WordPress object dict to a Markdown file.
    Converts HTML content to Markdown and prepends optional YAML front-matter.
    """
    os.makedirs(folder, exist_ok=True)
    fname = filename or obj.get('slug') or str(obj.get('id'))
    # Asegurarse de que fname sea un string válido para un nombre de archivo
    if not fname:
        fname = str(obj.get('id', 'unknown_id'))
    
    filepath = os.path.join(folder, f"{fname}.md")

    lines = []
    if front_matter:
        lines.append("---")
        title_rendered = obj.get('title', {}).get('rendered')
        if title_rendered:
            # Escapar comillas dobles dentro del título para que el YAML sea válido
            safe_title = title_rendered.replace('"', '\\"')
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

    raw_html = obj.get('content', {}).get('rendered') or ''
    md_content = md(raw_html, heading_style="ATX")
    lines.append(md_content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


if __name__ == '__main__':
    # Usar variable de entorno para la URL del sitio
    site_url = os.getenv("WORDPRESS_SITE_URL", "https://chestertons-atomiun.com")
    api_base = f"{site_url.rstrip('/')}/wp-json/wp/v2"

    endpoints = {
        'posts': 'posts',
        'pages': 'pages',
    }

    for endpoint, folder in endpoints.items():
        print(f"Fetching {endpoint}...")
        items = fetch_wp_items(api_base, endpoint, per_page=25)  # Reducir per_page para evitar timeouts
        if items:
            for item in items:
                save_markdown(item, folder)
            print(f"Saved {len(items)} items to ./{folder}/")
        else:
            print(f"No items found or failed to fetch for endpoint '{endpoint}'.")

    print("All done.") 