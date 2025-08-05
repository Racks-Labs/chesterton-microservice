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
    # --- MODIFICADO: Esquema definitivo con TODOS los campos ---
    cursor.execute("""
        CREATE TABLE propiedades (
            -- IDs y Referencias
            id NUMERIC PRIMARY KEY,
            referencia TEXT UNIQUE NOT NULL,
            agencia_id TEXT,
            url TEXT,

            -- Fechas
            fecha_creacion TIMESTAMP WITH TIME ZONE,
            fecha_publicacion TIMESTAMP WITH TIME ZONE, -- <-- AÑADIDO (para <Fecha>)
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
            parcela TEXT,
            latitud NUMERIC,
            longitud NUMERIC,
            zoom INTEGER,
            tipo_localizacion INTEGER,          -- <-- AÑADIDO
            latitud_zona NUMERIC,               -- <-- AÑADIDO
            longitud_zona NUMERIC,              -- <-- AÑADIDO
            radio_zona NUMERIC,                 -- <-- AÑADIDO
            
            -- Dimensiones y Superficies
            metros_construidos NUMERIC,
            metros_utiles NUMERIC,
            metros_parcela NUMERIC,
            metros_edificables NUMERIC,
            metros_oficinas NUMERIC,
            metros_jardin NUMERIC,
            metros_terrazas NUMERIC,
            metros_fachada NUMERIC,
            metros_fachada_secundaria NUMERIC,
            altura_techo NUMERIC,
            ano_construccion INTEGER,
            superficies JSONB,
            
            -- Características numéricas (Conteos)
            habitaciones INTEGER,
            banos INTEGER,
            aseos INTEGER,
            despachos INTEGER,
            salas_reunion INTEGER,
            sala_descanso INTEGER,              -- <-- AÑADIDO
            cocina INTEGER,                     -- <-- AÑADIDO
            comedor INTEGER,                    -- <-- AÑADIDO
            plazas_garaje INTEGER,
            plazas_parking INTEGER,
            armarios INTEGER,
            num_terrazas INTEGER,
            entradas_nave_tir INTEGER,
            plantas_del_edificio INTEGER,
            chimeneas INTEGER,                  -- <-- AÑADIDO
            trasteros INTEGER,
            
            -- Características Cualitativas (Texto)
            calificacion_suelo TEXT,
            tipo_configuracion TEXT,            -- <-- AÑADIDO
            orientacion TEXT,
            calificacion_energetica TEXT,
            consumo TEXT,
            calificacion_emisiones TEXT,
            emisiones TEXT,
            carpinteria TEXT,
            suelo TEXT,
            luminoso TEXT,                      -- <-- AÑADIDO
            ruido TEXT,                         -- <-- AÑADIDO
            vistas TEXT,                        -- <-- AÑADIDO

            -- Características Booleanas (0/1)
            en_esquina BOOLEAN,
            interior BOOLEAN,
            exterior BOOLEAN,
            salida_emergencia BOOLEAN,
            salida_humos BOOLEAN,
            divisiones BOOLEAN,
            vestuarios BOOLEAN,
            escaparate BOOLEAN,
            tiene_oficinas BOOLEAN,
            altillo BOOLEAN,
            patio BOOLEAN,
            muelle_carga BOOLEAN,
            cubierta BOOLEAN,
            vado BOOLEAN,
            buhardilla BOOLEAN,
            amueblado BOOLEAN,
            cocina_amueblada BOOLEAN,
            asfaltado BOOLEAN,
            alumbrado BOOLEAN,
            vallado BOOLEAN,
            urbanizado BOOLEAN,
            acometidas BOOLEAN,                 -- <-- AÑADIDO
            aire_acondicionado BOOLEAN,         -- <-- AÑADIDO
            luz BOOLEAN,
            gas BOOLEAN,
            agua BOOLEAN,
            telefono BOOLEAN,
            internet BOOLEAN,
            intranet BOOLEAN,                   -- <-- AÑADIDO
            tratamiento_ignifugo BOOLEAN,       -- <-- AÑADIDO
            sistema_antiincendios BOOLEAN,
            camara_frigorifica BOOLEAN,
            pozo BOOLEAN,                       -- <-- AÑADIDO
            piscina_privada BOOLEAN,
            piscina_comunitaria BOOLEAN,
            zonas_comunes BOOLEAN,              -- <-- AÑADIDO
            zona_infantil BOOLEAN,              -- <-- AÑADIDO
            zonas_verdes BOOLEAN,               -- <-- AÑADIDO
            pista_multiusos BOOLEAN,            -- <-- AÑADIDO
            gimnasio BOOLEAN,                   -- <-- AÑADIDO
            pista_padel BOOLEAN,                -- <-- AÑADIDO
            pista_tenis BOOLEAN,                -- <-- AÑADIDO
            bodega BOOLEAN,                     -- <-- AÑADIDO
            barbacoa BOOLEAN,                   -- <-- AÑADIDO
            solarium BOOLEAN,                   -- <-- AÑADIDO
            lavadero BOOLEAN,                   -- <-- AÑADIDO
            alarma BOOLEAN,
            alarma_perimetral BOOLEAN,          -- <-- AÑADIDO
            cerrado BOOLEAN,                    -- <-- AÑADIDO
            puerta_blindad BOOLEAN,             -- <-- AÑADIDO (respeta la errata del XML)
            caja_fuerte BOOLEAN,                -- <-- AÑADIDO
            conserje BOOLEAN,                   -- <-- AÑADIDO
            vigilancia_24h BOOLEAN,
            rejas BOOLEAN,                      -- <-- AÑADIDO
            adaptado BOOLEAN,                   -- <-- AÑADIDO
            acceso_discapacitados BOOLEAN,
            admite_mascotas BOOLEAN,            -- <-- AÑADIDO
            ascensor BOOLEAN,
            montacargas BOOLEAN,
            puente_grua BOOLEAN,
            bascula BOOLEAN,                    -- <-- AÑADIDO
            primera_linea_playa BOOLEAN,        -- <-- AÑADIDO
            segunda_linea_playa BOOLEAN,        -- <-- AÑADIDO
            
            -- Contenido Multimedia y otros (JSONB)
            grupos JSONB,
            fotos360 JSONB,                     -- <-- AÑADIDO
            videos JSONB,                       -- <-- AÑADIDO
            archivos JSONB,                     -- <-- AÑADIDO
            
            -- Campos para completitud (posiblemente vacíos)
            cuentas TEXT,                       -- <-- AÑADIDO
            mandatos TEXT                       -- <-- AÑADIDO
        );
        
        CREATE TABLE fotos (
            id SERIAL PRIMARY KEY,
            propiedad_referencia TEXT NOT NULL REFERENCES propiedades(referencia) ON DELETE CASCADE,
            url_foto TEXT,
            orden INTEGER
        );
    """)

    print("Creando tabla minimalista 'propiedades_min'...")
    cursor.execute("""
        CREATE TABLE propiedades_min (
            referencia TEXT PRIMARY KEY,
            url TEXT,
            titulo TEXT,
            descripcion TEXT,
            descripcion_ampliada TEXT,
            estado TEXT,
            operaciones JSONB,
            altura_techo NUMERIC,
            metros_parcela NUMERIC,
            metros_utiles NUMERIC,
            metros_edificables NUMERIC,
            metros_construidos NUMERIC,
            metros_oficinas NUMERIC,
            grupo_inmueble TEXT,
            latitud NUMERIC,
            longitud NUMERIC,
            poblacion TEXT,
            ano_construccion INTEGER
        );
    """)
    print("Tabla 'propiedades_min' creada.")

    print("Esquema de base de datos creado exitosamente.")


def procesar_xml_e_insertar(cursor, xml_content):
    print("Parseando el XML...")
    root = ET.fromstring(xml_content)
    total_inmuebles = len(root.findall('Inmueble'))
    print(f"Se encontraron {total_inmuebles} inmuebles para procesar.")

    for i, inmueble in enumerate(root.findall('Inmueble')):
        ref = obtener_texto_safe(inmueble.find('Referencia'))
        if not ref:
            print(f"Saltando inmueble sin referencia en la posición {i+1}")
            continue

        print(f"Procesando inmueble {i+1}/{total_inmuebles} (Ref: {ref})...")

        # --- Extracción de datos anidados a JSON ---
        def extract_json_list(xpath, mapping_func):
            elements = inmueble.findall(xpath)
            if not elements: return None
            data_list = [mapping_func(el) for el in elements]
            return json.dumps(data_list) if data_list else None

        operaciones_json = extract_json_list('Operaciones/Operacion', lambda op: {'tipo': obtener_texto_safe(op.find('Tipo')), 'precio': obtener_numeric_safe(op.find('Precio'))})
        superficies_json = extract_json_list('Superficies/Superficie', lambda s: {'nombre': obtener_texto_safe(s.find('Nombre')), 'superficie': obtener_numeric_safe(s.find('Superficie')), 'altura': obtener_numeric_safe(s.find('Altura')), 'observaciones': obtener_texto_safe(s.find('Observaciones'))})
        grupos_json = extract_json_list('Grupos/Grupo', obtener_texto_safe)
        fotos360_json = extract_json_list('Fotos360/Foto360', obtener_texto_safe) # Asumo estructura similar a Fotos
        videos_json = extract_json_list('Videos/Video', obtener_texto_safe)
        archivos_json = extract_json_list('Archivos/Archivo', obtener_texto_safe)

        # --- Diccionario de datos completo y definitivo ---
        propiedad_data = {
            'id': obtener_int_safe(inmueble.find('Id')), 'referencia': ref, 'agencia_id': obtener_texto_safe(inmueble.find('AgenciaId')), 'url': obtener_texto_safe(inmueble.find('UrlPublica')),
            'fecha_creacion': obtener_timestamp_safe(inmueble.find('FechaCreacion')), 'fecha_publicacion': obtener_timestamp_safe(inmueble.find('Fecha')), 'fecha_modificacion': obtener_timestamp_safe(inmueble.find('FechaModificacion')),
            'grupo_inmueble': obtener_texto_safe(inmueble.find('GrupoInmueble')), 'familia': obtener_texto_safe(inmueble.find('Familia')), 'tipo': obtener_texto_safe(inmueble.find('Tipo')), 'subtipo': obtener_texto_safe(inmueble.find('Subtipo')),
            'destacado': obtener_bool_safe(inmueble.find('Destacado')), 'estado': obtener_texto_safe(inmueble.find('Estado')), 'uso_inmueble': obtener_texto_safe(inmueble.find('UsoInmueble')), 'ultima_actividad': obtener_texto_safe(inmueble.find('UltimaActividad')),
            'titulo': obtener_texto_safe(inmueble.find('Titulo')), 'descripcion': obtener_texto_safe(inmueble.find('Descripcion')), 'descripcion_ampliada': obtener_texto_safe(inmueble.find('DescripcionAmpliada')),
            'operaciones': operaciones_json, 'ibi': obtener_numeric_safe(inmueble.find('Ibi')), 'gastos_comunidad': obtener_numeric_safe(inmueble.find('GastosComunidad')),
            'provincia': obtener_texto_safe(inmueble.find('Provincia')), 'poblacion': obtener_texto_safe(inmueble.find('Poblacion')), 'zona': obtener_texto_safe(inmueble.find('Zona')), 'subzona': obtener_texto_safe(inmueble.find('Subzona')), 'urbanizacion': obtener_texto_safe(inmueble.find('Urbanizacion')),
            'direccion': obtener_texto_safe(inmueble.find('Direccion')), 'numero': obtener_texto_safe(inmueble.find('Numero')), 'escalera': obtener_texto_safe(inmueble.find('Escalera')), 'planta': obtener_texto_safe(inmueble.find('Planta')), 'letra': obtener_texto_safe(inmueble.find('Letra')), 'codigo_postal': obtener_texto_safe(inmueble.find('CodigoPostal')), 'parcela': obtener_texto_safe(inmueble.find('Parcela')),
            'latitud': obtener_numeric_safe(inmueble.find('Latitud')), 'longitud': obtener_numeric_safe(inmueble.find('Longitud')), 'zoom': obtener_int_safe(inmueble.find('Zoom')),
            'tipo_localizacion': obtener_int_safe(inmueble.find('TipoLocalizacion')), 'latitud_zona': obtener_numeric_safe(inmueble.find('LatitudZona')), 'longitud_zona': obtener_numeric_safe(inmueble.find('LongitudZona')), 'radio_zona': obtener_numeric_safe(inmueble.find('RadioZona')),
            'metros_construidos': obtener_numeric_safe(inmueble.find('MetrosConstruidos')), 'metros_utiles': obtener_numeric_safe(inmueble.find('MetrosUtiles')), 'metros_parcela': obtener_numeric_safe(inmueble.find('MetrosParcela')), 'metros_edificables': obtener_numeric_safe(inmueble.find('MetrosEdificables')),
            'metros_oficinas': obtener_numeric_safe(inmueble.find('MetrosOficinas')), 'metros_jardin': obtener_numeric_safe(inmueble.find('MetrosJardin')), 'metros_terrazas': obtener_numeric_safe(inmueble.find('MetrosTerrazas')), 'metros_fachada': obtener_numeric_safe(inmueble.find('MetrosFachada')), 'metros_fachada_secundaria': obtener_numeric_safe(inmueble.find('MetrosFachadaSecundaria')),
            'altura_techo': obtener_numeric_safe(inmueble.find('AlturaTecho')), 'ano_construccion': obtener_int_safe(inmueble.find('AnoConstruccion')), 'superficies': superficies_json,
            'habitaciones': obtener_int_safe(inmueble.find('Habitaciones')), 'banos': obtener_int_safe(inmueble.find('Banos')), 'aseos': obtener_int_safe(inmueble.find('Aseos')), 'despachos': obtener_int_safe(inmueble.find('Despachos')), 'salas_reunion': obtener_int_safe(inmueble.find('SalasReunion')),
            'sala_descanso': obtener_int_safe(inmueble.find('SalaDescanso')), 'cocina': obtener_int_safe(inmueble.find('Cocina')), 'comedor': obtener_int_safe(inmueble.find('Comedor')),
            'plazas_garaje': obtener_int_safe(inmueble.find('PlazasGaraje')), 'plazas_parking': obtener_int_safe(inmueble.find('PlazasParking')), 'armarios': obtener_int_safe(inmueble.find('Armarios')), 'num_terrazas': obtener_int_safe(inmueble.find('NumTerrazas')), 'entradas_nave_tir': obtener_int_safe(inmueble.find('EntradasNaveTir')),
            'plantas_del_edificio': obtener_int_safe(inmueble.find('PlantasDelEdificio')), 'chimeneas': obtener_int_safe(inmueble.find('Chimeneas')), 'trasteros': obtener_int_safe(inmueble.find('Trasteros')),
            'calificacion_suelo': obtener_texto_safe(inmueble.find('CalificacionSuelo')), 'tipo_configuracion': obtener_texto_safe(inmueble.find('TipoConfiguracion')), 'orientacion': obtener_texto_safe(inmueble.find('Orientacion')), 'calificacion_energetica': obtener_texto_safe(inmueble.find('CalificacionEnergetica')),
            'consumo': obtener_texto_safe(inmueble.find('Consumo')), 'calificacion_emisiones': obtener_texto_safe(inmueble.find('CalificacionEmisiones')), 'emisiones': obtener_texto_safe(inmueble.find('Emisiones')), 'carpinteria': obtener_texto_safe(inmueble.find('Carpinteria')),
            'suelo': obtener_texto_safe(inmueble.find('Suelo')), 'luminoso': obtener_texto_safe(inmueble.find('Luminoso')), 'ruido': obtener_texto_safe(inmueble.find('Ruido')), 'vistas': obtener_texto_safe(inmueble.find('Vistas')),
            'en_esquina': obtener_bool_safe(inmueble.find('EnEsquina')), 'interior': obtener_bool_safe(inmueble.find('Interior')), 'exterior': obtener_bool_safe(inmueble.find('Exterior')), 'salida_emergencia': obtener_bool_safe(inmueble.find('SalidaEmergencia')),
            'salida_humos': obtener_bool_safe(inmueble.find('SalidaHumos')), 'divisiones': obtener_bool_safe(inmueble.find('Divisiones')), 'vestuarios': obtener_bool_safe(inmueble.find('Vestuarios')), 'escaparate': obtener_bool_safe(inmueble.find('Escaparate')), 'tiene_oficinas': obtener_bool_safe(inmueble.find('TieneOficinas')),
            'altillo': obtener_bool_safe(inmueble.find('Altillo')), 'patio': obtener_bool_safe(inmueble.find('Patio')), 'muelle_carga': obtener_bool_safe(inmueble.find('MuelleCarga')), 'cubierta': obtener_bool_safe(inmueble.find('Cubierta')), 'vado': obtener_bool_safe(inmueble.find('Vado')), 'buhardilla': obtener_bool_safe(inmueble.find('Buhardilla')),
            'amueblado': obtener_bool_safe(inmueble.find('Amueblado')), 'cocina_amueblada': obtener_bool_safe(inmueble.find('CocinaAmueblada')), 'asfaltado': obtener_bool_safe(inmueble.find('Asfaltado')), 'alumbrado': obtener_bool_safe(inmueble.find('Alumbrado')), 'vallado': obtener_bool_safe(inmueble.find('Vallado')), 'urbanizado': obtener_bool_safe(inmueble.find('Urbanizado')),
            'acometidas': obtener_bool_safe(inmueble.find('Acometidas')), 'aire_acondicionado': obtener_bool_safe(inmueble.find('AireAcondicionado')), 'luz': obtener_bool_safe(inmueble.find('Luz')), 'gas': obtener_bool_safe(inmueble.find('Gas')), 'agua': obtener_bool_safe(inmueble.find('Agua')), 'telefono': obtener_bool_safe(inmueble.find('Telefono')),
            'internet': obtener_bool_safe(inmueble.find('Internet')), 'intranet': obtener_bool_safe(inmueble.find('Intranet')), 'tratamiento_ignifugo': obtener_bool_safe(inmueble.find('TratamientoIgnifugo')), 'sistema_antiincendios': obtener_bool_safe(inmueble.find('SistemaAntiincendios')),
            'camara_frigorifica': obtener_bool_safe(inmueble.find('CamaraFrigorifica')), 'pozo': obtener_bool_safe(inmueble.find('Pozo')), 'piscina_privada': obtener_bool_safe(inmueble.find('PiscinaPrivada')), 'piscina_comunitaria': obtener_bool_safe(inmueble.find('PiscinaComunitaria')),
            'zonas_comunes': obtener_bool_safe(inmueble.find('ZonasComunes')), 'zona_infantil': obtener_bool_safe(inmueble.find('ZonaInfantil')), 'zonas_verdes': obtener_bool_safe(inmueble.find('ZonasVerdes')), 'pista_multiusos': obtener_bool_safe(inmueble.find('PistaMultiusos')), 'gimnasio': obtener_bool_safe(inmueble.find('Gimnasio')),
            'pista_padel': obtener_bool_safe(inmueble.find('PistaPadel')), 'pista_tenis': obtener_bool_safe(inmueble.find('PistaTenis')), 'bodega': obtener_bool_safe(inmueble.find('Bodega')), 'barbacoa': obtener_bool_safe(inmueble.find('Barbacoa')), 'solarium': obtener_bool_safe(inmueble.find('Solarium')), 'lavadero': obtener_bool_safe(inmueble.find('Lavadero')),
            'alarma': obtener_bool_safe(inmueble.find('Alarma')), 'alarma_perimetral': obtener_bool_safe(inmueble.find('AlarmaPerimetral')), 'cerrado': obtener_bool_safe(inmueble.find('Cerrado')), 'puerta_blindad': obtener_bool_safe(inmueble.find('PuertaBlindad')), 'caja_fuerte': obtener_bool_safe(inmueble.find('CajaFuerte')), 'conserje': obtener_bool_safe(inmueble.find('Conserje')),
            'vigilancia_24h': obtener_bool_safe(inmueble.find('Vigilancia24h')), 'rejas': obtener_bool_safe(inmueble.find('Rejas')), 'adaptado': obtener_bool_safe(inmueble.find('Adaptado')), 'acceso_discapacitados': obtener_bool_safe(inmueble.find('AccesoDiscapacitados')), 'admite_mascotas': obtener_bool_safe(inmueble.find('AdmiteMascotas')),
            'ascensor': obtener_bool_safe(inmueble.find('Ascensor')), 'montacargas': obtener_bool_safe(inmueble.find('Montacargas')), 'puente_grua': obtener_bool_safe(inmueble.find('PuenteGrua')), 'bascula': obtener_bool_safe(inmueble.find('Bascula')), 'primera_linea_playa': obtener_bool_safe(inmueble.find('PrimeraLineaPlaya')), 'segunda_linea_playa': obtener_bool_safe(inmueble.find('SegundaLineaPlaya')),
            'grupos': grupos_json, 'fotos360': fotos360_json, 'videos': videos_json, 'archivos': archivos_json,
            'cuentas': obtener_texto_safe(inmueble.find('Cuentas')), 'mandatos': obtener_texto_safe(inmueble.find('Mandatos'))
        }
        
        columnas = sql.SQL(', ').join(map(sql.Identifier, propiedad_data.keys()))
        placeholders = sql.SQL(', ').join(map(sql.Placeholder, propiedad_data.keys()))
        updates = sql.SQL(', ').join([sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(k), sql.Identifier(k)) for k in propiedad_data.keys() if k != 'referencia'])
        insert_propiedad = sql.SQL("INSERT INTO propiedades ({}) VALUES ({}) ON CONFLICT (referencia) DO UPDATE SET {}").format(columnas, placeholders, updates)
        cursor.execute(insert_propiedad, propiedad_data)

               # --- INICIO: LÓGICA PARA LA TABLA propiedades_min ---
        # 1. Crear un diccionario solo con los datos para la tabla minimalista.
        #    Reutilizamos los datos ya procesados del diccionario principal.
        propiedad_min_data = {
            'referencia':           propiedad_data['referencia'],
            'url':                  propiedad_data['url'],
            'titulo':               propiedad_data['titulo'],
            'descripcion':          propiedad_data['descripcion'],
            'descripcion_ampliada': propiedad_data['descripcion_ampliada'],
            'estado':               propiedad_data['estado'],
            'operaciones':          propiedad_data['operaciones'],
            'altura_techo':         propiedad_data['altura_techo'],
            'metros_parcela':       propiedad_data['metros_parcela'],
            'metros_utiles':        propiedad_data['metros_utiles'],
            'metros_edificables':   propiedad_data['metros_edificables'],
            'metros_construidos':   propiedad_data['metros_construidos'],
            'metros_oficinas':      propiedad_data['metros_oficinas'],
            'grupo_inmueble':       propiedad_data['grupo_inmueble'],
            'latitud':              propiedad_data['latitud'],
            'longitud':             propiedad_data['longitud'],
            'poblacion':            propiedad_data['poblacion'],
            'ano_construccion':     propiedad_data['ano_construccion']
        }

        # 2. Generar y ejecutar la sentencia SQL para 'propiedades_min'
        columnas_min = sql.SQL(', ').join(map(sql.Identifier, propiedad_min_data.keys()))
        placeholders_min = sql.SQL(', ').join(map(sql.Placeholder, propiedad_min_data.keys()))
        updates_min = sql.SQL(', ').join([sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(k), sql.Identifier(k)) for k in propiedad_min_data.keys() if k != 'referencia'])
        insert_propiedad_min = sql.SQL("INSERT INTO propiedades_min ({}) VALUES ({}) ON CONFLICT (referencia) DO UPDATE SET {}").format(columnas_min, placeholders_min, updates_min)
        cursor.execute(insert_propiedad_min, propiedad_min_data)
        # --- FIN: LÓGICA PARA LA TABLA propiedades_min ---

        # Insertar en 'fotos'
        fotos_element = inmueble.find('Fotos')
        if fotos_element is not None:
            cursor.execute("DELETE FROM fotos WHERE propiedad_referencia = %s;", (ref,))
            orden = 0
            for foto in fotos_element.findall('Foto'):
                url_foto = obtener_texto_safe(foto)
                if url_foto:
                    cursor.execute("INSERT INTO fotos (propiedad_referencia, url_foto, orden) VALUES (%s, %s, %s);", (ref, url_foto, orden))
                    orden += 1

def main():
    """Función principal del script."""
    conn = None
    try:
        print(f"Descargando XML desde {XML_URL}...")
        response = requests.get(XML_URL)
        response.raise_for_status()
        xml_content = response.content
        print("XML descargado exitosamente.")

        print("Conectando a la base de datos PostgreSQL...")
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        print("Conexión exitosa.")

        crear_esquema_db(cursor)
        procesar_xml_e_insertar(cursor, xml_content)

        conn.commit()
        print("\n¡Proceso completado! Todos los datos han sido importados y guardados en la base de datos.")

    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el XML: {e}")
    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    main() 