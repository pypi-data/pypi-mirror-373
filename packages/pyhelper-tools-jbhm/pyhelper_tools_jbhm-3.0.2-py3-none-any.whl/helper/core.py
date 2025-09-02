from .submodules.shared import ( ast, asyncio, csv, inspect, json, math, os, re, struct, sys, time, Callable,
    Path, Any, Dict, List, Optional, Set, Tuple, Union, mpl, plt, np, pd,
    sns, sa, FigureCanvasTkAgg, PdfReader, kurtosis, norm, skew, PCA, StandardScaler, Column, MetaData, Table,
    create_engine, func, select, text, SQLAlchemyError, sessionmaker,
    tk, filedialog, messagebox, ttk, ScrolledText, ET,
    gpd, warnings, t, show_gui_popup, show_alert_popup, format_number,
    display, Markdown, IN_JUPYTER, set_language, REGISTRY, register, 
    load_user_translations, GridSpec, datetime)

from .submodules.graph import ( hbar, vbar, pie, boxplot, histo, 
    heatmap, table, scatter, lineplot, kdeplot, 
    jointplot, violinplot, pairplot, countplot, lmplot, 
    swarmplot, regplot, barplot, stripplot)

from .submodules.pyswitch import Switch, switch, AsyncSwitch, async_switch

from .submodules.caller import read, call

from .submodules.statics import get_moda, get_media, get_median, get_rank, get_var, get_desv, disp, IQR

from .submodules.manager import normalize, conditional, convert_file

from .submodules.DBManager import manageDB, DataBase

from .submodules.checker import check_syntax, run, PythonFileChecker

from .submodules.timer import Timer

from .submodules.progress_bar import ProgressBar

from .submodules.resource_monitor import ResourceMonitor

date = datetime.datetime(1997,10,23)
test_df = pd.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': [10, 20, 30, 40, 50],
    'C': ['X', 'Y', 'X', 'Z', 'Y'],
    'UUID': '2eb9f3fc-bc5c-41ee-bc27-1f23eff5c279',
    'E': date,
    'id': 636
})


def fig_to_img(fig):
    """Convierte una figura matplotlib a una imagen para mostrar en otro gráfico"""
    fig.canvas.draw()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return img


def generate_all_previews(preview_data):
    preview_title = t("function_preview_title")
    preview_error = t("preview_error_message")

    graph_previews = {}
    for func_name, data in preview_data.items():
        try:
            result = data["preview_func"]()
            if hasattr(result, "figure"):
                graph_previews[func_name] = data
        except:
            pass

    num_funcs = len(graph_previews)
    if num_funcs == 0:
        return None

    rows = (num_funcs + 1) // 2
    fig_height = rows * 6
    fig_width = 18
    fig = plt.figure(figsize=(fig_width, fig_height), tight_layout=True)
    gs = GridSpec(rows, 2, figure=fig)

    for idx, (func_name, data) in enumerate(graph_previews.items()):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])

        try:
            result = data["preview_func"]()
            if hasattr(result, "figure"):
                result.canvas.draw()
                img = np.frombuffer(result.canvas.tostring_rgb(), dtype=np.uint8)
                img = img.reshape(result.canvas.get_width_height()[::-1] + (3,))
                ax.imshow(img)
                ax.axis("off")
                plt.close(result.figure)
        except Exception as e:
            ax.text(
                0.5,
                0.5,
                preview_error.format(error=str(e)),
                ha="center",
                va="center",
                color="red",
            )
            ax.axis("off")

        ax.set_title(f"{func_name}", fontsize=12)

    return fig


def help(type: str = None):

    translations_map = {
        "preview_error": "preview_error",
        "error_in_gui": "error_in_gui",
        "help_error": "help_error",
        "function_preview_title": "function_preview_title",
        "preview_error_message": "preview_error_message",
        "async_preview_not_available": "async_preview_not_available",
        "preview": "preview",
        "example": "example",
        "description": "description",
        "help_available_functions": "help_available_functions",
        "help_usage": "help_usage",
        "title_all": "title_all",
    }

    translated = {}
    for key, value in translations_map.items():
        translated[key] = Switch(value)(
            lambda x: value,
            lambda: t(value),
            "default",
            lambda: value.replace("_", " ").title(),
        )

    help_map = {
        "get_moda": {
            translated["description"]: t("get_moda_description"),
            translated["example"]: "get_moda(np.array([1, 2, 2, 3, 3, 3]), with_repetition=True, decimals=2)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("moda_title"),
                content=str(get_moda(np.array([1, 2, 2, 3, 3, 3]), with_repetition=True, decimals=2)),
                preview_mode=True,
            ),
        },
        "get_media": {
            translated["description"]: t("get_media_description"),
            translated["example"]: "get_media(np.array([1, 2, 3, 4, 5]), nan=False, decimals=2)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("media_title"),
                content=str(get_media(np.array([1, 2, 3, 4, 5]), nan=False, decimals=2)),
                preview_mode=True,
            ),
        },
        "get_median": {
            translated["description"]: t("get_median_description"),
            translated["example"]: "get_median(np.array([1, 2, 3, 4, 5]), nan=False, decimals=2)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("mediana_title"),
                content=str(get_median(np.array([1, 2, 3, 4, 5]), nan=False, decimals=2)),
                preview_mode=True,
            ),
        },
        "get_rank": {
            translated["description"]: t("get_rank_description"),
            translated["example"]: "get_rank(test_df, 'A', decimals=2)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("rango_title"),
                content=str(get_rank(test_df, 'A', decimals=2)),
                preview_mode=True,
            ),
        },
        "get_var": {
            translated["description"]: t("get_var_description"),
            translated["example"]: "get_var(test_df, 'A', decimals=2)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("varianza_title"),
                content=str(get_var(test_df, 'A', decimals=2)),
                preview_mode=True,
            ),
        },
        "get_desv": {
            translated["description"]: t("get_desv_description"),
            translated["example"]: "get_desv(test_df, 'A', decimals=2)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("desviacion_estandar_title"),
                content=str(get_desv(test_df, 'A', decimals=2)),
                preview_mode=True,
            ),
        },
        "disp": {
            translated["description"]: t("disp_description"),
            translated["example"]: "disp(df: pd.DataFrame, column: str, condition: pd.Series = None)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("dispersion_title"),
                content=str(disp(test_df, 'A', condition=test_df['A'] > 2)),
                preview_mode=True,
            ),
        },
        "IQR": {
            translated["description"]: t("IQR_description"),
            translated["example"]: "IQR(df: pd.DataFrame, column: str = None)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("rango_intercuartilico_title"),
                content=str(IQR(test_df, 'A')),
                preview_mode=True,
            ),
        },
        "call": {
            translated["description"]: t("call_description"),
            translated["example"]: "call('filename', type='csv', path='./data', timeout=5)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("call_function_title"),
                content=t("file_read_function_preview"),
                preview_mode=True,
            ),
        },
        "read": {
            translated["description"]: t("read_description"),
            translated["example"]: "read('file.csv')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("read_function_title"),
                content=t("file_read_function_preview"),
                preview_mode=True,
            ),
        },
        "check_syntax": {
            translated["description"]: t("check_syntax_description"),
            translated["example"]: "check_syntax('my_script.py')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("check_syntax_title"),
                content=t("syntax_check_function_preview"),
                preview_mode=True,
            ),
        },
        "run": {
            translated["description"]: t("run_description"),
            translated["example"]: "run('script.py')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("run_function_title"),
                content=t("run_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.exportData": {
            translated["description"]: t("exportData_description"),
            translated["example"]: "db.exportData(table_names='all', format_type='csv')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("export_data_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.addTable": {
            translated["description"]: t("addTable_description"),
            translated["example"]: "db.addTable('new_table', {'col1': 'int', 'col2': 'str'})",
            translated["preview"]: lambda: show_gui_popup(
                title=t("add_table_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.mergeTable": {
            translated["description"]: t("mergeTable_description"),
            translated["example"]: "db.mergeTable('table1', 'table2', on=['id'])",
            translated["preview"]: lambda: show_gui_popup(
                title=t("merge_table_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.join": {
            translated["description"]: t("join_description"),
            translated["example"]: "db.join('inner', 'table1', 'table2', on=['id'])",
            translated["preview"]: lambda: show_gui_popup(
                title=t("join_tables_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.drop": {
            translated["description"]: t("drop_description"),
            translated["example"]: "db.drop('table1', 'table2', cascade=True)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("drop_tables_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.cascadeDelete": {
            translated["description"]: t("cascadeDelete_description"),
            translated["example"]: "db.cascadeDelete('table', 'id = 5')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("cascade_delete_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.recursiveQuery": {
            translated["description"]: t("recursiveQuery_description"),
            translated["example"]: "db.recursiveQuery('employees', 'manager_id IS NULL', 'manager_id = employee_id')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("recursive_query_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.windowFunction": {
            translated["description"]: t("windowFunction_description"),
            translated["example"]: "db.windowFunction('sales', 'ROW_NUMBER', ['region'], ['date'])",
            translated["preview"]: lambda: show_gui_popup(
                title=t("window_function_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.executeRawSQL": {
            translated["description"]: t("executeRawSQL_description"),
            translated["example"]: "db.executeRawSQL('SELECT * FROM table WHERE condition')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("execute_raw_sql_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "DataBase.show": {
            translated["description"]: t("show_description"),
            translated["example"]: "db.show(table_names='all', limit=100)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("show_tables_title"),
                content=t("database_function_preview"),
                preview_mode=True,
            ),
        },
        "hbar": {
            translated["description"]: t("hbar_description"),
            translated["example"]: "hbar( data: pd.Series, title: str, xlabel: str, ylabel: str, save_path: Optional[str] = None, show: bool = True, color: Union[str, List[str]] = 'skyblue', **kwargs)",
            translated["preview"]: lambda: hbar(
                test_df['A'],
                t("ejemplo_hbar_title"),
                t("valores_label"),
                t("categorias_label"),
                show=False,
            ),
        },
        "vbar": {
            translated["description"]: t("vbar_description"),
            translated["example"]: "vbar(test_df['A'], 'Title', 'X Label', 'Y Label', color='skyblue')",
            translated["preview"]: lambda: vbar(
                test_df['A'],
                t("ejemplo_vbar_title"),
                t("categorias_label"),
                t("valores_label"),
                show=False,
            ),
        },
        "pie": {
            translated["description"]: t("pie_description"),
            translated["example"]: "pie([30, 40, 30], ['A', 'B', 'C'], 'Título del Gráfico')",
            translated["preview"]: lambda: pie(
                [30, 40, 30], ["A", "B", "C"], t("ejemplo_pie_title"), show=False
            ),
        },
        "boxplot": {
            translated["description"]: t("boxplot_description"),
            translated["example"]: "boxplot(test_df, x='C', y='A')",
            translated["preview"]: lambda: boxplot(
                test_df, x='C', y='A', title=t("boxplot_example_title"), show=False
            ),
        },
        "histo": {
            translated["description"]: t("histo_description"),
            translated["example"]: "histo(test_df, 'A', bins=5, title='Histograma')",
            translated["preview"]: lambda: histo(
                test_df, 'A', bins=5, title=t("histogram_example_title"), show=False
            ),
        },
        "heatmap": {
            translated["description"]: t("heatmap_description"),
            translated["example"]: "heatmap(test_df.corr(), title='Correlation Heatmap')",
            translated["preview"]: lambda: heatmap(
                test_df[['A', 'B']].corr(), title=t("heatmap_example_title"), show=False
            ),
        },
        "table": {
            translated["description"]: t("table_description"),
            translated["example"]: "table(test_df.head().values, col_labels=test_df.columns)",
            translated["preview"]: lambda: table(
                test_df.head().values,
                col_labels=test_df.columns.tolist(),
                title=t("tabla_ejemplo_title"),
                show=False,
            ),
        },
        "scatter": {
            translated["description"]: t("scatter_description"),
            translated["example"]: "scatter(test_df, x='A', y='B')",
            translated["preview"]: lambda: scatter(
                test_df, x='A', y='B', title=t("scatter_plot_example_title"), show=False
            ),
        },
        "lineplot": {
            translated["description"]: t("lineplot_description"),
            translated["example"]: "lineplot(test_df, x='A', y='B')",
            translated["preview"]: lambda: lineplot(
                test_df, x='A', y='B', title=t("line_plot_example_title"), show=False
            ),
        },
        "kdeplot": {
            translated["description"]: t("kdeplot_description"),
            translated["example"]: "kdeplot(test_df, 'A')",
            translated["preview"]: lambda: kdeplot(
                test_df, 'A', title=t("kde_plot_example_title"), show=False
            ),
        },
        "jointplot": {
            translated["description"]: t("jointplot_description"),
            translated["example"]: "jointplot(test_df, x='A', y='B')",
            translated["preview"]: lambda: jointplot(
                test_df, x='A', y='B', title=t("joint_plot_example_title"), show=False
            ),
        },
        "violinplot": {
            translated["description"]: t("violinplot_description"),
            translated["example"]: "violinplot(test_df, x='C', y='A')",
            translated["preview"]: lambda: violinplot(
                test_df, x='C', y='A', title=t("violin_plot_example_title"), show=False
            ),
        },
        "pairplot": {
            translated["description"]: t("pairplot_description"),
            translated["example"]: "pairplot(test_df, vars=['A', 'B'])",
            translated["preview"]: lambda: pairplot(
                test_df[['A', 'B', 'C']], title=t("pair_plot_example_title"), show=False
            ),
        },
        "countplot": {
            translated["description"]: t("countplot_description"),
            translated["example"]: "countplot(test_df, x='C')",
            translated["preview"]: lambda: countplot(
                test_df, x='C', title=t("count_plot_example_title"), show=False
            ),
        },
        "lmplot": {
            translated["description"]: t("lmplot_description"),
            translated["example"]: "lmplot(test_df, x='A', y='B')",
            translated["preview"]: lambda: lmplot(
                test_df, x='A', y='B', title=t("lm_plot_example_title"), show=False
            ),
        },
        "swarmplot": {
            translated["description"]: t("swarmplot_description"),
            translated["example"]: "swarmplot(test_df, x='C', y='A')",
            translated["preview"]: lambda: swarmplot(
                test_df, x='C', y='A', title=t("swarm_plot_example_title"), show=False
            ),
        },
        "regplot": {
            translated["description"]: t("regplot_description"),
            translated["example"]: "regplot(test_df, x='A', y='B')",
            translated["preview"]: lambda: regplot(
                test_df, x='A', y='B', title=t("reg_plot_example_title"), show=False
            ),
        },
        "barplot": {
            translated["description"]: t("barplot_description"),
            translated["example"]: "barplot(test_df, x='C', y='A')",
            translated["preview"]: lambda: barplot(
                test_df, x='C', y='A', title=t("bar_plot_example_title"), show=False
            ),
        },
        "stripplot": {
            translated["description"]: t("stripplot_description"),
            translated["example"]: "stripplot(test_df, x='C', y='A')",
            translated["preview"]: lambda: stripplot(
                test_df, x='C', y='A', title=t("strip_plot_example_title"), show=False
            ),
        },
        "normalize": {
            translated["description"]: t("normalize_description"),
            translated["example"]: "normalize(np.array([1, 2, 3, 4, 5]))",
            translated["preview"]: lambda: show_gui_popup(
                title=t("normalize_title"),
                content=str(normalize(np.array([1, 2, 3, 4, 5]))),
                preview_mode=True,
            ),
        },
        "conditional": {
            translated["description"]: t("conditional_description"),
            translated["example"]: "conditional(test_df, [test_df['A'] > 2], ['greater'], 'result_col')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("conditional_title"),
                content=str(conditional(test_df, [test_df['A'] > 2], ['greater'], 'result_col').head()),
                preview_mode=True,
            ),
        },
        "convert_file": {
            translated["description"]: t("convert_file_description"),
            translated["example"]: "convert_file('input.shp', 'output.csv')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("convert_file_title"),
                content=t("conversion_function_preview"),
                preview_mode=True,
            ),
        },
        "Switch": {
            translated["description"]: t("Switch_description"),
            translated["example"]: "Switch(value)(case1, action1, case2, action2, 'default', default_action)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("switch_example_title"),
                content=str(Switch(2)(1, t("uno_text"), 2, t("dos_text"), "default", t("otro_text"))),
                preview_mode=True,
            ),
        },
        "switch": {
            translated["description"]: t("switch_description"),
            translated["example"]: "switch(value, {case1, action1, case2, action2, 'default', default_action})",
            translated["preview"]: lambda: show_gui_popup(
                title=t("switch_example_title"),
                content=str(switch(2, {1, t("uno_text"), 2, t("dos_text"), "default", t("otro_text")})),
                preview_mode=True,
            ),
        },
        "AsyncSwitch": {
            translated["description"]: t("AsyncSwitch_description"),
            translated["example"]: "await AsyncSwitch(value)(case1, action1, case2, action2, 'default', default_action)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("async_switch_title"),
                content=t("async_function_preview"),
                preview_mode=True,
            ),
        },
        "async_switch": {
            translated["description"]: t("async_switch_description"),
            translated["example"]: "await async_switch(value, case1, action1, case2, action2, 'default', default_action)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("async_switch_title"),
                content=t("async_function_preview"),
                preview_mode=True,
            ),
        },
        "fig_to_img": {
            translated["description"]: t("fig_to_img_description"),
            translated["example"]: "image_array = fig_to_img(figure)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("fig_to_image_title"),
                content=t("figure_conversion_preview"),
                preview_mode=True,
            ),
        },
        "format_number": {
            translated["description"]: t("format_number_description"),
            translated["example"]: "format_number(1234.5678, decimals=2)",
            translated["preview"]: lambda: show_gui_popup(
                title=t("format_number_title"),
                content=format_number(1234.5678, decimals=2),
                preview_mode=True,
            ),
        },
        "load_user_translations": {
            translated["description"]: t("load_user_translations_description"),
            translated["example"]: "load_user_translations('my_translations.json')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("load_user_translations_title"),
                content=t("translation_load_preview"),
                preview_mode=True,
            ),
        },
        "register": {
            translated["description"]: t("register_description"),
            translated["example"]: "@register('my_function')\ndef my_function(): ...",
            translated["preview"]: lambda: show_gui_popup(
                title=t("register_title"),
                content=t("register_decorator_preview"),
                preview_mode=True,
            ),
        },
        "set_language": {
            translated["description"]: t("set_language_description"),
            translated["example"]: "set_language('es')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("set_language_title"),
                content=t("language_setting_preview"),
                preview_mode=True,
            ),
        },
        "show_gui_popup": {
            translated["description"]: t("show_gui_popup_description"),
            translated["example"]: "show_gui_popup('Título', 'Contenido del mensaje')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("show_gui_popup_example_title"),
                content=t("show_gui_popup_demo"),
                preview_mode=True,
            ),
        },
        "t": {
            translated["description"]: t("t_description"),
            translated["example"]: "translated_text = t('key_name')",
            translated["preview"]: lambda: show_gui_popup(
                title=t("translation_function_title"),
                content=f"{t('example_text')}: {t('help_available_functions')}",
                preview_mode=True,
            ),
        },
    }

    functions = sorted(help_map.keys())

    if type is None:
        if IN_JUPYTER:
            display(Markdown(f"**{t('help_available_functions')}**"))
            for func in functions:
                display(Markdown(f"- `{func}`"))
            display(Markdown(f"\n*{t('help_usage')}*"))
        else:
            func_list = "\n".join(f"- {func}" for func in functions)
            show_gui_popup(
                t("title_all"),
                f"{t('help_available_functions')}\n{func_list}\n\n{t('help_usage')}",
            )
        return

    if not isinstance(type, str):
        msg = t("error_instance_type")
        if IN_JUPYTER:
            display(Markdown(f"**Error:** {msg}"))
        else:
            show_gui_popup(title=t("error_in_gui"), content=msg)
        return

    type = type.lower()

    if type == "all":
        full_doc = []
        preview_data = {}

        for func_name in functions:
            entry = help_map.get(func_name, {})
            doc = entry.get(translated["description"], "")
            example = entry.get(translated["example"], "")

            func_doc = f"{func_name.upper()}\n\n{doc}\n\nExample:\n{example}"
            full_doc.append(func_doc)

            if translated["preview"] in entry:
                preview_data[func_name] = {
                    translated["example"]: example,
                    "preview_func": entry[translated["preview"]],
                }

        full_doc_text = (
            "\n\n"
            + ("=" * 50).join("\n\n")
            + "\n\n".join(full_doc)
            + "\n\n"
            + ("=" * 50)
        )

        if IN_JUPYTER:
            display(Markdown(full_doc_text))
            for func_name, data in preview_data.items():
                display(Markdown(f"**Preview for {func_name}**"))
                try:
                    result = data["preview_func"]()
                    if hasattr(result, "figure"):
                        display(result.figure)
                        plt.close(result.figure)
                    else:
                        display(Markdown(f"```\n{str(result)}\n```"))
                except Exception as e:
                    display(Markdown(f"**Error in preview:**\n```\n{str(e)}\n```"))
        else:
            show_gui_popup(
                t("title_all"),
                full_doc_text,
                plot_function=lambda: generate_all_previews(preview_data),
            )
        return

    if type in functions:
        doc = help_map.get(type, {}).get(translated["description"], t(type))
        entry = help_map.get(type, {})
        example = entry.get(translated["example"], "")
        preview_func = entry.get(translated["preview"])

        if IN_JUPYTER:
            output = f"**{type.upper()}**\n```python\n{doc.strip()}\n```"
            if example:
                output += f"\n\n**{t('example')}:**\n```python\n{example}\n```"
            display(Markdown(output))

            if preview_func:
                try:
                    print(f"\n**{t('preview')}:**")
                    preview_func()
                except Exception as e:
                    display(Markdown(f"**{t('preview_error')}:**\n```\n{str(e)}\n```"))
        else:
            full_text = doc.strip()
            if example:
                full_text += f"\n\n{t('example')}:\n{example}"

            fig = None
            if preview_func:
                try:
                    result = preview_func()
                    if hasattr(result, "figure"):
                        fig = result.figure
                except Exception as e:
                    messagebox.showerror(f"{t('preview_error')} {type}", str(e))

            show_gui_popup(type.upper(), full_text, fig=fig)
    else:
        error_msg = t("help_error").format(type)
        if IN_JUPYTER:
            display(Markdown(f"**{error_msg}**"))
        else:
            show_gui_popup(t("error_in_gui"), error_msg)


__all__ = ["Any", "ast", "async_switch", "asyncio", "AsyncSwitch", "barplot", "boxplot", "call", "Callable", "check_syntax", 
           "Column", "conditional", "convert_file", "countplot", "create_engine", "csv", "DataBase", "datetime", "Dict", "disp", 
           "display", "ET", "fig_to_img", "FigureCanvasTkAgg", "filedialog", "format_number", "func", "generate_all_previews", "get_desv", 
           "get_media", "get_median", "get_moda", "get_rank", "get_var", "gpd", "GridSpec", "hbar", "heatmap", "help", "histo", "IN_JUPYTER", 
           "inspect", "IQR", "jointplot", "json", "kdeplot", "kurtosis", "lineplot", "List", "lmplot", "load_user_translations", "manageDB", 
           "Markdown", "math", "messagebox", "MetaData", "mpl", "norm", "normalize", "np", "Optional", "os", "pairplot", "Path", "PCA", "pd", 
           "PdfReader", "pie", "plt", "PythonFileChecker", "re", "read", "register", "REGISTRY", "regplot", "run", "sa", "scatter", 
           "ScrolledText", "select", "sessionmaker", "Set", "set_language", "show_alert_popup", "show_gui_popup", "skew", "sns", 
           "SQLAlchemyError", "StandardScaler", "stripplot", "struct", "swarmplot", "Switch", "switch", "sys", "t", "Table", "table", "text", 
           "time", "tk", "ttk", "Tuple", "Union", "vbar", "violinplot", "warnings", 
           #v3.0.0 new functions
           "Timer", "ProgressBar", "ResourceMonitor"]
