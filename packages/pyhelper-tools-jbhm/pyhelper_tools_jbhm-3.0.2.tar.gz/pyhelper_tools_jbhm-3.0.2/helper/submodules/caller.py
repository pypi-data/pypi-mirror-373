import time, os, json, csv
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from .shared import show_gui_popup, t
from .pyswitch import Switch



def call(
    name: str,
    type: str = None,
    path: str = None,
    timeout: int = 5,
    strict: bool = True,
    verbose: bool = False,
):
    try:
        start_time = time.time()
        path = Path(path) if path else Path.cwd()
        name = Path(name).stem

        def _search_files_(directory):
            try:
                found = {}
                for root, _, files in os.walk(directory):
                    try:
                        for file in files:
                            file_path = Path(root) / file
                            if file_path.stem == name:
                                ext = file_path.suffix[1:].lower()
                                if ext in ["csv", "json", "xml"]:
                                    found[ext] = file_path
                        if time.time() - start_time > timeout:
                            break
                    except Exception as e:
                        if verbose:
                            print(f"Error processing directory {root}: {e}")
                        continue
                return found
            except Exception as e:
                if verbose:
                    print(f"Error in file search: {e}")
                return {}

        found = _search_files_(path)

        if verbose:
            try:
                show_gui_popup(
                    title=t("file_search_title"),
                    text=f"{t('searching_from')}: {path}\n{t('files_found')}: {list(found.keys())}",
                )
            except Exception as e:
                print(f"Error showing GUI popup: {e}")

        if type:
            try:
                type = type.lower()
                if type not in found:
                    raise FileNotFoundError(
                        t("file_not_found_explicit").format(name=name, ext=type, path=path)
                    )
                return read(found[type])
            except Exception as e:
                if verbose:
                    print(f"Error processing specific file type '{type}': {e}")
                raise
        else:
            try:
                if not found:
                    raise FileNotFoundError(
                        t("file_not_found_any").format(name=name, path=path)
                    )
                if len(found) == 1:
                    ext, ruta = list(found.items())[0]
                    return read(ruta, ext)
                if strict:
                    raise ValueError(
                        t("file_ambiguous").format(name=name, types=list(found.keys()))
                    )
                else:
                    return {ext: read(ruta, ext) for ext, ruta in found.items()}
            except Exception as e:
                if verbose:
                    print(f"Error processing found files: {e}")
                raise

    except FileNotFoundError as e:
        if verbose:
            print(f"File not found error: {e}")
        raise
    except ValueError as e:
        if verbose:
            print(f"Value error: {e}")
        raise
    except Exception as e:
        if verbose:
            print(f"Unexpected error in call function: {e}")
        raise

def read(file_path: Path):
    ext = file_path.suffix

    res = Switch(ext)(
                    {
                        "cases": [
                            {
                                "case": ".json",
                                "then": lambda: pd.read_json(file_path),
                            },
                            {
                                "case": ".csv",
                                "then": lambda: pd.read_csv(file_path),
                            },
                            {
                                "case": ".xml",
                                "then": lambda: pd.read_xml(file_path),
                            },
                            {
                                "case": ".html",
                                "then": lambda: pd.read_html(file_path),
                            },
                        ],
                        "default": lambda: None,
                    }
                )
    if res is None:
        raise  ValueError(t("unsupported_file_type").format(ext=ext))
    else:
        return res
