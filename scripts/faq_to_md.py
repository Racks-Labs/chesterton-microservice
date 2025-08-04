import fitz  # PyMuPDF
import os
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def sanitize_filename(name):
    """
    Limpia una cadena de texto para que sea un nombre de archivo válido.
    """
    # Elimina el número inicial y el punto (ej. "1. ")
    name = re.sub(r'^\d{1,2}\.\s*', '', name)
    # Reemplaza caracteres no válidos por un guion bajo
    sanitized = re.sub(r'[\\/*?:"<>|\n]', '_', name)
    # Reemplaza múltiples espacios con un solo guion bajo
    sanitized = re.sub(r'\s+', '_', sanitized).lower()
    # Acorta el nombre para que no sea excesivamente largo
    return sanitized[:60]

def find_section(question_start_index, text, sections_map):
    """
    Encuentra a qué sección pertenece una pregunta basándose en su posición en el texto.
    """
    current_section = "desconocida"
    for section_name, start_index in sections_map.items():
        if start_index < question_start_index:
            current_section = section_name
        else:
            break
    return current_section

def extract_and_save_faqs(pdf_path, output_folder="faqs_markdown"):
    """
    Extrae preguntas numeradas de un PDF y las guarda en archivos Markdown.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ Error: No se encontró el archivo '{pdf_path}'. Asegúrate de que el nombre es correcto y está en la carpeta data/.")
        return

    print(f"📖 Procesando el archivo: {pdf_path}")
    os.makedirs(output_folder, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
    except Exception as e:
        print(f"❌ Error al leer el PDF: {e}")
        return

    # 1. Encontrar las secciones para usarlas como metadatos
    section_headers = ["GENERAL", "PARA PROPIETARIOS / VENDEDORES", "PARA COMPRADORES / INVERSORES", "DOCUMENTACIÓN Y PROCESOS", "CONTACTO Y ATENCIÓN"]
    sections_map = {}
    for header in section_headers:
        match = re.search(header, full_text)
        if match:
            sections_map[header.strip()] = match.start()
    
    # Ordenar el mapa de secciones por su posición de inicio
    sections_map = dict(sorted(sections_map.items(), key=lambda item: item[1]))

    # 2. Usar una expresión regular para encontrar todas las preguntas y sus respuestas
    # El patrón busca: (Pregunta numerada) (Respuesta hasta la siguiente pregunta o el final)
    pattern = re.compile(
        r"(^\d{1,2}\.\s*¿.*?\?)"  # Grupo 1: La pregunta (ej. "1. ¿Quiénes sois?")
        r"(.*?)"                  # Grupo 2: La respuesta (todo lo que sigue)
        r"(?=^\d{1,2}\.\s*¿|\Z)",  # Parar antes de la siguiente pregunta o al final del texto
        re.MULTILINE | re.DOTALL
    )

    matches = pattern.finditer(full_text)
    
    count = 0
    for match in matches:
        count += 1
        question = match.group(1).replace('\n', ' ').strip()
        answer = match.group(2).strip()
        
        # Mejorar formato de las listas
        answer = re.sub(r'•\s+', '\n- ', answer)
        answer = re.sub(r'Ο\s+', '\n  - ', answer)

        # Encontrar la sección de la pregunta actual
        question_index = match.start()
        section_name = find_section(question_index, full_text, sections_map)

        # Crear el nombre del archivo
        file_id = question.split('.')[0]
        filename = f"{file_id}_{sanitize_filename(question)}.md"
        filepath = os.path.join(output_folder, filename)

        # Crear el contenido del archivo Markdown
        markdown_content = f"""---
id: {file_id}
source: "{os.path.basename(pdf_path)}"
section: "{section_name}"
question: "{question.replace('"', '""')}"
---

{answer}
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✔️ Creado: {filename} (Sección: {section_name})")
        
    if count == 0:
        print("⚠️ No se encontró ninguna pregunta numerada con el formato '1. ¿...?' en el PDF.")
    else:
        print(f"\n✅ Proceso finalizado. Se han creado {count} archivos en la carpeta '{output_folder}'.")

if __name__ == '__main__':
    # Buscar el PDF en la carpeta data
    PDF_FILENAME = "data/faq_chesterton.pdf"
    OUTPUT_DIR = "faqs_markdown"
    extract_and_save_faqs(PDF_FILENAME, OUTPUT_DIR) 