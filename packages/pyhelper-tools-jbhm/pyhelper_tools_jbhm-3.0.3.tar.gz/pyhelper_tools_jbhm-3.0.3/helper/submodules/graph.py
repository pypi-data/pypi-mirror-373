import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from typing import Optional, Union, List
from .shared import BIG_SIZE, NORMAL_SIZE, format_number, show_gui_popup, t
from .pyswitch import Switch



_non_interactive_mode = False


def _set_non_interactive_mode(enable: bool):
    """Configura el modo no interactivo globalmente"""
    global _non_interactive_mode
    _non_interactive_mode = enable
    if enable:
        mpl.use("Agg")


def _validate_data(data, data_type="dataframe"):
    """Valida datos comunes para todas las funciones"""
    if data is None or (hasattr(data, "empty") and data.empty):
        show_gui_popup("Error", t("ERROR_EMPTY_DATA"))
        return False
    return True


def _validate_columns(df, columns):
    """Valida que las columnas existan en el DataFrame"""
    if not columns:
        return True
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        show_gui_popup(
            "Error", t("ERROR_COLUMN_NOT_FOUND").format(", ".join(missing_cols))
        )
        return False
    return True


def _handle_color_palette(color, palette, hue, default_palette="deep"):
    """Maneja consistentemente los parámetros de color y palette"""
    color_params = {}

    if hue and palette:
        color_params["palette"] = palette
        color_params["hue"] = hue
    elif hue and not palette:
        color_params["palette"] = default_palette
        color_params["hue"] = hue
    elif color and not hue:
        color_params["color"] = color
    elif palette and not hue:
        color_params["palette"] = palette
        color_params["legend"] = False
    else:
        color_params["palette"] = default_palette

    return color_params


def _save_and_show_fig(fig, save_path, show):
    """Maneja el guardado y visualización de figuras"""
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show and not _non_interactive_mode:
        plt.show()
        return None
    else:
        return fig


def _format_number_based_on_value(value):
    """Formatea números basado en su magnitud usando Switch"""
    return Switch(value)(
        lambda x: abs(x) > 1000, lambda: format_number(value, use_decimals=False),
        lambda x: 0 < abs(x) < 0.001, lambda: format_number(value, use_decimals=True, decimals=4),
        lambda x: abs(x) < 1, lambda: format_number(value, use_decimals=True, decimals=3),
        "default", lambda: format_number(value, use_decimals=True, decimals=2),
    )


def hbar(
    data: pd.Series,
    title: str,
    xlabel: str,
    ylabel: str,
    save_path: Optional[str] = None,
    show: bool = True,
    color: Union[str, List[str]] = "skyblue",
    **kwargs,
):
    try:
        if not _validate_data(data, "series"):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))
        y_pos = range(len(data))
        bars = plt.barh(y_pos, data.values, color=color)

        plt.yticks(ticks=y_pos, labels=data.index)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(axis="x", alpha=0.3)

        for i, bar in enumerate(bars):
            width = bar.get_width()
            formatted_text = _format_number_based_on_value(width)
            plt.text(
                width + 2,
                bar.get_y() + bar.get_height() / 2,
                formatted_text,
                va="center",
            )
        try:
            plt.tight_layout()
        except Exception:
            None

        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def vbar(
    data: Union[pd.Series, pd.DataFrame],
    title: str,
    xlabel: str,
    ylabel: str,
    save_path: Optional[str] = None,
    show: bool = True,
    color: Union[str, List[str]] = "skyblue",
    **kwargs,
):
    try:
        if not _validate_data(data):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))
        bars = plt.bar(data.index, data.values, color=color)

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(axis="y", alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            x = bar.get_x() + bar.get_width() / 2
            formatted_text = _format_number_based_on_value(height)
            plt.text(
                x, height + (height * 0.02), formatted_text, ha="center", va="bottom"
            )

        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def pie(
    valores: Union[List[float], np.ndarray, pd.Series],
    etiquetas: Union[List[str], np.ndarray, pd.Series],
    title: str,
    save_path: Optional[str] = None,
    show: bool = True,
    colors: Optional[List[str]] = None,
    decimales: int = 1,
    **kwargs,
):
    try:
        if len(valores) == 0 or len(etiquetas) == 0:
            show_gui_popup("Error", t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig, ax = plt.subplots(figsize=kwargs.get("figsize", NORMAL_SIZE))

        use_labels = Switch(len(etiquetas))(
            lambda x: x <= 10, lambda: True, 
            "default", lambda: False)

        labels = etiquetas if use_labels else None

        def format_pct(pct):
            return format_number(
                pct / 100, use_decimals=True, decimals=decimales, percent=True
            )

        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            autopct=format_pct,
            colors=colors if colors else plt.cm.tab20.colors,
            startangle=90,
            wedgeprops={"edgecolor": "black", "linewidth": 0.8},
            textprops={"fontsize": 8},
        )

        if not use_labels:
            ax.legend(
                wedges,
                etiquetas,
                title="Categories",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=8,
                title_fontsize=9,
            )

        ax.set_title(title)
        ax.axis("equal")
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def _create_seaborn_plot(
    plot_type, df, x, y, hue, color, palette, default_palette, **kwargs
):
    """Función helper para crear plots de seaborn con manejo de color/palette"""
    color_params = _handle_color_palette(color, palette, hue, default_palette)

    plot_function = Switch(plot_type)({
        "cases":[
        {"case": lambda x: x == "boxplot", "then": lambda: sns.boxplot},
        {"case": lambda x: x == "violinplot", "then": lambda: sns.violinplot},
        {"case": lambda x: x == "countplot", "then": lambda: sns.countplot},
        {"case": lambda x: x == "barplot", "then": lambda: sns.barplot},
        {"case": lambda x: x == "stripplot", "then": lambda: sns.stripplot},
        {"case": lambda x: x == "swarmplot", "then": lambda: sns.swarmplot}],
        "default": lambda: None,
    })

    if plot_function:
        return plot_function(data=df, x=x, y=y, **color_params, **kwargs)
    return None


def boxplot(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: Optional[Union[str, List[str]]] = "tab10",
    **kwargs,
):
    try:
        if not _validate_data(df):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))

        _create_seaborn_plot(
            "boxplot", df, x, y, hue, color, palette, "tab10", **kwargs
        )

        plt.title(title)
        if x:
            plt.xlabel(x)
        if y:
            plt.ylabel(y)
        try:
            if hue:
                plt.legend(title=hue)
        except Exception:
            None

        plt.grid(True, alpha=0.4)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def histo(
    df: pd.DataFrame,
    column: str,
    condition: Optional[pd.Series] = None,
    bins: int = 20,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = "skyblue",
    **kwargs,
):
    try:
        if not _validate_data(df) or not _validate_columns(df, [column]):
            return None

        if condition is not None:
            df = df[condition]

        if df[column].dropna().empty:
            show_gui_popup("Error", t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", NORMAL_SIZE))
        plt.hist(
            df[column].dropna(), bins=bins, color=color, edgecolor="black", alpha=0.7
        )

        plt.title(title or f"Histogram of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def heatmap(
    data: Union[pd.DataFrame, np.ndarray],
    index_col: Optional[str] = None,
    column_col: Optional[str] = None,
    value_col: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    cmap: str = "YlGnBu",
    annot: bool = True,
    **kwargs,
):
    try:
        if isinstance(data, pd.DataFrame):
            if all([index_col, column_col, value_col]):
                if not _validate_columns(data, [index_col, column_col, value_col]):
                    return None
                tabla = (
                    data.groupby([index_col, column_col])[value_col]
                    .size()
                    .unstack(fill_value=0)
                )
            else:
                tabla = data
        else:
            tabla = pd.DataFrame(data)

        if not _validate_data(tabla):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", NORMAL_SIZE))

        fmt_switch = Switch(annot)(
            lambda x: x == True, lambda: "d" if tabla.dtypes.iloc[0].kind in "iubB" else ".2f", 
            lambda x: x == False, lambda: None
        )

        sns.heatmap(
            tabla,
            cmap=cmap,
            annot=annot,
            fmt=fmt_switch,
            annot_kws={"size": 7},
            linewidths=0.1,
            **kwargs,
        )

        plt.title(title)
        if index_col:
            plt.ylabel(index_col)
        if column_col:
            plt.xlabel(column_col)
        plt.xticks(rotation=0)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def table(
    data: Union[List[List], np.ndarray, pd.DataFrame],
    col_labels: Optional[List[str]] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    **kwargs,
):
    try:
        if len(data) == 0:
            show_gui_popup("Error", t("ERROR_EMPTY_DATA"))
            return None

        if not show:
            _set_non_interactive_mode(True)

        if isinstance(data, pd.DataFrame):
            if col_labels is None:
                col_labels = data.columns.tolist()
            data = data.values.tolist()
        elif isinstance(data, np.ndarray):
            data = data.tolist()

        fig, ax = plt.subplots(figsize=kwargs.get("figsize", NORMAL_SIZE))
        ax.axis("off")

        tabla = ax.table(
            cellText=data, colLabels=col_labels, cellLoc="center", loc="top"
        )
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(12)
        tabla.scale(1.5, 1.5)

        if title:
            plt.title(title)

        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "viridis",
    **kwargs,
):
    try:
        required_cols = [x, y] + ([hue] if hue else [])
        if not _validate_data(df) or not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))


        if hue:
            sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
        elif color:
            plt.scatter(df[x], df[y], color=color, **kwargs)
        else:
            plt.scatter(df[x], df[y], color="blue", **kwargs)

        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, alpha=0.3)
        if hue:
            plt.legend(title=hue)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def lineplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "tab10",
    **kwargs,
):
    try:
        required_cols = [x, y] + ([hue] if hue else [])
        if not _validate_data(df) or not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))


        if hue:
            sns.lineplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
            plt.legend(title=hue)
        elif color:
            plt.plot(df[x], df[y], color=color, **kwargs)
        else:
            plt.plot(df[x], df[y], color="blue", **kwargs)

        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def kdeplot(
    df: pd.DataFrame,
    column: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "husl",
    **kwargs,
):
    try:
        required_cols = [column] + ([hue] if hue else [])
        if not _validate_data(df) or not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", NORMAL_SIZE))


        if hue:
            sns.kdeplot(data=df, x=column, hue=hue, palette=palette, **kwargs)
        elif color:
            sns.kdeplot(data=df[column], color=color, **kwargs)
        else:
            sns.kdeplot(data=df[column], color="blue", **kwargs)

        plt.title(title or f"KDE Plot of {column}")
        plt.xlabel(column)
        plt.ylabel("Density")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def jointplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[str] = None,
    kind: str = "scatter",
    **kwargs,
):
    try:
        if not _validate_data(df) or not _validate_columns(df, [x, y]):
            return None

        if not show:
            _set_non_interactive_mode(True)


        if hue:
            g = _create_jointplot_with_hue(df, x, y, hue, **kwargs)
        elif color:
            g = sns.jointplot(data=df, x=x, y=y, color=color, kind=kind, **kwargs)
        else:
            g = sns.jointplot(data=df, x=x, y=y, color="blue", kind=kind, **kwargs)

        if title:
            g.figure.suptitle(title, y=1.02)

        return _save_and_show_fig(g.figure, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def _create_jointplot_with_hue(df, x, y, hue, **kwargs):
    """Helper function for jointplot with hue"""
    g = sns.JointGrid(data=df, x=x, y=y, hue=hue, **kwargs)
    g.plot_joint(sns.scatterplot)
    g.plot_marginals(sns.histplot, kde=True)
    return g


def violinplot(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "muted",
    **kwargs,
):
    try:
        if not _validate_data(df):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))

        _create_seaborn_plot(
            "violinplot", df, x, y, hue, color, palette, "muted", **kwargs
        )

        plt.title(title)
        if x:
            plt.xlabel(x)
        if y:
            plt.ylabel(y)
        if hue:
            try:
                plt.legend(title=hue)
            except Exception:
                None
        else:
            hue = x
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def pairplot(
    df: pd.DataFrame,
    vars: Optional[List[str]] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    palette: str = "husl",
    **kwargs,
):
    try:
        if not _validate_data(df):
            return None

        if vars and not _validate_columns(df, vars):
            return None

        if not show:
            _set_non_interactive_mode(True)

        vars_to_use = Switch(vars)(
            lambda x: x == None, lambda: df.select_dtypes(include=[np.number]).columns.tolist(),
            "default", lambda: vars,
        )

        g = sns.pairplot(df, vars=vars_to_use, hue=hue, palette=palette, **kwargs)

        if title:
            g.figure.suptitle(title, y=1.02)

        return _save_and_show_fig(g.figure, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def countplot(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs,
):
    try:
        if not _validate_data(df):
            return None

        required_cols = [col for col in [x, y, hue] if col is not None]
        if required_cols and not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))

        _create_seaborn_plot(
            "countplot", df, x, y, hue, color, palette, "deep", **kwargs
        )

        plt.title(title)
        if x:
            plt.xlabel(x)
        if y:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def lmplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    palette: str = "viridis",
    **kwargs,
):
    try:
        required_cols = [x, y] + ([hue] if hue else [])
        if not _validate_data(df) or not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        g = sns.lmplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)

        if title:
            g.figure.suptitle(title, y=1.02)

        return _save_and_show_fig(g.figure, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def swarmplot(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs,
):
    try:
        if not _validate_data(df):
            return None

        required_cols = [col for col in [x, y, hue] if col is not None]
        if required_cols and not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))

        _create_seaborn_plot(
            "swarmplot", df, x, y, hue, color, palette, "deep", **kwargs
        )

        plt.title(title)
        if x:
            plt.xlabel(x)
        if y:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def regplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[str] = None,
    **kwargs,
):
    try:
        if not _validate_data(df) or not _validate_columns(df, [x, y]):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))

        sns.regplot(data=df, x=x, y=y, color=color if color else "blue", **kwargs)

        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def barplot(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs,
):
    try:
        if not _validate_data(df):
            return None

        required_cols = [col for col in [x, y, hue] if col is not None]
        if required_cols and not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))

        _create_seaborn_plot("barplot", df, x, y, hue, color, palette, "deep", **kwargs)

        plt.title(title)
        if x:
            plt.xlabel(x)
        if y:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None


def stripplot(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    color: Optional[Union[str, List[str]]] = None,
    palette: str = "deep",
    **kwargs,
):
    try:
        if not _validate_data(df):
            return None

        required_cols = [col for col in [x, y, hue] if col is not None]
        if required_cols and not _validate_columns(df, required_cols):
            return None

        if not show:
            _set_non_interactive_mode(True)

        fig = plt.figure(figsize=kwargs.get("figsize", BIG_SIZE))

        _create_seaborn_plot(
            "stripplot", df, x, y, hue, color, palette, "deep", **kwargs
        )

        plt.title(title)
        if x:
            plt.xlabel(x)
        if y:
            plt.ylabel(y)
        if hue:
            plt.legend(title=hue)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return _save_and_show_fig(fig, save_path, show)

    except Exception as e:
        show_gui_popup("Error", t("ERROR_PLOT_GENERATION").format(str(e)))
        return None
