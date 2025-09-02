import numpy as np
import pandas as pd
from pathlib import Path
import geopandas as gpd
import warnings
from typing import Optional, Union
import xml.etree.ElementTree as ET
import re, struct
from PyPDF2 import PdfReader
from .shared import show_gui_popup


def normalize(data: np.ndarray):
    """Normaliza un array entre 0 y 1 usando min-max scaling."""
    range_val = data.max() - data.min()
    return np.zeros_like(data) if range_val == 0 else (data - data.min()) / range_val

def conditional(df, conditions, results, column_name):
    """Aplica condiciones lógicas para generar una nueva columna."""
    try:
        if len(conditions) != len(results):
            raise ValueError("La cantidad de condiciones y resultados debe ser igual.")

        condlist = []
        for cond in conditions:
            if callable(cond):
                cond = cond(df)
            cond = np.asarray(cond, dtype=bool)
            condlist.append(cond)

        df[column_name] = np.select(condlist, results, default=False)
        return df

    except Exception as e:
        show_gui_popup(title="Error", content=str(e))


def convert_atx_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo ATX a CSV."""
    try:
        input_path = Path(input_path)
        with open(input_path, "rb") as f:
            content = f.read()
        
        records = []
        field_number = struct.unpack('<i', content[0:4])[0]
        
        for i in range(4, len(content), 4):
            if i + 4 > len(content):
                break
            offset = struct.unpack('<i', content[i:i+4])[0]
            records.append({
                "field_index": field_number,
                "record_number": (i-4)//4 + 1,
                "offset": offset
            })
        
        df = pd.DataFrame(records)
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)
    except Exception as e:
        raise RuntimeError(f"Error procesando ATX {input_path.name}: {e}")

def convert_cpg_to_csv(input_path: Union[str, Path], output_path: Union[str, Path], name: Optional[str] = None) -> None:
    """Convierte archivo CPG a CSV."""
    try:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

        with open(input_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            content = f.read().strip()

        if not content:
            raise ValueError(f"El archivo CPG {input_path.name} está vacío")

        data = {"encoding": [content]}
        if name is not None:
            data["from_file"] = [name]
            
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, quoting=1)

    except Exception as e:
        raise RuntimeError(f"Error leyendo CPG {input_path.name}: {e}")

def convert_dbf_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo DBF a CSV."""
    try:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        

        try:
            from simpledbf import Dbf5
            dbf = Dbf5(str(input_path), codec="latin1")
            df = dbf.to_dataframe()
        except ImportError:

            df = pd.read_csv(input_path, engine="python", encoding="latin1")
        except Exception as e:
            raise ValueError(f"Error al leer DBF: {e}")

        if df.empty:
            raise ValueError(f"El DBF {input_path.name} está vacío")


        for col in df.columns:
            if df[col].dtype == object and isinstance(df[col].iloc[0], bytes):
                df[col] = df[col].apply(lambda x: x.decode('latin1', errors='ignore'))

        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)

    except Exception as e:
        raise RuntimeError(f"Error procesando DBF {input_path.name}: {e}")

def convert_pdf_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo PDF a CSV."""
    try:
        input_path = Path(input_path)
        reader = PdfReader(str(input_path))
        text_data = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                clean_text = re.sub(r'\s+', ' ', text).strip()
                text_data.append({"page": i+1, "text": clean_text})

        if not text_data:
            raise ValueError(f"El PDF {input_path.name} no contiene texto extraíble")

        df = pd.DataFrame(text_data)
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)
    except Exception as e:
        raise RuntimeError(f"Error procesando PDF {input_path.name}: {e}")

def convert_prj_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo PRJ a CSV."""
    try:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()

        if not content:
            raise ValueError(f"El archivo {input_path.name} está vacío")

        metadata = {"metadata_content": content}
        df = pd.DataFrame([metadata])
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)
    except Exception as e:
        raise RuntimeError(f"Error procesando metadatos {input_path.name}: {e}")

def convert_sbn_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo SBN a CSV."""
    try:
        input_path = Path(input_path)
        with open(input_path, "rb") as f:
            content = f.read()
        
        records = []
        for i in range(0, len(content), 32):  # 4 doubles * 8 bytes cada uno
            if i + 32 > len(content):
                break
            try:
                minx, miny, maxx, maxy = struct.unpack('<4d', content[i:i+32])
                records.append({
                    "record_number": i//32 + 1,
                    "min_x": minx,
                    "min_y": miny,
                    "max_x": maxx,
                    "max_y": maxy,
                    "note": "Bounding box del nodo en el arbol espacial"
                })
            except:
                continue
        
        if not records:
            raise ValueError("No se pudieron extraer bounding boxes validas")
            
        df = pd.DataFrame(records)
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)
    except Exception as e:
        raise RuntimeError(f"Error procesando SBN {input_path.name}: {e}")

def convert_sbx_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo SBX a CSV."""
    try:
        input_path = Path(input_path)
        with open(input_path, "rb") as f:
            content = f.read()

        header_size = 100
        records = []


        formats = {
            8: ('<2i', ["offset", "length"], "Offset/Length"),
            16: ('<4i', ["i1", "i2", "i3", "i4"], "4 enteros"),
            32: ('<4d', ["min_x", "min_y", "max_x", "max_y"], "Bounding box")
        }

        detected_format = None
        for size, (fmt, fields, note) in formats.items():
            if header_size + size <= len(content):
                try:
                    struct.unpack(fmt, content[header_size:header_size+size])
                    detected_format = (size, fmt, fields, note)
                    break
                except:
                    continue

        if not detected_format:
            raise RuntimeError("Formato de SBX no reconocido")

        size, fmt, fields, note = detected_format
        for i in range(header_size, len(content), size):
            if i + size > len(content):
                break
            values = struct.unpack(fmt, content[i:i+size])
            record = {"record_number": (i - header_size)//size + 1}
            for fname, val in zip(fields, values):
                record[fname] = val
            record["note"] = note
            records.append(record)

        df = pd.DataFrame(records)
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)

    except Exception as e:
        raise RuntimeError(f"Error procesando SBX {input_path.name}: {e}")

def convert_shp_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo SHP a CSV."""
    try:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")


        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gdf = gpd.read_file(input_path)
        
        if gdf.empty:
            raise ValueError(f"El shapefile {input_path.name} está vacío")


        gdf['geometry'] = gdf.make_valid()
        valid_geoms = gdf.geometry.notna() & ~gdf.is_empty & gdf.is_valid
        gdf = gdf[valid_geoms]
        
        if gdf.empty:
            raise ValueError("Todas las geometrías son inválidas")


        utm_crs = gdf.estimate_utm_crs()
        gdf = gdf.to_crs(utm_crs)
        
        gdf['longitude'] = np.nan
        gdf['latitude'] = np.nan
        gdf['area_km2'] = np.nan
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            valid_idx = gdf.geometry.is_valid
            centroids = gdf[valid_idx].centroid.to_crs("EPSG:4326")
            gdf.loc[valid_idx, "longitude"] = centroids.x
            gdf.loc[valid_idx, "latitude"] = centroids.y
            gdf.loc[valid_idx, "area_km2"] = gdf[valid_idx].geometry.area / 1e6

        gdf['geometry_type'] = gdf.geometry.geom_type
        

        keep_cols = [c for c in gdf.columns if c != 'geometry']
        df = pd.DataFrame(gdf)[keep_cols]
        
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)

    except Exception as e:
        raise RuntimeError(f"Error procesando SHP {input_path.name}: {str(e)}")

def convert_shx_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo SHX a CSV."""
    try:
        input_path = Path(input_path)
        with open(input_path, "rb") as f:
            content = f.read()
        
        records = []
        for i in range(0, len(content), 8):
            if i + 8 > len(content):
                break
            offset = struct.unpack('>i', content[i:i+4])[0]
            length = struct.unpack('>i', content[i+4:i+8])[0]
            records.append({
                "record_number": i//8 + 1,
                "byte_offset_in_shp": offset * 2,
                "content_length_bytes": length * 2,
                "note": "Offset para geometría en SHP"
            })
        
        df = pd.DataFrame(records)
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)
    except Exception as e:
        raise RuntimeError(f"Error procesando SHX {input_path.name}: {e}")

def convert_xml_to_csv(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Convierte archivo XML a CSV."""
    try:
        input_path = Path(input_path)
        tree = ET.parse(input_path)
        root = tree.getroot()

        def parse_node(node):
            data = {}
            for child in node:
                if len(child) == 0:
                    data[child.tag] = child.text
                else:
                    data[child.tag] = parse_node(child)
            return data

        rows = []
        for child in root:
            rows.append(parse_node(child))

        if not rows:
            raise ValueError(f"El XML {input_path.name} no contiene datos")

        df = pd.json_normalize(rows)
        df.to_csv(output_path, index=False, encoding='utf-8', quoting=1)

    except Exception as e:
        raise RuntimeError(f"Error procesando XML {input_path.name}: {e}")


CONVERTERS = {
    '.atx': convert_atx_to_csv,
    '.cpg': convert_cpg_to_csv,
    '.dbf': convert_dbf_to_csv,
    '.pdf': convert_pdf_to_csv,
    '.prj': convert_prj_to_csv,
    '.sbn': convert_sbn_to_csv,
    '.sbx': convert_sbx_to_csv,
    '.shp': convert_shp_to_csv,
    '.shx': convert_shx_to_csv,
    '.xml': convert_xml_to_csv
}

def convert_file(input_path: Union[str, Path], output_path: Union[str, Path], **kwargs) -> None:
    """Convierte un archivo a CSV basado en su extensión."""
    input_path = Path(input_path)
    ext = input_path.suffix.lower()
    
    if ext not in CONVERTERS:
        raise ValueError(f"Formato no soportado: {ext}")
    
    converter = CONVERTERS[ext]
    converter(input_path, output_path, **kwargs)
