import os
import yaml
import glob
import uuid
from dotenv import load_dotenv

# llama-index imports
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

# qdrant imports
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

# Cargar variables de entorno
load_dotenv()

# --- 1) CONFIGURACIÓN ---
# Usar variables de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = os.getenv("QDRANT_COLLECTION", "chesterton")

# Configuración del modelo de embeddings
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

# Límite de tokens aproximado. 8192 para text-embedding-3-small.
# Usamos un límite de caracteres conservador como proxy. 1 token ~= 4 caracteres.
# 8000 tokens * 4 chars/token = 32000. Lo dejamos en 28000 para tener margen.
MAX_CHARS_LIMIT = 28000

# Configurar las API keys
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- 2) FUNCIONES AUXILIARES ---

def get_embedder():
    """Crea y retorna el embedder configurado."""
    if EMBEDDING_PROVIDER == "google":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY no está configurada")
        print(f"🔧 Usando Google AI Embeddings con modelo: {EMBEDDING_MODEL}")
        return GoogleGenAIEmbedding(model_name=EMBEDDING_MODEL)
    
    elif EMBEDDING_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada")
        print(f"🔧 Usando OpenAI Embeddings con modelo: {EMBEDDING_MODEL}")
        return OpenAIEmbedding(model=EMBEDDING_MODEL)
    
    else:
        raise ValueError(f"Proveedor de embeddings no soportado: {EMBEDDING_PROVIDER}")

def truncate_vector(vector, target_dimensions):
    """Trunca un vector a las dimensiones especificadas."""
    if len(vector) <= target_dimensions:
        return vector
    return vector[:target_dimensions]

def parse_md_file(path):
    """Parsea un archivo Markdown con front-matter YAML."""
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

# --- 3) FUNCIÓN PRINCIPAL ---

def main():
    # ... (verificación de configuración sin cambios)

    try:
        embedder = get_embedder()
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        # ... (creación de colección sin cambios)
    except Exception as e:
        print(f"❌ Error de configuración inicial: {e}")
        return

    # Buscar archivos
    print("Buscando archivos Markdown en 'faqs_markdown/' y 'pages/'...")
    paths = (
        glob.glob("faqs_markdown/*.md", recursive=True) +
        glob.glob("pages/**/*.md", recursive=True)
    )
    if not paths:
        print("✅ No se encontraron archivos para procesar.")
        return
        
    print(f"📂 Encontrados {len(paths)} archivos.")

    docs_for_embedding = []
    payloads = []

    for path in paths:
        content, meta = parse_md_file(path)
        
        question = meta.get("question", "")
        combined_text = f"Pregunta: {question}\nRespuesta: {content}" if question else content
        
        # --- TRUNCADO SIMPLE ---
        if len(combined_text) > MAX_CHARS_LIMIT:
            print(f"⚠️  Documento '{path}' demasiado largo ({len(combined_text)} caracteres). Truncando a {MAX_CHARS_LIMIT} caracteres.")
            combined_text = combined_text[:MAX_CHARS_LIMIT]

        docs_for_embedding.append(combined_text)
        payloads.append({"content": content, "metadata": meta})

    print(f"🧠 Generando embeddings para {len(docs_for_embedding)} documentos...")
    try:
        embeddings = embedder.get_text_embedding_batch(docs_for_embedding, show_progress=True)
    except Exception as e:
        print(f"❌ Error fatal al generar embeddings: {e}")
        return

    points = []
    for payload, emb in zip(payloads, embeddings):
        truncated_vector = truncate_vector(emb, EMBEDDING_DIMENSIONS)
        
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, payload["metadata"]["source_path"]))
        
        points.append(
            PointStruct(id=point_id, vector=truncated_vector, payload=payload)
        )

    print(f"⬆️ Cargando {len(points)} puntos en la colección '{COLLECTION}'...")
    try:
        client.upsert(collection_name=COLLECTION, points=points, wait=True)
        print(f"✅ ¡Éxito! Se han indexado {len(points)} documentos en la colección '{COLLECTION}'.")
        # ... (resumen sin cambios)
    except Exception as e:
        print(f"❌ Error durante la carga a Qdrant: {e}")
        if hasattr(e, 'response'):
             print(f"Raw response content:\n{e.response.content}")


if __name__ == "__main__":
    main()
