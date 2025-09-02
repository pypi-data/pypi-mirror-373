from .shared import (show_gui_popup, show_alert_popup, IN_JUPYTER, 
                     pd, Path, List, Dict, Union, Optional, Any, Set, Tuple,
                     os, ast)

class ComplexityAnalyzer:
    """
    Analiza archivos Python para calcular complejidad y sugerir mejoras.
    """

    def __init__(self, debug: bool = False):
        self.debug = debug

    def analyze(self, target: Union[str, Path, List[Union[str, Path]]]) -> Dict[str, Dict]:
        """
        Analiza uno o varios archivos o carpetas.
        Devuelve un diccionario con resultados por archivo.
        """
        paths = self._normalize_targets(target)
        results = {}
        for path in paths:
            if path.suffix == ".py":
                try:
                    results[str(path)] = self._analyze_file(path)
                except Exception as e:
                    results[str(path)] = {"error": str(e)}
        return results

    def _normalize_targets(self, target):
        if isinstance(target, (str, Path)):
            target = [target]
        paths = []
        for t in target:
            p = Path(t)
            if p.is_dir():
                paths.extend(list(p.rglob("*.py")))
            elif p.is_file():
                paths.append(p)
        return paths

    def _analyze_file(self, path: Path) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()

        tree = ast.parse(src)
        complexity_score = 0
        suggestions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                complexity_score += 1

            # Detectar cadenas largas de if/elif comparando la misma variable
            if isinstance(node, ast.If):
                chain = self._collect_if_chain(node)
                if len(chain) >= 3 and self._same_test_var(chain):
                    lineno = getattr(node, "lineno", None)
                    suggestions.append({
                        "line": lineno,
                        "issue": "Cadena larga de if/elif comparando el mismo valor",
                        "recommendation": "Usar Switch de helper.pyswitch",
                        "current_complexity": len(chain),
                        "possible_complexity": 1
                    })

        return {
            "complexity_score": complexity_score,
            "suggestions": suggestions
        }

    def _collect_if_chain(self, node: ast.If):
        """Recorre if/elif hasta el final para contar el tamaño de la cadena."""
        chain = [node]
        current = node
        while isinstance(current.orelse, list) and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            current = current.orelse[0]
            chain.append(current)
        return chain

    def _same_test_var(self, chain: List[ast.If]) -> bool:
        """Verifica si todos los if/elif comparan la misma variable a igualdad."""
        # Simplificación: chequea si todos son comparaciones simples con == sobre el mismo nombre
        first_var = None
        for n in chain:
            if not isinstance(n.test, ast.Compare) or len(n.test.ops) != 1 or not isinstance(n.test.ops[0], ast.Eq):
                return False
            left = n.test.left
            if not isinstance(left, ast.Name):
                return False
            if first_var is None:
                first_var = left.id
            elif first_var != left.id:
                return False
        return True

    def run_and_show(
        self, 
        target: Union[str, Path, List[Union[str, Path]]], 
        title: Optional[str] = None
    ):
        """
        Convenience: run analyze() and show results in GUI popup (or fallback to console).
        If running in Jupyter and pandas is available, also returns a DataFrame of issues.
        """
        title = title or "Complexity Analysis Results"
        try:
            result = self.analyze(target)
            pretty = self._format_results_for_display(result)
            show_gui_popup(title, pretty)

            df = None
            try:
                if IN_JUPYTER:
                    all_issues = []
                    for file, data in result.items():
                        for issue in data.get("issues", []):
                            issue_copy = issue.copy()
                            issue_copy["file"] = file
                            all_issues.append(issue_copy)
                    if all_issues:
                        df = pd.DataFrame(all_issues)
            except Exception:
                pass

            return (result, df) if df is not None else result

        except Exception as e:
            show_alert_popup("error", "An unexpected error occurred during complexity analysis", detail=str(e))
            return {}

    def _normalize_targets(self, target: Union[str, Path, List[Union[str, Path]]]) -> List[Path]:
        if isinstance(target, (str, Path)):
            target = [target]
        paths: List[Path] = []
        for t in target:
            p = Path(t)
            if p.is_dir():
                for f in p.rglob("*.py"):
                    if any(part.startswith(".") for part in f.parts):
                        continue
                    if "site-packages" in str(f) or "dist-packages" in str(f):
                        continue
                    paths.append(f)
            elif p.is_file():
                paths.append(p)
            else:
                raise FileNotFoundError(f"Target not found: {t}")
        # dedupe and normalize
        unique: List[Path] = []
        seen: Set[str] = set()
        cwd = Path(os.getcwd())
        for p in paths:
            try:
                rel = os.path.relpath(str(p), cwd)
                if rel.startswith("..") or rel.startswith("/"):
                    normalized = p.resolve()
                else:
                    normalized = Path(rel)
            except Exception:
                normalized = p.resolve()
            if str(normalized) not in seen:
                seen.add(str(normalized))
                unique.append(normalized)
        return sorted(unique)
