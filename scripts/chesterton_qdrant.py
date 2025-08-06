import os
import yaml
import glob
import uuid
from dotenv import load_dotenv

from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

# Cargar variables de entorno
load_dotenv()

# —————— 1) CONFIGURACIÓN ——————
# Usar variables de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = os.getenv("QDRANT_COLLECTION", "chesterton")

# Configuración del modelo de embeddings
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()  # "google" o "openai"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")  # Modelo específico
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))  # Dimensiones del vector

# Configurar las API keys
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def get_embedder():
    """
    Crea y retorna el embedder configurado según las variables de entorno.
    """
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
    """
    Trunca un vector a las dimensiones especificadas.
    """
    if len(vector) <= target_dimensions:
        return vector
    
    print(f"🔧 Truncando vector de {len(vector)} a {target_dimensions} dimensiones")
    return vector[:target_dimensions]

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
    # Verificar configuración
    if EMBEDDING_PROVIDER == "google" and (not GOOGLE_API_KEY or GOOGLE_API_KEY == "tu_clave_de_google_ai_aqui"):
        print("❌ Error: Por favor, establece tu GOOGLE_API_KEY en el archivo .env")
        return
    
    if EMBEDDING_PROVIDER == "openai" and (not OPENAI_API_KEY or OPENAI_API_KEY == "tu_clave_de_openai_aqui"):
        print("❌ Error: Por favor, establece tu OPENAI_API_KEY en el archivo .env")
        return

    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Error: Por favor, configura QDRANT_URL y QDRANT_API_KEY en el archivo .env")
        return

    print(f"🚀 Iniciando indexación con {EMBEDDING_PROVIDER.upper()} embeddings")
    print(f"📋 Configuración:")
    print(f"   - Proveedor: {EMBEDDING_PROVIDER}")
    print(f"   - Modelo: {EMBEDDING_MODEL}")
    print(f"   - Dimensiones: {EMBEDDING_DIMENSIONS}")

    try:
        embedder = get_embedder()
    except Exception as e:
        print(f"❌ Error al inicializar el embedder: {e}")
        return

    print(f"Conectando a Qdrant en {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    try:
        collections_response = client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        if COLLECTION not in collection_names:
            print(f"La colección '{COLLECTION}' no existe. Creándola ahora...")
            client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=EMBEDDING_DIMENSIONS, distance=Distance.COSINE)
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
        # Truncar vector si es necesario
        truncated_vector = truncate_vector(emb, EMBEDDING_DIMENSIONS)
        
        # Generar siempre un UUID estable basado en la ruta del archivo
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, payload["metadata"]["source_path"]))
        
        points.append(
            PointStruct(id=point_id, vector=truncated_vector, payload=payload)
        )

    print(f"⬆️ Cargando {len(points)} puntos en la colección '{COLLECTION}'...")
    try:
        # Usar wait=True para esperar a que la operación se complete
        client.upsert(collection_name=COLLECTION, points=points, wait=True)
        print(f"✅ ¡Éxito! Se han indexado {len(points)} documentos en la colección '{COLLECTION}'.")
        print(f"📊 Resumen:")
        print(f"   - Proveedor: {EMBEDDING_PROVIDER}")
        print(f"   - Modelo: {EMBEDDING_MODEL}")
        print(f"   - Dimensiones: {EMBEDDING_DIMENSIONS}")
        print(f"   - Documentos procesados: {len(points)}")
    except Exception as e:
        print(f"❌ Error durante la carga a Qdrant: {e}")
        # Opcional: imprimir más detalles si el error es complejo
        if hasattr(e, 'response'):
             print(f"Raw response content:\n{e.response.content}")


if __name__ == "__main__":
    main() 