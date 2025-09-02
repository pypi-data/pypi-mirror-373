import ast, sys, os
from pathlib import Path
from typing import Union, Dict, Set, List, Tuple
from .shared import t, show_gui_popup, IN_JUPYTER, display, Markdown
from .pyswitch import switch


class PythonFileChecker:
    def __init__(self):
        self.errors: List[Dict[str, str]] = []
        self.imported_names: Set[str] = set()
        self.defined_names: Set[str] = set()
        self.import_lines: Dict[str, int] = {}
        self.syntax_errors: List[Dict[str, str]] = []
        self.exception_handlers: Set[str] = set()
        self.python_exceptions = [
            "BaseException", "SystemExit", "KeyboardInterrupt", "GeneratorExit", "Exception",
            "ArithmeticError", "FloatingPointError", "OverflowError", "ZeroDivisionError",
            "AssertionError", "AttributeError", "BufferError", "EOFError", "ImportError",
            "ModuleNotFoundError", "LookupError", "IndexError", "KeyError", "MemoryError",
            "NameError", "UnboundLocalError", "OSError", "BlockingIOError", "ChildProcessError",
            "ConnectionError", "BrokenPipeError", "ConnectionAbortedError", "ConnectionRefusedError",
            "ConnectionResetError", "FileExistsError", "FileNotFoundError", "InterruptedError",
            "IsADirectoryError", "NotADirectoryError", "PermissionError", "ProcessLookupError",
            "TimeoutError", "ReferenceError", "RuntimeError", "NotImplementedError", "RecursionError",
            "StopAsyncIteration", "StopIteration", "SyntaxError", "IndentationError", "TabError",
            "SystemError", "TypeError", "ValueError", "UnicodeError", "UnicodeDecodeError",
            "UnicodeEncodeError", "UnicodeTranslateError", "Warning", "DeprecationWarning",
            "PendingDeprecationWarning", "RuntimeWarning", "SyntaxWarning", "UserWarning",
            "FutureWarning", "ImportWarning", "UnicodeWarning", "BytesWarning", "ResourceWarning"
        ]

    def check_file(self, file_path: Union[str, Path]) -> bool:
        """Check a Python file for all possible errors without stopping"""
        self._reset_state()
        
        if not os.path.exists(file_path):
            self._add_error(0, t("file_not_found").format(file_path=file_path), "FileNotFound")
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
                source_lines = source_code.splitlines()
        except UnicodeDecodeError:
            self._add_error(0, t("encoding_error"), "EncodingError")
            return False
        except Exception as e:
            self._add_error(0, t("file_read_error").format(error=str(e)), "IOError")
            return False


        tree = self._parse_code(source_code, source_lines)
        
        if tree is not None:
            self._analyze_tree(tree, source_lines)
        else:
            self._incremental_analysis(source_code, source_lines)


        self.errors.extend(self.syntax_errors)
        
        return len(self.errors) == 0

    def _reset_state(self) -> None:
        """Reset all state variables"""
        self.errors.clear()
        self.imported_names.clear()
        self.defined_names.clear()
        self.import_lines.clear()
        self.syntax_errors.clear()
        self.exception_handlers.clear()

    def _parse_code(self, source_code: str, source_lines: List[str]) -> ast.AST:
        """Parse the source code and handle syntax errors"""
        try:
            return ast.parse(source_code)
        except SyntaxError as e:
            self._add_syntax_error(e, source_lines)
            try:
                return ast.parse(source_code, mode="exec")
            except SyntaxError as e2:
                self._add_syntax_error(e2, source_lines)
            except Exception:
                pass
        return None

    def _analyze_tree(self, tree: ast.AST, source_lines: List[str]) -> None:
        """Analyze the AST tree for various issues"""
        try:

            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    setattr(child, "parent", node)

            self._collect_imports_and_definitions(tree)
            self._check_exception_handling(tree, source_lines)
            self._check_undefined_names(tree, source_lines)
            self._check_other_issues(tree, source_lines)

        except Exception as e:
            self._add_error(0, t("analysis_error").format(msg=str(e)), "AnalysisError")

    def _add_syntax_error(self, error: SyntaxError, source_lines: List[str]) -> None:
        """Helper to add syntax errors with proper formatting"""
        line_content = ""
        if error.lineno and error.lineno <= len(source_lines):
            line_content = source_lines[error.lineno - 1].strip()
            
        self.syntax_errors.append({
            "line": error.lineno or 0,
            "message": t("syntax_error").format(msg=error.msg),
            "type": "SyntaxError",
            "context": line_content,
        })

    def _incremental_analysis(self, source_code: str, source_lines: List[str]) -> None:
        """Try to analyze the file incrementally when full parsing fails"""

        for i, line in enumerate(source_lines, 1):
            line = line.strip()
            if not line or line.startswith(('#', '"""', "'''")):
                continue
                
            try:
                ast.parse(line)
            except SyntaxError as e:
                self._add_syntax_error(e, source_lines)
            except Exception:
                pass


        self._analyze_code_blocks(source_code, source_lines)

    def _analyze_code_blocks(self, source_code: str, source_lines: List[str]) -> None:
        """Try to analyze blocks of code when full parsing fails"""
        blocks = self._split_into_blocks(source_lines)
        
        for block_content, start_line in blocks:
            try:
                tree = ast.parse(block_content)

                for node in ast.walk(tree):
                    for child in ast.iter_child_nodes(node):
                        setattr(child, "parent", node)

                self._collect_imports_and_definitions(tree)
                self._check_exception_handling_with_offset(tree, source_lines, start_line - 1)
                self._check_undefined_names_with_offset(tree, source_lines, start_line - 1)
                self._check_other_issues_with_offset(tree, source_lines, start_line - 1)

            except SyntaxError as e:
                e.lineno = (e.lineno or 0) + start_line - 1
                self._add_syntax_error(e, source_lines)
            except Exception:
                pass

    def _split_into_blocks(self, source_lines: List[str]) -> List[Tuple[str, int]]:
        """Split source code into logical blocks"""
        blocks = []
        current_block = []
        
        for i, line in enumerate(source_lines):
            if line.strip() == "" and current_block:
                blocks.append(("\n".join(current_block), i - len(current_block) + 1))
                current_block = []
            elif line.strip() != "":
                current_block.append(line)
                
        if current_block:
            blocks.append(("\n".join(current_block), len(source_lines) - len(current_block) + 1))
            
        return blocks

    def _check_exception_handling(self, tree: ast.AST, source_lines: List[str]) -> None:
        """Check for proper exception handling"""
        for node in ast.walk(tree):
            node_type = type(node).__name__
            switch(node_type, {
                "Try": self._analyze_try_block(node, source_lines),
                "Raise": self._analyze_raise_statement(node, source_lines),
                "default": None
            })

    def _check_exception_handling_with_offset(self, tree: ast.AST, source_lines: List[str], line_offset: int) -> None:
        """Check exception handling with line number adjustment"""
        for node in ast.walk(tree):
            node_type = type(node).__name__
            switch(node_type, {
                "Try": self._analyze_try_block_with_offset(node, source_lines, line_offset),
                "Raise": self._analyze_raise_statement_with_offset(node, source_lines, line_offset),
                "default": None
            })

    def _analyze_try_block(self, node: ast.Try, source_lines: List[str]) -> None:
        """Analyze a try block for exception handling issues"""
        for handler in node.handlers:
            if handler.type:

                handler_type = type(handler.type).__name__
                switch(handler_type, {
                    "Name": self.exception_handlers.add(handler.type.id),
                    "Tuple": [self.exception_handlers.add(elt.id) for elt in handler.type.elts 
                                     if isinstance(elt, ast.Name)],
                    "default": None
                })
            

            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                line_content = source_lines[handler.lineno - 1].strip() if handler.lineno <= len(source_lines) else ""
                self._add_error(
                    handler.lineno,
                    t("empty_except_handler"),
                    "ExceptionWarning",
                    line_content,
                )

    def _analyze_try_block_with_offset(self, node: ast.Try, source_lines: List[str], line_offset: int) -> None:
        """Analyze try block with line offset"""
        for handler in node.handlers:
            if handler.type:
                handler_type = type(handler.type).__name__
                switch(handler_type, {
                    "Name": self.exception_handlers.add(handler.type.id),
                    "Tuple": [self.exception_handlers.add(elt.id) for elt in handler.type.elts 
                                     if isinstance(elt, ast.Name)],
                    "default": None
                })
            
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                adjusted_line = handler.lineno + line_offset
                line_content = source_lines[adjusted_line - 1].strip() if adjusted_line <= len(source_lines) else ""
                self._add_error(
                    adjusted_line,
                    t("empty_except_handler"),
                    "ExceptionWarning",
                    line_content,
                )

    def _analyze_raise_statement(self, node: ast.Raise, source_lines: List[str]) -> None:
        """Analyze raise statements for potential issues"""
        if node.exc is None:

            line_content = source_lines[node.lineno - 1].strip() if node.lineno <= len(source_lines) else ""
            self._add_error(
                node.lineno,
                t("bare_raise_outside_handler"),
                "ExceptionWarning",
                line_content,
            )
        elif isinstance(node.exc, ast.Call):

            if isinstance(node.exc.func, ast.Name):
                exception_name = node.exc.func.id
                if exception_name not in self.python_exceptions:
                    line_content = source_lines[node.lineno - 1].strip() if node.lineno <= len(source_lines) else ""
                    self._add_error(
                        node.lineno,
                        t("unknown_exception_type").format(name=exception_name),
                        "ExceptionWarning",
                        line_content,
                    )

    def _analyze_raise_statement_with_offset(self, node: ast.Raise, source_lines: List[str], line_offset: int) -> None:
        """Analyze raise statement with line offset"""
        if node.exc is None:
            adjusted_line = node.lineno + line_offset
            line_content = source_lines[adjusted_line - 1].strip() if adjusted_line <= len(source_lines) else ""
            self._add_error(
                adjusted_line,
                t("bare_raise_outside_handler"),
                "ExceptionWarning",
                line_content,
            )
        elif isinstance(node.exc, ast.Call):
            if isinstance(node.exc.func, ast.Name):
                exception_name = node.exc.func.id
                if exception_name not in self.python_exceptions:
                    adjusted_line = node.lineno + line_offset
                    line_content = source_lines[adjusted_line - 1].strip() if adjusted_line <= len(source_lines) else ""
                    self._add_error(
                        adjusted_line,
                        t("unknown_exception_type").format(name=exception_name),
                        "ExceptionWarning",
                        line_content,
                    )

    def _check_undefined_names_with_offset(self, tree: ast.AST, source_lines: List[str], line_offset: int) -> None:
        """Check for undefined names with line number adjustment"""
        defined = self.defined_names.union(self.imported_names)
        builtins = set(dir(__builtins__)).union({
            'self', 'cls', '_', 'print', 'open', 
            'ImportError', 'globals', 'Exception'
        })

        for node in ast.walk(tree):
            try:
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    name = node.id
                    if (name not in defined and 
                        name not in builtins and 
                        not name.startswith('_')):
                        
                        is_attribute = False
                        if hasattr(node, "parent"):
                            parent = node.parent
                            if (isinstance(parent, ast.Attribute) and 
                                parent.value == node):
                                is_attribute = True

                        if not is_attribute:
                            adjusted_line = node.lineno + line_offset
                            line_content = (
                                source_lines[adjusted_line - 1].strip()
                                if adjusted_line <= len(source_lines)
                                else ""
                            )
                            self._add_error(
                                adjusted_line,
                                t("undefined_name").format(name=name),
                                "NameError",
                                line_content,
                            )
            except Exception:
                continue

    def _check_other_issues_with_offset(self, tree: ast.AST, source_lines: List[str], line_offset: int) -> None:
        """Check for other potential issues with line number adjustment"""
        imported_names = set(self.import_lines.keys())
        all_used_names = set()
        assigned_but_unused = {}

        bad_comparisons = {
            "Eq": {  # ==
                "True": t("redundant_true"),
                "False": t("redundant_false"),
                "None": t("none_comparison"),
            },
            "NotEq": {  # !=
                "True": t("not_true_recommendation"),
                "False": t("not_false_recommendation"),
            },
        }

        for node in ast.walk(tree):
            try:
                node_type = type(node).__name__
                switch(node_type, {
                    "Name": self._handle_name_node(node, imported_names, all_used_names) if isinstance(node.ctx, ast.Load) else None,
                    "Assign": self._handle_assign_node(node, assigned_but_unused, line_offset),
                    "Compare": self._handle_compare_node(node, bad_comparisons, source_lines, line_offset),
                    "FunctionDef": self._handle_function_def_node(node, source_lines, line_offset),
                    "ClassDef": self._handle_class_def_node(node, source_lines, line_offset),
                    "AsyncFunctionDef": self._handle_function_def_node(node, source_lines, line_offset),
                    "default": None
                })
            except Exception:
                continue


        for name in imported_names:
            line = self.import_lines.get(name, 0)
            line_content = source_lines[line - 1].strip() if line > 0 and line <= len(source_lines) else ""
            self._add_error(
                line,
                f"Unused import '{name}'",
                "StyleWarning",
                line_content,
            )


        for name, line in assigned_but_unused.items():
            if name not in all_used_names:
                line_content = source_lines[line - 1].strip() if line <= len(source_lines) else ""
                self._add_error(
                    line,
                    f"Unused variable '{name}'",
                    "StyleWarning",
                    line_content,
                )

    def _handle_name_node(self, node: ast.Name, imported_names: Set[str], all_used_names: Set[str]) -> None:
        """Handle Name node in switch statement"""
        all_used_names.add(node.id)
        if node.id in imported_names:
            imported_names.remove(node.id)

    def _handle_assign_node(self, node: ast.Assign, assigned_but_unused: Dict[str, int], line_offset: int) -> None:
        """Handle Assign node in switch statement"""
        for target in node.targets:
            target_type = type(target).__name__
            switch(target_type, {
                "Name": assigned_but_unused.__setitem__(target.id, node.lineno + line_offset),
                "Tuple": [assigned_but_unused.__setitem__(elt.id, node.lineno + line_offset) 
                                for elt in target.elts if isinstance(elt, ast.Name)],
                "default": None
            })

    def _handle_compare_node(self, node: ast.Compare, bad_comparisons: Dict, source_lines: List[str], line_offset: int) -> None:
        """Handle Compare node in switch statement"""
        if node.ops:
            op_type = type(node.ops[0]).__name__
            if op_type in bad_comparisons:
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant):
                        const_value = str(comparator.value)
                        if const_value in bad_comparisons[op_type]:
                            adjusted_line = node.lineno + line_offset
                            line_content = source_lines[adjusted_line - 1].strip() if adjusted_line <= len(source_lines) else ""
                            self._add_error(
                                adjusted_line,
                                bad_comparisons[op_type][const_value],
                                "StyleWarning",
                                line_content,
                            )

    def _handle_function_def_node(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                                 source_lines: List[str], line_offset: int) -> None:
        """Handle FunctionDef and AsyncFunctionDef nodes in switch statement"""
        adjusted_line = node.lineno + line_offset
        line_content = source_lines[adjusted_line - 1].strip() if adjusted_line <= len(source_lines) else ""
        
        if not node.body:
            self._add_error(
                adjusted_line,
                t("empty_block").format(type=t("function")),
                "IndentationWarning",
                line_content,
            )
        elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self._add_error(
                adjusted_line,
                t("empty_block_with_pass").format(type=t("function")),
                "IndentationWarning",
                line_content,
            )

    def _handle_class_def_node(self, node: ast.ClassDef, source_lines: List[str], line_offset: int) -> None:
        """Handle ClassDef node in switch statement"""
        adjusted_line = node.lineno + line_offset
        line_content = source_lines[adjusted_line - 1].strip() if adjusted_line <= len(source_lines) else ""
        
        if not node.body:
            self._add_error(
                adjusted_line,
                t("empty_block").format(type=t("class")),
                "IndentationWarning",
                line_content,
            )
        elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self._add_error(
                adjusted_line,
                t("empty_block_with_pass").format(type=t("class")),
                "IndentationWarning",
                line_content,
            )

    def _add_error(self, line: int, message: str, error_type: str, context: str = None):
        """Helper to add errors with translation support"""
        self.errors.append({
            "line": line,
            "message": message,
            "type": error_type,
            "context": context,
        })

    def _collect_imports_and_definitions(self, tree: ast.AST) -> None:
        """Collect all imported and defined names in the AST."""
        for node in ast.walk(tree):
            node_type = type(node).__name__
            switch(node_type, {
                "Import": self._handle_import_node(node),
                "ImportFrom": self._handle_import_from_node(node),
                "FunctionDef": self.defined_names.add(node.name),
                "AsyncFunctionDef": self.defined_names.add(node.name),
                "ClassDef": self.defined_names.add(node.name),
                "Assign": self._handle_assign_definition_node(node),
                "default": None
            })

    def _handle_import_node(self, node: ast.Import) -> None:
        """Handle Import node in switch statement"""
        for alias in node.names:
            self.imported_names.add(alias.name)
            self.import_lines[alias.name] = node.lineno
            if alias.asname:
                self.imported_names.add(alias.asname)
                self.import_lines[alias.asname] = node.lineno

    def _handle_import_from_node(self, node: ast.ImportFrom) -> None:
        """Handle ImportFrom node in switch statement"""
        module = node.module or ""
        for alias in node.names:
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.imported_names.add(full_name)
            self.import_lines[full_name] = node.lineno
            if alias.asname:
                self.imported_names.add(alias.asname)
                self.import_lines[alias.asname] = node.lineno
            else:
                self.imported_names.add(alias.name)
                self.import_lines[alias.name] = node.lineno

    def _handle_assign_definition_node(self, node: ast.Assign) -> None:
        """Handle Assign node for definitions in switch statement"""
        for target in node.targets:
            target_type = type(target).__name__
            switch(target_type, {
                "Name": self.defined_names.add(target.id),
                "Tuple": [self.defined_names.add(elt.id) for elt in target.elts 
                                 if isinstance(elt, ast.Name)],
                "default": None
            })

    def _check_undefined_names(self, tree: ast.AST, source_lines: List[str]) -> None:
        """Check for undefined names in the AST."""
        defined = self.defined_names.union(self.imported_names)
        builtins = set(dir(__builtins__)).union({
            'self', 'cls', '_', 'print', 'open', 
            'ImportError', 'globals', 'Exception'
        })

        for node in ast.walk(tree):
            try:
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    name = node.id
                    if (name not in defined and 
                        name not in builtins and 
                        not name.startswith('_')):
                        
                        is_attribute = False
                        if hasattr(node, "parent"):
                            parent = node.parent
                            if (isinstance(parent, ast.Attribute) and 
                                parent.value == node):
                                is_attribute = True

                        if not is_attribute:
                            line_content = (
                                source_lines[node.lineno - 1].strip()
                                if node.lineno <= len(source_lines)
                                else ""
                            )
                            self._add_error(
                                node.lineno,
                                t("undefined_name").format(name=name),
                                "NameError",
                                line_content,
                            )
            except Exception:
                continue

    def _check_other_issues(self, tree: ast.AST, source_lines: List[str]) -> None:
        """Check for other potential issues in the code."""
        imported_names = set(self.import_lines.keys())
        all_used_names = set()
        assigned_but_unused = {}

        bad_comparisons = {
            "Eq": {  # ==
                "True": t("redundant_true"),
                "False": t("redundant_false"),
                "None": t("none_comparison"),
            },
            "NotEq": {  # !=
                "True": t("not_true_recommendation"),
                "False": t("not_false_recommendation"),
            },
        }

        for node in ast.walk(tree):
            try:
                node_type = type(node).__name__
                switch(node_type, {
                    "Name": self._handle_name_node(node, imported_names, all_used_names) if isinstance(node.ctx, ast.Load) else None,
                    "Assign": self._handle_assign_node(node, assigned_but_unused, 0),
                    "Compare": self._handle_compare_node(node, bad_comparisons, source_lines, 0),
                    "FunctionDef": self._handle_function_def_node(node, source_lines, 0),
                    "ClassDef": self._handle_class_def_node(node, source_lines, 0),
                    "AsyncFunctionDef": self._handle_function_def_node(node, source_lines, 0),
                    "default": None
                })
            except Exception:
                continue


        for name in imported_names:
            line = self.import_lines.get(name, 0)
            line_content = source_lines[line - 1].strip() if line > 0 and line <= len(source_lines) else ""
            self._add_error(
                line,
                f"Unused import '{name}'",
                "StyleWarning",
                line_content,
            )


        for name, line in assigned_but_unused.items():
            if name not in all_used_names:
                line_content = source_lines[line - 1].strip() if line <= len(source_lines) else ""
                self._add_error(
                    line,
                    f"Unused variable '{name}'",
                    "StyleWarning",
                    line_content,
                )

    def get_errors(self) -> List[Dict[str, str]]:
        """Return the list of errors found."""
        return sorted(self.errors, key=lambda e: e["line"])

def check_syntax(file_path: Union[str, Path]) -> None:
    """Check a Python file and show all errors found."""
    checker = PythonFileChecker()
    checker.check_file(file_path)

    errors = checker.get_errors()

    if not errors:
        if IN_JUPYTER:
            display(Markdown(f"**{t('syntax_check_title')}**\n\n{t('no_errors_found')}"))
        else:
            show_gui_popup(t("syntax_check_title"), t("no_errors_found"))
        return

    error_categories = {
        "Syntax Errors": ["SyntaxError"],
        "File Issues": ["FileNotFound", "EncodingError", "IOError"],
        "Name Issues": ["NameError"],
        "Style Warnings": ["StyleWarning", "IndentationWarning"],
        "Exception Handling": ["ExceptionWarning"],
        "Other Issues": ["AnalysisError"],
    }

    unique_types = sorted(set(e["type"] for e in errors))
    error_text = f"Found {len(errors)} error(s) in {file_path}:\n"
    error_text += f"Error types found: {len(unique_types)}\n\n"


    categorized_errors = {}
    for category, error_types in error_categories.items():
        category_errors = [e for e in errors if e["type"] in error_types]
        if category_errors:
            categorized_errors[category] = category_errors


    for category, category_errors in categorized_errors.items():
        error_text += f"=== {category} ===\n"
        for error in category_errors:
            error_text += f"Line {error['line']}: {error['message']}\n"
            if error.get("context"):
                error_text += f"Context: {error['context']}\n"
            error_text += f"Type: {error['type']}\n\n"

    if IN_JUPYTER:
        display(Markdown(f"**Python Code Analysis**\n\n```\n{error_text}\n```"))
    else:
        show_gui_popup(t("multiple_errors_title"), error_text)


class This:
    """Clase para obtener información del archivo actual"""

    @staticmethod
    def get_caller_path(levels_up: int = 2) -> str:
        """
        Obtiene la ruta del archivo que llamó a esta función
        :param levels_up: Número de niveles en el stack de llamadas a subir (default 2)
        """
        import inspect

        frame = inspect.currentframe()
        try:
            for _ in range(levels_up):
                frame = frame.f_back
                if frame is None:
                    return None

            return frame.f_globals.get("__file__")
        finally:
            del frame

    @staticmethod
    def get_script_path() -> str:
        """Obtiene la ruta del script principal en ejecución"""
        import sys

        return sys.argv[0] if len(sys.argv) > 0 else None


def run(file_path=None):
    def show_error_and_exit():
        show_gui_popup(t("error"), t("provide_file_path"))
        return

    if hasattr(file_path, "__file__"):
        file_path = file_path.__file__

    if file_path is None:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            file_path = This.get_caller_path()

            if file_path is None:
                file_path = This.get_script_path()

    if not file_path or not os.path.exists(file_path):
        show_error_and_exit()
        return

    check_syntax(file_path)
