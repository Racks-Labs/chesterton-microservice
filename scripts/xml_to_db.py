import os
import requests
import psycopg2
import xml.etree.ElementTree as ET
import json
from psycopg2 import sql
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN ---
XML_URL = os.getenv("XML_URL", "https://atomiunservices.mobiliagestion.es/ExportarInmueblesMobilia/fa557043af982e6b3a5a4e53f86b3724.xml")
DB_URL = os.getenv("DB_URL")

# --- FUNCIONES AUXILIARES ---

def obtener_texto_safe(elemento, default=None):
    return elemento.text.strip() if elemento is not None and elemento.text else default

def obtener_int_safe(elemento, default=None):
    try:
        return int(obtener_texto_safe(elemento))
    except (ValueError, TypeError):
        return default

def obtener_numeric_safe(elemento, default=None):
    try:
        text_value = obtener_texto_safe(elemento, '0').replace(',', '.')
        return float(text_value)
    except (ValueError, TypeError):
        return default

def obtener_bool_safe(elemento, default=False):
    return obtener_texto_safe(elemento) == '1'

def obtener_timestamp_safe(elemento, default=None):
    text_value = obtener_texto_safe(elemento)
    if not text_value:
        return default
    try:
        return datetime.strptime(text_value, '%d-%m-%Y %H:%M:%S')
    except (ValueError, TypeError):
        return default

def crear_esquema_db(cursor):
    """Crea las tablas necesarias en la base de datos, borrándolas si ya existen."""
    print("Borrando tablas antiguas si existen...")
    cursor.execute("""
        DROP TABLE IF EXISTS propiedad_caracteristicas CASCADE;
        DROP TABLE IF EXISTS caracteristicas CASCADE;
        DROP TABLE IF EXISTS fotos CASCADE;
        DROP TABLE IF EXISTS propiedades CASCADE;
        DROP TABLE IF EXISTS propiedades_min CASCADE; 
    """)

    print("Creando nuevas tablas...")
    # Esquema definitivo con TODOS los campos
    cursor.execute("""
        CREATE TABLE propiedades (
            -- IDs y Referencias
            id NUMERIC PRIMARY KEY,
            referencia TEXT UNIQUE NOT NULL,
            agencia_id TEXT,
            url TEXT,

            -- Fechas
            fecha_creacion TIMESTAMP WITH TIME ZONE,
            fecha_publicacion TIMESTAMP WITH TIME ZONE,
            fecha_modificacion TIMESTAMP WITH TIME ZONE,
            
            -- Clasificación del Inmueble
            grupo_inmueble TEXT,
            familia TEXT,
            tipo TEXT,
            subtipo TEXT,
            destacado BOOLEAN,
            estado TEXT,
            uso_inmueble TEXT,
            ultima_actividad TEXT,
            
            -- Descripciones y Títulos
            titulo TEXT,
            descripcion TEXT,
            descripcion_ampliada TEXT,
            
            -- Operaciones y Datos Financieros
            operaciones JSONB,
            ibi NUMERIC,
            gastos_comunidad NUMERIC,
            
            -- Localización
            provincia TEXT,
            poblacion TEXT,
            zona TEXT,
            subzona TEXT,
            urbanizacion TEXT,
            direccion TEXT,
            numero TEXT,
            escalera TEXT,
            planta TEXT,
            letra TEXT,
            codigo_postal TEXT,
            latitud NUMERIC,
            longitud NUMERIC,
            
            -- Características Físicas
            superficie_construida NUMERIC,
            superficie_util NUMERIC,
            superficie_parcela NUMERIC,
            num_habitaciones INTEGER,
            num_banos INTEGER,
            num_aseos INTEGER,
            num_plantas INTEGER,
            ano_construccion INTEGER,
            estado_conservacion TEXT,
            
            -- Características Adicionales
            equipamiento TEXT,
            calefaccion TEXT,
            aire_acondicionado TEXT,
            ascensor BOOLEAN,
            parking BOOLEAN,
            trastero BOOLEAN,
            terraza BOOLEAN,
            jardin BOOLEAN,
            piscina BOOLEAN,
            
            -- Información Adicional
            caracteristicas JSONB,
            fotos JSONB,
            documentos JSONB,
            
            -- Metadatos
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Crear índices para mejorar el rendimiento
    cursor.execute("""
        CREATE INDEX idx_propiedades_referencia ON propiedades(referencia);
        CREATE INDEX idx_propiedades_tipo ON propiedades(tipo);
        CREATE INDEX idx_propiedades_poblacion ON propiedades(poblacion);
        CREATE INDEX idx_propiedades_operaciones ON propiedades USING GIN (operaciones);
    """)

def procesar_xml_e_insertar(cursor, xml_content):
    """Procesa el contenido XML e inserta los datos en la base de datos."""
    try:
        root = ET.fromstring(xml_content)
        
        def extract_json_list(xpath, mapping_func):
            """Extrae una lista de elementos y los convierte a JSON."""
            elements = root.findall(xpath)
            return [mapping_func(elem) for elem in elements]
        
        # Procesar cada propiedad
        propiedades = root.findall('.//Inmueble')
        print(f"Procesando {len(propiedades)} propiedades...")
        
        for i, prop in enumerate(propiedades, 1):
            if i % 100 == 0:
                print(f"Procesadas {i} propiedades...")
            
            # Extraer datos básicos
            id_prop = obtener_int_safe(prop.find('ID'))
            referencia = obtener_texto_safe(prop.find('Referencia'))
            
            if not id_prop or not referencia:
                continue
            
            # Extraer operaciones
            operaciones = {}
            for operacion in prop.findall('.//Operacion'):
                tipo_operacion = obtener_texto_safe(operacion.find('TipoOperacion'))
                if tipo_operacion:
                    operaciones[tipo_operacion] = {
                        'precio': obtener_numeric_safe(operacion.find('Precio')),
                        'moneda': obtener_texto_safe(operacion.find('Moneda')),
                        'gastos': obtener_numeric_safe(operacion.find('Gastos')),
                        'disponible': obtener_bool_safe(operacion.find('Disponible'))
                    }
            
            # Extraer características
            caracteristicas = {}
            for carac in prop.findall('.//Caracteristica'):
                nombre = obtener_texto_safe(carac.find('Nombre'))
                valor = obtener_texto_safe(carac.find('Valor'))
                if nombre:
                    caracteristicas[nombre] = valor
            
            # Extraer fotos
            fotos = []
            for foto in prop.findall('.//Foto'):
                fotos.append({
                    'url': obtener_texto_safe(foto.find('URL')),
                    'descripcion': obtener_texto_safe(foto.find('Descripcion')),
                    'principal': obtener_bool_safe(foto.find('Principal'))
                })
            
            # Preparar datos para inserción
            datos = {
                'id': id_prop,
                'referencia': referencia,
                'agencia_id': obtener_texto_safe(prop.find('AgenciaID')),
                'url': obtener_texto_safe(prop.find('URL')),
                'fecha_creacion': obtener_timestamp_safe(prop.find('FechaCreacion')),
                'fecha_publicacion': obtener_timestamp_safe(prop.find('Fecha')),
                'fecha_modificacion': obtener_timestamp_safe(prop.find('FechaModificacion')),
                'grupo_inmueble': obtener_texto_safe(prop.find('GrupoInmueble')),
                'familia': obtener_texto_safe(prop.find('Familia')),
                'tipo': obtener_texto_safe(prop.find('Tipo')),
                'subtipo': obtener_texto_safe(prop.find('Subtipo')),
                'destacado': obtener_bool_safe(prop.find('Destacado')),
                'estado': obtener_texto_safe(prop.find('Estado')),
                'uso_inmueble': obtener_texto_safe(prop.find('UsoInmueble')),
                'ultima_actividad': obtener_texto_safe(prop.find('UltimaActividad')),
                'titulo': obtener_texto_safe(prop.find('Titulo')),
                'descripcion': obtener_texto_safe(prop.find('Descripcion')),
                'descripcion_ampliada': obtener_texto_safe(prop.find('DescripcionAmpliada')),
                'operaciones': json.dumps(operaciones),
                'ibi': obtener_numeric_safe(prop.find('IBI')),
                'gastos_comunidad': obtener_numeric_safe(prop.find('GastosComunidad')),
                'provincia': obtener_texto_safe(prop.find('.//Provincia')),
                'poblacion': obtener_texto_safe(prop.find('.//Poblacion')),
                'zona': obtener_texto_safe(prop.find('.//Zona')),
                'subzona': obtener_texto_safe(prop.find('.//Subzona')),
                'urbanizacion': obtener_texto_safe(prop.find('.//Urbanizacion')),
                'direccion': obtener_texto_safe(prop.find('.//Direccion')),
                'numero': obtener_texto_safe(prop.find('.//Numero')),
                'escalera': obtener_texto_safe(prop.find('.//Escalera')),
                'planta': obtener_texto_safe(prop.find('.//Planta')),
                'letra': obtener_texto_safe(prop.find('.//Letra')),
                'codigo_postal': obtener_texto_safe(prop.find('.//CodigoPostal')),
                'latitud': obtener_numeric_safe(prop.find('.//Latitud')),
                'longitud': obtener_numeric_safe(prop.find('.//Longitud')),
                'superficie_construida': obtener_numeric_safe(prop.find('SuperficieConstruida')),
                'superficie_util': obtener_numeric_safe(prop.find('SuperficieUtil')),
                'superficie_parcela': obtener_numeric_safe(prop.find('SuperficieParcela')),
                'num_habitaciones': obtener_int_safe(prop.find('NumHabitaciones')),
                'num_banos': obtener_int_safe(prop.find('NumBanos')),
                'num_aseos': obtener_int_safe(prop.find('NumAseos')),
                'num_plantas': obtener_int_safe(prop.find('NumPlantas')),
                'ano_construccion': obtener_int_safe(prop.find('AnoConstruccion')),
                'estado_conservacion': obtener_texto_safe(prop.find('EstadoConservacion')),
                'equipamiento': obtener_texto_safe(prop.find('Equipamiento')),
                'calefaccion': obtener_texto_safe(prop.find('Calefaccion')),
                'aire_acondicionado': obtener_texto_safe(prop.find('AireAcondicionado')),
                'ascensor': obtener_bool_safe(prop.find('Ascensor')),
                'parking': obtener_bool_safe(prop.find('Parking')),
                'trastero': obtener_bool_safe(prop.find('Trastero')),
                'terraza': obtener_bool_safe(prop.find('Terraza')),
                'jardin': obtener_bool_safe(prop.find('Jardin')),
                'piscina': obtener_bool_safe(prop.find('Piscina')),
                'caracteristicas': json.dumps(caracteristicas),
                'fotos': json.dumps(fotos),
                'documentos': json.dumps([])  # Por ahora vacío
            }
            
            # Insertar en la base de datos
            columns = ', '.join(datos.keys())
            placeholders = ', '.join(['%s'] * len(datos))
            query = f"INSERT INTO propiedades ({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO UPDATE SET updated_at = NOW()"
            
            cursor.execute(query, list(datos.values()))
        
        print(f"✅ Procesamiento completado. {len(propiedades)} propiedades procesadas.")
        
    except ET.ParseError as e:
        print(f"❌ Error al parsear XML: {e}")
        raise
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        raise

def main():
    if not DB_URL:
        print("❌ Error: DB_URL no está configurada en el archivo .env")
        return
    
    if not XML_URL:
        print("❌ Error: XML_URL no está configurada en el archivo .env")
        return
    
    print(f"🔗 Conectando a la base de datos...")
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        print("✅ Conexión a la base de datos establecida")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return
    
    try:
        # Crear esquema
        crear_esquema_db(cursor)
        
        # Descargar XML
        print(f"📥 Descargando XML desde: {XML_URL}")
        response = requests.get(XML_URL, timeout=30)
        response.raise_for_status()
        xml_content = response.text
        
        # Procesar XML
        procesar_xml_e_insertar(cursor, xml_content)
        
        # Commit cambios
        conn.commit()
        print("✅ Cambios guardados en la base de datos")
        
    except requests.RequestException as e:
        print(f"❌ Error al descargar XML: {e}")
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("🔌 Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main() 