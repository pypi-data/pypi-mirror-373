from .shared import (
    Dict,
    List,
    Optional,
    filedialog,
    json,
    Path,
    pd,
    plt,
    create_engine,
    MetaData,
    Table,
    text,
    SQLAlchemyError,
    URL,
    sessionmaker,
    show_gui_popup,
    show_alert_popup,
    show_yesno_popup,
    Union,
    Column,
    sa,
    t,
    pyodbc,
    sys,
    webbrowser
)
from .pyswitch import Switch
import re  # Added for type parsing


class DataBase:
    """Clase para manejo de bases de datos SQL con múltiples funcionalidades."""

    def __init__(self, config: Dict[str, str]):
        """
        Inicializa la conexión a la base de datos.

        Args:
            config: Diccionario con configuración de conexión
                - db_name: Nombre de la base de datos
                - db_host: Host de la base de datos
                - db_user: Usuario
                - db_pass: Contraseña
                - db_port: Puerto
                - db_type: Tipo de BD (mysql, postgresql, mssql)
        """
        self.config = config
        self.engine = None
        self.metadata = MetaData()
        self.session = None
        self.db_version = None  # Almacenar versión de la BD
        try:
            self._connect_()
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "connection_error",
                    f"{t('database_connection_failed')}: {str(e)}",
                )
            raise

    def _connect_(self) -> None:
        """Establece conexión con la base de datos."""
        try:
            db_type = self.config.get("db_type", "mysql").lower()

            if self.config["db_debug"]:
                debug_info = f"""
                    DB Type: {db_type}
                    Host: {self.config['db_host']}
                    Database: {self.config['db_name']}
                    User: {self.config['db_user']}
                    Port: {self.config['db_port']}
                    Password (repr): {repr(self.config['db_pass'])}
                    """
                show_gui_popup("Database Debug", debug_info.strip())

            if db_type == "postgresql":

                import psycopg2


                password = self.config["db_pass"]
                if isinstance(password, str):
                    password = password.encode("latin-1", "ignore").decode("latin-1")

                if self.config["db_debug"]:
                    show_gui_popup(
                        t("debug_title"), f"Password after encoding: {repr(password)}"
                    )


                try:
                    conn = psycopg2.connect(
                        host=self.config["db_host"],
                        database=self.config["db_name"],
                        user=self.config["db_user"],
                        password=password,
                        port=int(self.config["db_port"]),
                        connect_timeout=5,
                    )
                    conn.close()
                    if self.config["db_debug"]:
                        show_gui_popup(t("debug_title"), "Conexión directa exitosa!")
                except Exception as e:
                    if self.config["db_debug"]:
                        show_alert_popup(
                            "warning",
                            "direct_connect_error",
                            f"Error en conexión directa: {e}",
                        )
                    raise



                import urllib.parse

                user = urllib.parse.quote_plus(self.config["db_user"])
                password_encoded = urllib.parse.quote_plus(password)
                host = urllib.parse.quote_plus(self.config["db_host"])
                database = urllib.parse.quote_plus(self.config["db_name"])

                connection_string = f"postgresql://{user}:{password_encoded}@{host}:{self.config['db_port']}/{database}"
                if self.config["db_debug"]:
                    show_gui_popup(
                        "debug_title", f"Connection string: {connection_string}"
                    )

                self.engine = create_engine(connection_string)

            elif db_type == "mssql":

                connection_string = f"mssql+pyodbc://{self.config['db_user']}:{self.config['db_pass']}@{self.config['db_host']}:{self.config['db_port']}/{self.config['db_name']}?driver=ODBC+Driver+17+for+SQL+Server"
                self.engine = create_engine(connection_string)
            else:

                connection_string = f"mysql+pymysql://{self.config['db_user']}:{self.config['db_pass']}@{self.config['db_host']}:{self.config['db_port']}/{self.config['db_name']}"
                self.engine = create_engine(connection_string)

            Session = sessionmaker(bind=self.engine)
            self.session = Session()


            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if self.config["db_debug"]:
                    show_gui_popup(
                        t("debug_title"), "Test query ejecutado correctamente"
                    )


                if db_type == "mysql":
                    version_result = conn.execute(text("SELECT VERSION()"))
                    self.db_version = version_result.scalar()
                    if self.config["db_debug"]:
                        show_gui_popup(
                            "Database Version", f"MySQL Version: {self.db_version}"
                        )
                elif db_type == "postgresql":
                    version_result = conn.execute(text("SELECT version()"))
                    self.db_version = version_result.scalar()
                elif db_type == "mssql":
                    version_result = conn.execute(text("SELECT @@VERSION"))
                    self.db_version = version_result.scalar()

        except Exception as e:

            error_msg = f"""
            {t('connection_error_details')}:
            - {t('type')}: {db_type}
            - {t('host')}: {self.config.get('db_host')}
            - {t('port')}: {self.config.get('db_port')}
            - {t('database')}: {self.config.get('db_name')}
            - {t('user')}: {self.config.get('db_user')}
            - {t('error')}: {str(e)}
            - {t('error_type')}: {type(e).__name__}
            """
            if self.config["db_debug"]:
                show_alert_popup("error", "connection_error", error_msg)
            raise ConnectionError(f"{t('database_connection_failed')}: {str(e)}")

    def is_empty_table(self, table_name: str) -> bool:
        """Verifica si una tabla existe y está vacía"""
        try:
            if not self.table_exists(table_name):
                return False
                
            query = text(f"SELECT COUNT(*) FROM {table_name}")
            result = self.session.execute(query).scalar()
            return result == 0
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "empty_table_check_error",
                    f"{t('empty_table_check_failed')}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('empty_table_check_failed')}: {str(e)}")

    def _get_all_tables(self) -> List[str]:
        """Obtiene todas las tablas de la base de datos."""
        db_type = self.config.get("db_type", "mysql").lower()
        
        if db_type == "postgresql":
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
        elif db_type == "mssql":
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE'
            """
        else:  # MySQL
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            """
            
        result = pd.read_sql(query, self.engine)
        return result["table_name"].tolist()

    def _get_columns_for_table(
        self, columns: Union[List[str], Dict[str, List[str]]], table_name: str
    ) -> Optional[List[str]]:
        """Obtiene las columnas específicas para una tabla."""
        if columns is None:
            return None
        elif isinstance(columns, dict):
            return columns.get(table_name)
        else:
            return columns

    def _get_where_for_table(
        self, where_condition: Union[str, Dict[str, str]], table_name: str
    ) -> Optional[str]:
        """Obtiene la condición WHERE específica para una tabla."""
        if where_condition is None:
            return None
        elif isinstance(where_condition, dict):
            return where_condition.get(table_name)
        else:
            return where_condition

    def _export_to_sql(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato SQL (INSERT statements)."""
        final_path = output_path.with_suffix(".sql")
        df = pd.read_sql(query, self.engine)

        mode = "a" if output_path.exists() else "w"

        with open(final_path, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write(f"-- Exportación de múltiples tablas\n")
                f.write(f"-- Fecha: {pd.Timestamp.now()}\n\n")

            f.write(f"-- Tabla: {table_name}\n")
            f.write(f"-- Total de registros: {len(df)}\n\n")

            for _, row in df.iterrows():
                columns = []
                values = []

                for col, value in row.items():
                    if pd.notna(value):
                        columns.append(col)
                        if isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            escaped_value = str(value).replace("'", "''")
                            values.append(f"'{escaped_value}'")

                if columns:
                    insert_stmt = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                    f.write(insert_stmt)

            f.write("\n")

        return str(final_path)

    def _export_to_excel(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato Excel con múltiples hojas."""
        final_path = output_path.with_suffix(".xlsx")
        df = pd.read_sql(query, self.engine)

        mode = "a" if output_path.exists() else "w"

        with pd.ExcelWriter(final_path, engine="openpyxl", mode=mode) as writer:
            df.to_excel(
                writer, sheet_name=table_name[:31], index=False
            )  # Limitar a 31 chars

        return str(final_path)

    def _export_to_xml(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato XML con soporte para múltiples tablas."""
        final_path = output_path.with_suffix(".xml")
        df = pd.read_sql(query, self.engine)

        mode = "a" if output_path.exists() else "w"

        if mode == "w":
            xml_content = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                "<database_export>",
            ]
        else:
            with open(final_path, "r", encoding="utf-8") as f:
                existing_content = f.read().splitlines()
            xml_content = existing_content[:-1]  # Remover </database_export>

        xml_content.append(f"  <{table_name}_data>")

        for _, row in df.iterrows():
            xml_content.append(f"    <{table_name}>")
            for col, value in row.items():
                if pd.notna(value):
                    xml_content.append(f"      <{col}>{value}</{col}>")
            xml_content.append(f"    </{table_name}>")

        xml_content.append(f"  </{table_name}_data>")
        xml_content.append("</database_export>")

        with open(final_path, "w", encoding="utf-8") as f:
            f.write("\n".join(xml_content))

        return str(final_path)

    def _export_to_json(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato JSON con estructura para múltiples tablas."""
        final_path = output_path.with_suffix(".json")
        df = pd.read_sql(query, self.engine)

        if output_path.exists():
            with open(final_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_data[table_name] = df.to_dict("records")
            export_data = existing_data
        else:
            export_data = {table_name: df.to_dict("records")}

        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return str(final_path)

    def _export_to_csv(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato CSV."""
        final_path = output_path.with_suffix(".csv")
        df = pd.read_sql(query, self.engine)
        df.to_csv(final_path, index=False)
        return str(final_path)

    def _export_to_parquet(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato Parquet."""
        final_path = output_path.with_suffix(".parquet")
        df = pd.read_sql(query, self.engine)
        df.to_parquet(final_path, index=False)
        return str(final_path)

    def _export_to_html(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato HTML."""
        final_path = output_path.with_suffix(".html")
        df = pd.read_sql(query, self.engine)
        df.to_html(final_path, index=False)
        return str(final_path)

    def _export_to_feather(
        self, query: str, output_path: Path, table_name: str, chunk_size: int
    ) -> str:
        """Exporta datos a formato Feather."""
        final_path = output_path.with_suffix(".feather")
        df = pd.read_sql(query, self.engine)
        df.to_feather(final_path)
        return str(final_path)

    def insert(self, table_name: str, data: Dict[str, any]) -> None:
        """Inserta un registro en la tabla."""
        try:
            cols = ", ".join(data.keys())
            placeholders = ", ".join([f":{k}" for k in data.keys()])
            query = text(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})")
            with self.engine.begin() as conn:
                conn.execute(query, data)
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "insert_error",
                    f"{t('insert_failed')} {table_name}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('insert_failed')} {table_name}: {str(e)}")

    def select(
        self, table_name: str, where: Optional[Dict[str, any]] = None
    ) -> pd.DataFrame:
        """Selecciona registros de una tabla."""
        try:
            query = f"SELECT * FROM {table_name}"
            params = {}
            if where:
                conditions = [f"{col} = :{col}" for col in where.keys()]
                query += " WHERE " + " AND ".join(conditions)
                params = where
            return pd.read_sql(text(query), self.engine, params=params)
        except Exception as e:
            raise SQLAlchemyError(f"{t('select_failed')} {table_name}: {str(e)}")

    def update(
        self, table_name: str, data: Dict[str, any], where: Dict[str, any]
    ) -> None:
        """Actualiza registros en una tabla."""
        try:
            set_clause = ", ".join([f"{col} = :{col}" for col in data.keys()])
            where_clause = " AND ".join([f"{col} = :w_{col}" for col in where.keys()])
            params = {**data, **{f"w_{k}": v for k, v in where.items()}}

            dialect_name = self.engine.dialect.name
            if dialect_name == "postgresql":
                for key, value in where.items():
                    if isinstance(value, int):
                        params[f"w_{key}"] = str(value)

            query = text(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}")
            with self.engine.begin() as conn:
                conn.execute(query, params)
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "update_error",
                    f"{t('update_failed')} {table_name}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('update_failed')} {table_name}: {str(e)}")

    def delete(self, table_name: str, where: Dict[str, any]) -> None:
        """Elimina registros de una tabla."""
        try:
            where_clause = " AND ".join([f"{col} = :{col}" for col in where.keys()])
            query = text(f"DELETE FROM {table_name} WHERE {where_clause}")


            params = where.copy()
            dialect_name = self.engine.dialect.name
            if dialect_name == "postgresql":
                for key, value in where.items():
                    if isinstance(value, int):
                        params[key] = str(value)

            with self.engine.begin() as conn:
                conn.execute(query, params)
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "delete_error",
                    f"{t('delete_failed')} {table_name}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('delete_failed')} {table_name}: {str(e)}")

    def exportData(
        self,
        table_names: Union[str, List[str]] = "all",
        output_path: str = None,
        format_type: str = "csv",
        where_condition: Optional[Union[str, Dict[str, str]]] = None,
        columns: Optional[Union[List[str], Dict[str, List[str]]]] = None,
        chunk_size: int = 10000,
        separate_files: bool = True,
    ) -> Union[str, List[str]]:
        """
        Exporta datos de una o más tablas a diferentes formatos.

        Args:
            table_names: Nombre de tabla(s) a exportar o 'all' para toda la BD
            output_path: Ruta donde guardar el archivo(s)
            format_type: Formato de exportación (csv, xml, json, sql, excel, parquet)
            where_condition: Condición WHERE para filtrar datos (str o dict con {tabla: condición})
            columns: Columnas específicas a exportar (List o dict con {tabla: [columnas]})
            chunk_size: Tamaño de chunks para datasets grandes
            separate_files: Si True, crea archivos separados por tabla

        Returns:
            Ruta(s) del archivo(s) exportado(s)

        Raises:
            ValueError: Si el formato no es soportado
            SQLAlchemyError: Si hay error en la consulta
        """
        try:

            if table_names == "all":

                table_names = self._get_all_tables()
            elif isinstance(table_names, str):
                table_names = [table_names]

            if not table_names:
                raise ValueError("no_tables_to_export")


            output_path = Path(output_path) if output_path else Path.cwd() / "export"
            output_path.mkdir(parents=True, exist_ok=True)


            results = []

            for table_name in table_names:

                table_cols = self._get_columns_for_table(columns, table_name)
                table_where = self._get_where_for_table(where_condition, table_name)

                cols = "*" if not table_cols else ", ".join(table_cols)
                query = f"SELECT {cols} FROM {table_name}"
                if table_where:
                    query += f" WHERE {table_where}"


                if separate_files or len(table_names) > 1:
                    table_output_path = output_path / f"{table_name}.{format_type}"
                else:
                    table_output_path = output_path.with_suffix(f".{format_type}")


                export_function = Switch(format_type.lower())(
                    {
                        "cases": [
                            {"case": "csv", "then": lambda: self._export_to_csv},
                            {"case": "xml", "then": lambda: self._export_to_xml},
                            {"case": "json", "then": lambda: self._export_to_json},
                            {"case": "sql", "then": lambda: self._export_to_sql},
                            {"case": "excel", "then": lambda: self._export_to_excel},
                            {
                                "case": "parquet",
                                "then": lambda: self._export_to_parquet,
                            },
                            {"case": "html", "then": lambda: self._export_to_html},
                            {
                                "case": "feather",
                                "then": lambda: self._export_to_feather,
                            },
                        ],
                        "default": lambda: self._export_to_csv,
                    }
                )

                result_path = export_function(
                    query, table_output_path, table_name, chunk_size
                )
                results.append(result_path)

            return results if len(results) > 1 else results[0]

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error", "export_error", f"{t('export_failed')}: {str(e)}"
                )
            raise SQLAlchemyError(f"{t('export_failed')}: {str(e)}")

    def table_exists(self, table_name: str) -> bool:
        """Verifica si una tabla existe en la base de datos (compatible con MySQL, PostgreSQL y MSSQL)."""
        try:
            db_type = self.config.get("db_type", "").lower()
            if db_type == "postgresql":
                query = text(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = :table_name
                    )
                """
                )
            elif db_type == "mssql":
                query = text(
                    """
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_type = 'BASE TABLE' AND table_name = :table_name
                """
                )
            else:  # MySQL y otros
                query = text(
                    """
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() AND table_name = :table_name
                """
                )
            result = self.session.execute(query, {"table_name": table_name}).scalar()
            return bool(result)
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "table_check_error",
                    f"{t('table_check_failed')}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('table_check_failed')}: {str(e)}")

    def _parse_column_type(self, col_type: str):
        """Parsea el tipo de columna y devuelve el tipo SQLAlchemy apropiado con longitud para VARCHAR en MySQL"""

        if hasattr(col_type, "__class__") and hasattr(col_type, "compile"):
            return col_type


        col_type = col_type.lower().strip()


        if "(" in col_type and ")" in col_type:
            type_name = col_type.split("(")[0]
            params = col_type.split("(")[1].split(")")[0].split(",")

            if type_name == "varchar":
                length = int(params[0])
                return sa.String(length=length)

        else:

            type_mapping = {
                "varchar": sa.String(255),  # Longitud por defecto para MySQL
                "string": sa.String(255),
                "text": sa.Text(),
                "integer": sa.Integer(),
                "int": sa.Integer(),
                "bigint": sa.BigInteger(),
                "smallint": sa.SmallInteger(),
                "float": sa.Float(),
                "double": sa.Float(),
                "numeric": sa.Numeric(),
                "boolean": sa.Boolean(),
                "date": sa.Date(),
                "datetime": sa.DateTime(),
                "time": sa.Time(),
                "binary": sa.LargeBinary(),
            }

            if col_type in type_mapping:
                return type_mapping[col_type]


        return sa.String(255)

    def addTable(
        self,
        table_name: str,
        columns: Dict[str, str],
        constraints: Optional[Dict[str, str]] = None,
        if_not_exists: bool = True,
    ) -> None:
        """Agrega una nueva tabla a la base de datos."""
        try:
            if if_not_exists and self.table_exists(table_name):
                if self.config["db_debug"]:
                    show_alert_popup(
                        "warning",
                        "table_exists_warning",
                        f"{t('table_exists')} {table_name}",
                    )
                return

            table_columns = []
            for col_name, col_type in columns.items():
                col_type_obj = self._parse_column_type(col_type)
                table_columns.append(Column(col_name, col_type_obj))

            if constraints:
                for ctype, col in constraints.items():
                    if ctype.upper() == "PRIMARY KEY":
                        for col_def in table_columns:
                            if col_def.name == col:
                                col_def.primary_key = True

            Table(table_name, self.metadata, *table_columns)
            self.metadata.create_all(self.engine)

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "create_table_error",
                    f"{t('create_table_failed')} {table_name}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('create_table_failed')} {table_name}: {str(e)}")

    def mergeTable(
        self, *table_names: str, on: Optional[List[str]] = None, how: str = "inner"
    ) -> pd.DataFrame:
        """
        Fusiona múltiples tablas usando lógica SQL.

        Args:
            table_names: Nombres de las tablas a fusionar
            on: Columnas para el merge
            how: Tipo de merge (inner, outer, left, right)

        Returns:
            DataFrame con el resultado del merge
        """
        try:
            if len(table_names) < 2:
                raise ValueError("at_least_two_tables_required")


            query = f"SELECT * FROM {table_names[0]}"
            result_df = pd.read_sql(query, self.engine)


            for i in range(1, len(table_names)):
                next_df = pd.read_sql(f"SELECT * FROM {table_names[i]}", self.engine)

                merge_on = (
                    on
                    if on
                    else result_df.columns.intersection(next_df.columns).tolist()
                )

                if not merge_on:
                    raise ValueError(
                        f"{t('no_common_columns')} {table_names[0]} {t('and')} {table_names[i]}"
                    )

                result_df = result_df.merge(next_df, on=merge_on, how=how)

            return result_df

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error", "merge_error", f"{t('merge_failed')}: {str(e)}"
                )
            raise SQLAlchemyError(f"{t('merge_failed')}: {str(e)}")

    def join(
        self,
        join_type: str,
        table1: str,
        table2: str,
        on: Optional[List[str]] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Realiza JOIN entre tablas usando lógica SQL.

        Args:
            join_type: Tipo de join (inner, left, right, outer, cross)
            table1: Nombre de la primera tabla
            table2: Nombre de la segunda tabla
            on: Columnas para el join
            **kwargs: Condiciones adicionales WHERE, etc.

        Returns:
            DataFrame con el resultado del join
        """
        try:
            join_query = Switch(join_type.lower())(
                {
                    "cases": [
                        {"case": "inner", "then": f"INNER JOIN {table2}"},
                        {"case": "left", "then": f"LEFT JOIN {table2}"},
                        {"case": "right", "then": f"RIGHT JOIN {table2}"},
                        {"case": "outer", "then": f"FULL OUTER JOIN {table2}"},
                        {"case": "cross", "then": f"CROSS JOIN {table2}"},
                    ],
                    "default": f"INNER JOIN {table2}",
                }
            )


            on_condition = ""
            if on and join_type.lower() != "cross":
                on_clauses = []
                for col in on:
                    if "." in col:
                        on_clauses.append(f"{table1}.{col} = {table2}.{col}")
                    else:
                        on_clauses.append(f"{table1}.{col} = {table2}.{col}")
                on_condition = " ON " + " AND ".join(on_clauses)


            query = f"""
            SELECT * FROM {table1}
            {join_query}
            {on_condition}
            """


            where_conditions = kwargs.get("where", [])
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            return pd.read_sql(query, self.engine)

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup("error", "join_error", f"{t('join_failed')}: {str(e)}")
            raise SQLAlchemyError(f"{t('join_failed')}: {str(e)}")

    def drop(
    self, 
    table_name: str, 
    where: Optional[Dict[str, any]] = None,
    cascade: bool = False
) -> None:
        """
        Elimina registros de una tabla, con opción de eliminación en cascada.

        Args:
            table_name: Nombre de la tabla
            where: Condiciones para la eliminación (si es None, elimina todos los registros)
            cascade: Si es True, realiza eliminación en cascada de registros relacionados
        """
        try:
            dialect_name = self.engine.dialect.name
        
            if cascade and where:

                if dialect_name == 'postgresql':
                    query = text("""
                        SELECT
                            tc.table_name as table_name,
                            kcu.column_name as column_name,
                            ccu.table_name AS referenced_table_name,
                            ccu.column_name AS referenced_column_name
                        FROM 
                            information_schema.table_constraints AS tc 
                            JOIN information_schema.key_column_usage AS kcu
                              ON tc.constraint_name = kcu.constraint_name
                              AND tc.table_schema = kcu.table_schema
                            JOIN information_schema.constraint_column_usage AS ccu
                              ON ccu.constraint_name = tc.constraint_name
                              AND ccu.table_schema = tc.table_schema
                        WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name = :table_name
                    """)
                elif dialect_name == 'mssql':
                    query = text("""
                        SELECT 
                            OBJECT_NAME(fkc.parent_object_id) AS table_name,
                            COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS column_name,
                            OBJECT_NAME(fkc.referenced_object_id) AS referenced_table_name,
                            COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS referenced_column_name
                        FROM 
                            sys.foreign_key_columns AS fkc
                            INNER JOIN sys.foreign_keys AS fk ON fkc.constraint_object_id = fk.object_id
                        WHERE 
                            OBJECT_NAME(fk.referenced_object_id) = :table_name
                    """)
                else:  # MySQL y otros
                    query = text("""
                        SELECT 
                            TABLE_NAME, 
                            COLUMN_NAME, 
                            REFERENCED_TABLE_NAME, 
                            REFERENCED_COLUMN_NAME
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                        WHERE REFERENCED_TABLE_NAME = :table_name
                    """)
                

                dependencies = pd.read_sql(query, self.engine, params={"table_name": table_name})


                where_conditions = [f"{col} = :{col}" for col in where.keys()]
                where_clause = " AND ".join(where_conditions)


                for _, dep in dependencies.iterrows():
                    delete_query = text(f"""
                        DELETE FROM {dep['table_name']} 
                        WHERE {dep['column_name']} IN (
                            SELECT {dep['referenced_column_name']} 
                            FROM {table_name} 
                            WHERE {where_clause}
                        )
                    """)
                
                    with self.engine.begin() as conn:
                        conn.execute(delete_query, where)


            if where:
                where_conditions = [f"{col} = :{col}" for col in where.keys()]
                where_clause = " AND ".join(where_conditions)
                query = text(f"DELETE FROM {table_name} WHERE {where_clause}")
                params = where.copy()
            else:
                query = text(f"DELETE FROM {table_name}")
                params = {}
        

            if dialect_name == 'postgresql':
                for key, value in params.items():
                    if isinstance(value, int):
                        params[key] = str(value)
            elif dialect_name == 'mssql':

                pass
        
            with self.engine.begin() as conn:
                conn.execute(query, params)

        except Exception as e:
            if self.config.get("db_debug", False):
                show_alert_popup(
                    "error",
                    "delete_error",
                    f"{t('delete_failed')}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('delete_failed')}: {str(e)}")

    def recursiveQuery(
        self,
        table_name: str,
        start_with: str,
        connect_by: str,
        level_col: str = "level",
    ) -> pd.DataFrame:
        """
        Ejecuta una consulta recursiva (COMMON TABLE EXPRESSION).

        Args:
            table_name: Nombre de la tabla
            start_with: Condición inicial
            connect_by: Condición de conexión
            level_col: Nombre de la columna de nivel

        Returns:
            DataFrame con el resultado recursivo
        """
        try:
            db_type = self.config.get("db_type", "").lower()
            
            if db_type == "postgresql":
                query = f"""
                WITH RECURSIVE cte AS (
                    SELECT *, 1 as {level_col}
                    FROM {table_name}
                    WHERE {start_with}
                    
                    UNION ALL
                    
                    SELECT t.*, c.{level_col} + 1
                    FROM {table_name} t
                    INNER JOIN cte c ON {connect_by}
                )
                SELECT * FROM cte
                """
            elif db_type == "mssql":
                query = f"""
                WITH cte AS (
                    SELECT *, 1 as {level_col}
                    FROM {table_name}
                    WHERE {start_with}
                    
                    UNION ALL
                    
                    SELECT t.*, c.{level_col} + 1
                    FROM {table_name} t
                    INNER JOIN cte c ON {connect_by}
                )
                SELECT * FROM cte
                """
            else:

                if self.db_version and int(self.db_version.split('.')[0]) >= 8:
                    query = f"""
                    WITH RECURSIVE cte AS (
                        SELECT *, 1 as {level_col}
                        FROM {table_name}
                        WHERE {start_with}
                        
                        UNION ALL
                        
                        SELECT t.*, c.{level_col} + 1
                        FROM {table_name} t
                        INNER JOIN cte c ON {connect_by}
                    )
                    SELECT * FROM cte
                    """
                else:
                    raise SQLAlchemyError("recursive_cte_not_supported")

            return pd.read_sql(query, self.engine)

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "recursive_query_error",
                    f"{t('recursive_query_failed')}: {str(e)}",
                )
            raise SQLAlchemyError(f"{t('recursive_query_failed')}: {str(e)}")

    def windowFunction(
        self,
        table_name: str,
        function: str,
        partition_by: List[str],
        order_by: List[str],
    ) -> pd.DataFrame:
        """
        Aplica funciones de ventana a una tabla.

        Args:
            table_name: Nombre de la tabla
            function: Función de ventana (ROW_NUMBER, RANK, DENSE_RANK, etc.)
            partition_by: Columnas para PARTITION BY
            order_by: Columnas para ORDER BY

        Returns:
            DataFrame con los resultados
        """
        try:

            if (
                self.engine.dialect.name == "mysql"
                and self.db_version
                and int(self.db_version.split(".")[0]) < 8
            ):

                if self.config["db_debug"]:
                    show_alert_popup(
                        "warning",
                        "window_function_not_available",
                        f"{t('window_function_requires_mysql8')} "
                        f"{t('current_version')} {self.db_version}. "
                        f"{t('window_function_omitted')}",
                    )


                query = f"SELECT * FROM {table_name}"
                return pd.read_sql(query, self.engine)

            partition_clause = (
                f"PARTITION BY {', '.join(partition_by)}" if partition_by else ""
            )
            order_clause = f"ORDER BY {', '.join(order_by)}" if order_by else ""

            query = f"""
            SELECT *, 
                   {function}() OVER ({partition_clause} {order_clause}) as window_result
            FROM {table_name}
        """

            return pd.read_sql(query, self.engine)

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "warning",
                    "window_function_error",
                    f"{t('window_function_failed')}: {str(e)}. "
                    f"{t('window_function_omitted')}",
                )


            query = f"SELECT * FROM {table_name}"
            return pd.read_sql(query, self.engine)

    def executeRawSQL(self, sql: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Ejecuta SQL raw directamente.

        Args:
            sql: Consulta SQL
            params: Parámetros para la consulta

        Returns:
            DataFrame con los resultados
        """
        try:
            query = text(sql)


            new_params = params.copy() if params else {}
            dialect_name = self.engine.dialect.name
            if dialect_name == "postgresql" and params:
                for key, value in params.items():
                    if isinstance(value, int):
                        new_params[key] = str(value)

            return pd.read_sql(query, self.engine, params=new_params)
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error", "sql_execution_error", f"{t('sql_execution_failed')}: {str(e)}"
                )
            raise SQLAlchemyError(f"{t('sql_execution_failed')}: {str(e)}")

    def close(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()

        self.config = None
        self.engine = None
        self.metadata = None
        self.session = None

    def show(
        self,
        table_names: Union[str, List[str]] = "all",
        where_condition: Optional[Union[str, Dict[str, str]]] = None,
        columns: Optional[Union[List[str], Dict[str, List[str]]]] = None,
        limit: int = 1000,
    ) -> None:
        """
        Muestra las tablas y datos de la base de datos en una interfaz gráfica.

        Args:
            table_names: Nombre de tabla(s) a mostrar o 'all' para toda la BD
            where_condition: Condición WHERE para filtrar datos
            columns: Columnas específicas a mostrar
            limit: Límite de registros a mostrar por tabla
        """
        try:

            if table_names == "all":
                table_names = self._get_all_tables()
            elif isinstance(table_names, str):
                table_names = [table_names]

            if not table_names:
                show_gui_popup("Database Info", t("no_tables_in_database"))
                return


            content = f"{t('database')}: {self.config['db_name']}\n"
            content += f"{t('tables_found')}: {len(table_names)}\n\n"


            table_data = {}
            for table_name in table_names:
                table_cols = self._get_columns_for_table(columns, table_name)
                table_where = self._get_where_for_table(where_condition, table_name)

                cols = "*" if not table_cols else ", ".join(table_cols)
                query = f"SELECT {cols} FROM {table_name}"
                if table_where:
                    query += f" WHERE {table_where}"
                query += f" LIMIT {limit}"

                df = pd.read_sql(query, self.engine)
                table_data[table_name] = df


                content += f"{t('table')}: {table_name}\n"
                content += f"{t('records')}: {len(df)}\n"
                content += f"{t('columns')}: {', '.join(df.columns)}\n\n"


            def generate_preview():
                fig, axes = plt.subplots(1, len(table_names), figsize=(15, 8))
                if len(table_names) == 1:
                    axes = [axes]

                for i, (table_name, df) in enumerate(table_data.items()):
                    if i >= len(axes):
                        break


                    ax = axes[i]
                    ax.axis("off")
                    ax.set_title(
                        f"{t('table')}: {table_name}\n{t('records')}: {len(df)}", fontsize=12
                    )

                    if not df.empty:

                        table_data_preview = [df.columns.tolist()] + df.head(
                            5
                        ).values.tolist()
                        table = ax.table(
                            cellText=table_data_preview, cellLoc="left", loc="center"
                        )
                        table.auto_set_font_size(False)
                        table.set_fontsize(8)
                        table.scale(1, 1.5)

                plt.tight_layout()
                return fig


            def export_data(format_type):
                try:
                    output_path = filedialog.asksaveasfilename(
                        defaultextension=f".{format_type}",
                        filetypes=[
                            (f"{format_type.upper()} files", f"*.{format_type}")
                        ],
                    )
                    if output_path:
                        self.exportData(
                            table_names=table_names,
                            output_path=output_path,
                            format_type=format_type,
                            where_condition=where_condition,
                            columns=columns,
                            separate_files=False,
                        )
                        if self.config["db_debug"]:
                            show_gui_popup(
                                "success",
                                f"{t('data_exported_successfully')} {output_path}",
                            )
                except Exception as e:
                    if self.config["db_debug"]:
                        show_gui_popup("error", f"{t('export_error')}: {str(e)}")


            show_gui_popup(
                title="Database Explorer",
                content=content,
                fig=generate_preview(),
                export_callback=export_data,
                table_data=table_data,
            )

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error",
                    "display_error",
                    f"{t('display_data_failed')}: {str(e)}",
                )

    def reset(self) -> None:
        """
        Elimina todas las tablas de la base de datos en orden normal.
        """
        try:
            inspector = sa.inspect(self.engine)
            tables = inspector.get_table_names()

            with self.engine.begin() as conn:
                for table in tables:
                    try:
                        conn.execute(text(f'DROP TABLE IF EXISTS "{table}"'))
                    except Exception as e:
                        if self.config["db_debug"]:
                            show_alert_popup(
                                "error", f"⚠️ {t('drop_table_failed')} {table}", f"{e}"
                            )

            if self.config["db_debug"]:
                show_gui_popup(
                    "success",
                    f"{t('reset_completed')}: {t('all_tables_dropped')}",
                )

        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup("error", "reset_error", f"{t('reset_failed')}: {str(e)}")
            raise SQLAlchemyError(f"{t('reset_failed')}: {str(e)}")

    def force_reset(self) -> None:
        """
        Elimina todas las tablas de la base de datos ignorando dependencias.
        - En PostgreSQL usa CASCADE
        - En MySQL/MariaDB ignora CASCADE (no existe)
        """
        try:
            inspector = sa.inspect(self.engine)
            tables = inspector.get_table_names()
            dialect = self.engine.dialect.name  # mysql, postgresql, mssql, etc.

            with self.engine.begin() as conn:
                for table in tables:
                    try:
                        if dialect == "postgresql":
                            conn.execute(
                                text(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                            )
                        elif dialect in ("mysql", "mariadb"):
                            conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
                        elif dialect == "mssql":
                            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                        else:
                            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    except Exception as e:
                        if self.config["db_debug"]:
                            show_alert_popup(
                                "error", f"⚠️ {t('drop_table_failed')} {table}", f"{e}"
                            )
            if self.config["db_debug"]:
                show_gui_popup(
                    "success", f"{t('force_reset_completed')}: {t('all_tables_dropped')}"
                )
        except Exception as e:
            if self.config["db_debug"]:
                show_alert_popup(
                    "error", "force_reset_error", f"{t('force_reset_failed')}: {str(e)}"
                )
            raise SQLAlchemyError(f"{t('force_reset_failed')}: {str(e)}")


def manageDB(
    db_name: str,
    db_host: str,
    db_user: str,
    db_pass: str,
    db_port: str,
    db_type: str,
    create_if_not_exists: bool = False,
    db_debug: bool = False,
) -> DataBase:

    def get_available_driver():
        """Busca controladores ODBC compatibles en orden de preferencia"""
        drivers_to_try = [
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 13 for SQL Server',
            'ODBC Driver 11 for SQL Server'
        ]
    
        installed_drivers = pyodbc.drivers()
        for driver in drivers_to_try:
            if driver in installed_drivers:
                return driver
        return None

    


    if db_type.lower() == "postgresql":
        engine = create_engine(
            f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/postgres"
        )
    elif db_type.lower() == "mysql":
        engine = create_engine(
            f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/"
        )
    elif db_type.lower() == "mssql":
        driver = get_available_driver()
        if driver is None: 
            if show_yesno_popup(
                "no_mssql_driver_title",
                "no_mssql_driver_msg"
            ):

                webbrowser.open("https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
                show_alert_popup(
                    "warning",
                    t("need_install"),
                    t("install_req_msg")
                )
            else:
                show_alert_popup(
                    "warning",
                    t("c_error"),
                    t("odbc_error_msg")
                )
            sys.exit(1)
            raise ValueError(f"{t('no_mssql_drivers_installed')}")
        else:
            engine = create_engine(
                f"mssql+pyodbc://{db_user}:{db_pass}@{db_host}:{db_port}/master?driver={driver}"
            )
    else:
        raise ValueError(f"{t('database_type_not_supported')}: {db_type}")

    if create_if_not_exists:
        if db_type.lower() == "postgresql":

            with engine.connect().execution_options(
                isolation_level="AUTOCOMMIT"
            ) as conn:
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                    {"dbname": db_name},
                )
                if not result.scalar():
                    conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        elif db_type.lower() == "mysql":
            with engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        elif db_type.lower() == "mssql":
            with engine.connect() as conn:
                conn.execute(text(f"IF NOT EXISTS(SELECT * FROM sys.databases WHERE name = '{db_name}') CREATE DATABASE {db_name}"))


    config = {
        "db_name": db_name,
        "db_host": db_host,
        "db_user": db_user,
        "db_pass": db_pass,
        "db_port": db_port,
        "db_type": db_type,
        "db_debug": db_debug,
    }

    return DataBase(config)
