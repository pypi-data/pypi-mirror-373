import pandas as pd
import numpy as np
from typing import Union, List
from .shared import format_number, show_gui_popup, t



def get_moda(data: np.ndarray, with_repetition: bool = False, decimals: int = 2) -> Union[float, List[Union[float, int]]]:
    try:
        data_no_nan = data[~np.isnan(data)]

        if len(data_no_nan) == 0:
            return np.nan if not with_repetition else [np.nan, 0]

        valores, conteos = np.unique(data_no_nan, return_counts=True)

        if len(conteos) == 0:
            return np.nan if not with_repetition else [np.nan, 0]

        index_moda = np.argmax(conteos)

        if with_repetition:
            return [format_number(valores[index_moda], decimals), format_number(conteos[index_moda], decimals)]
        else:
            return format_number(valores[index_moda], decimals)
    except Exception as e:
        show_gui_popup(t("ERROR_MODA"))
        return np.nan if not with_repetition else [np.nan, 0]


def get_media(data: np.ndarray, nan: bool = False, decimals: int = 2) -> float:
    try:
        return format_number(np.nanmean(data) if nan else np.mean(data), decimals)
    except Exception as e:
        show_gui_popup(t("ERROR_MEDIA"))
        return np.nan


def get_median(data: np.ndarray, nan: bool = False, decimals: int = 2) -> float:
    try:
        return format_number(np.nanmedian(data) if nan else np.median(data), decimals)
    except Exception as e:
        show_gui_popup(t("ERROR_MEDIANA"))
        return np.nan


def get_rank(df: pd.DataFrame, column: str, decimals: int = 2) -> float:
    try:
        if column not in df.columns:
            show_gui_popup(t("ERROR_COLUMNA_NO_EXISTE").format(column))
            return np.nan
            
        return format_number(np.nanmax(df[column]) - np.nanmin(df[column]), decimals)
    except Exception as e:
        show_gui_popup(t("ERROR_RANGO"))
        return np.nan


def get_var(df: pd.DataFrame, column: str, decimals: int = 2) -> float:
    try:
        if column not in df.columns:
            show_gui_popup(t("ERROR_COLUMNA_NO_EXISTE").format(column))
            return np.nan
            
        return format_number(np.nanvar(df[column]), decimals)
    except Exception as e:
        show_gui_popup(t("ERROR_VARIANZA"))
        return np.nan


def get_desv(df: pd.DataFrame, column: str, decimals: int = 2) -> float:
    try:
        if column not in df.columns:
            show_gui_popup(t("ERROR_COLUMNA_NO_EXISTE").format(column))
            return np.nan
            
        return format_number(np.nanstd(df[column]), decimals)
    except Exception as e:
        show_gui_popup(t("ERROR_DESVIACION"))
        return np.nan


def disp(df: pd.DataFrame, column: str, condition: pd.Series = None) -> dict:
    try:
        if column not in df.columns:
            show_gui_popup(t("ERROR_COLUMNA_NO_EXISTE").format(column))
            return {
                "rango": np.nan,
                "varianza": np.nan,
                "desviacion estandar": np.nan
            }

        if condition is not None:
            df = df[condition]

        return {
            "rango": get_rank(df, column),
            "varianza": get_var(df, column),
            "desviacion estandar": get_desv(df, column),
        }
    except Exception as e:
        show_gui_popup(t("ERROR_DISPERSION"))
        return {
            "rango": np.nan,
            "varianza": np.nan,
            "desviacion estandar": np.nan
        }
    
def IQR(df: pd.DataFrame, column: str = None):
    if column is None:
        return err("not_none_allowed")
    
    q1 = None
    q3 = None
    iqr = None
    lower_bound = None
    upper_bound = None
    
    try:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
    except ValueError as e:
        return print(e)
    
    if not q1 is None and not q3 is None:
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers_iqr = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        show_gui_popup(t("iqr_method"),f"Q1: {q1}, Q3: {q3}, IQR: {iqr}\n{t("lower_bound")}: {lower_bound}, {t("upper_bound")}: {upper_bound}\n{t("outliers_iqr")}: {outliers_iqr}")
  