import os
import yaml
import glob
import uuid
from dotenv import load_dotenv

from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

# Cargar variables de entorno
load_dotenv()

# —————— 1) CONFIGURACIÓN ——————
# Usar variables de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = os.getenv("QDRANT_COLLECTION", "chesterton")

# Configurar la API key de Google
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def parse_md_file(path):
    """
    Parsea un archivo Markdown con front-matter YAML.
    Devuelve el contenido y los metadatos.
    """
    with open(path, encoding="utf-8") as f:
        full_content = f.read()

    parts = full_content.split('---', 2)
    meta = {}
    content = ""

    if len(parts) >= 3:
        raw_yaml = parts[1]
        content = parts[2].strip()
        try:
            meta = yaml.safe_load(raw_yaml) or {}
        except yaml.YAMLError as e:
            print(f"Advertencia: No se pudo parsear el YAML en {path}: {e}")
    else:
        content = full_content.strip()

    meta["filename"] = os.path.basename(path)
    meta["source_path"] = path
    return content, meta


def main():
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "tu_clave_de_google_ai_aqui":
        print("❌ Error: Por favor, establece tu GOOGLE_API_KEY en el archivo .env")
        return

    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Error: Por favor, configura QDRANT_URL y QDRANT_API_KEY en el archivo .env")
        return

    print("Inicializando el modelo de embeddings de Google...")
    embedder = GoogleGenAIEmbedding(model_name="text-embedding-004")

    print(f"Conectando a Qdrant en {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    try:
        collections_response = client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        if COLLECTION not in collection_names:
            print(f"La colección '{COLLECTION}' no existe. Creándola ahora...")
            client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
            print(f"✅ Colección '{COLLECTION}' creada con éxito.")
        else:
            print(f"👍 La colección '{COLLECTION}' ya existe.")
    except Exception as e:
        print(f"❌ Error al interactuar con las colecciones de Qdrant: {e}")
        return

    # Buscar archivos en carpetas específicas (solo FAQs y páginas)
    print("Buscando archivos Markdown en 'faqs_markdown/' y 'pages/'...")
    paths = (
        glob.glob("faqs_markdown/*.md", recursive=True) +
        glob.glob("pages/**/*.md", recursive=True)
    )
    
    if not paths:
        print("❌ No se encontraron archivos Markdown en ninguna de las carpetas.")
        return
        
    print(f"📂 Encontrados {len(paths)} archivos Markdown en total.")

    docs_for_embedding = []
    payloads = []

    for path in paths:
        content, meta = parse_md_file(path)
        
        # Lógica adaptativa: Si es una FAQ, combinar pregunta y respuesta.
        # Si no, usar solo el contenido.
        question = meta.get("question", "")
        if question:
            # Es una FAQ
            combined_text = f"Pregunta: {question}\nRespuesta: {content}"
        else:
            # Es un post o una página
            combined_text = content
            
        docs_for_embedding.append(combined_text)
        payloads.append({"content": content, "metadata": meta})

    print(f"🧠 Generando embeddings para {len(docs_for_embedding)} documentos...")
    embeddings = embedder.get_text_embedding_batch(docs_for_embedding, show_progress=True)

    points = []
    for payload, emb in zip(payloads, embeddings):
        # Generar siempre un UUID estable basado en la ruta del archivo
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, payload["metadata"]["source_path"]))
        
        points.append(
            PointStruct(id=point_id, vector=emb, payload=payload)
        )

    print(f"⬆️ Cargando {len(points)} puntos en la colección '{COLLECTION}'...")
    try:
        # Usar wait=True para esperar a que la operación se complete
        client.upsert(collection_name=COLLECTION, points=points, wait=True)
        print(f"✅ ¡Éxito! Se han indexado {len(points)} documentos en la colección '{COLLECTION}'.")
    except Exception as e:
        print(f"❌ Error durante la carga a Qdrant: {e}")
        # Opcional: imprimir más detalles si el error es complejo
        if hasattr(e, 'response'):
             print(f"Raw response content:\n{e.response.content}")


if __name__ == "__main__":
    main() 