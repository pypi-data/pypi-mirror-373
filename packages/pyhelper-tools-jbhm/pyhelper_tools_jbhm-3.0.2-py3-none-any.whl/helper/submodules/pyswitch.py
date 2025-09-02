from typing import Callable, Any, Dict, List
import pandas as pd
import numpy as np
import re
import inspect

class BaseSwitch:
    """Clase base con la lógica común para ambos tipos de switch"""
    
    def __init__(self, value: Any, *, match_all: bool = False, debug: bool = False):
        self.value = value
        self.match_all = match_all
        self.debug = debug

    def _match_case(self, key: Any) -> bool:
        """Lógica común para comparación de casos"""
        try:
            if self.value == key:
                return True

            if isinstance(key, re.Pattern):
                return bool(key.match(str(self.value)))

            if isinstance(key, type):
                return isinstance(self.value, key)

            if isinstance(key, Callable):
                return key(self.value)

            if isinstance(self.value, (pd.Series, pd.DataFrame, np.ndarray)):
                return str(self.value) == str(key)

        except Exception as e:
            if self.debug:
                print(f"[Switch] Error matching case {key}: {e}")
            return False

        return False

    def _convert_dict_to_pairs(self, case_dict: Dict) -> List:
        """Convierte formato de diccionario a pares de casos"""
        pairs = []
        try:

            if 'cases' in case_dict:
                for case in case_dict.get('cases', []):
                    pairs.extend([case['case'], case['then']])
                if 'default' in case_dict:
                    pairs.extend(['default', case_dict['default']])
            

            else:
                for case_key, action in case_dict.items():
                    if case_key == "default":
                        pairs.extend(['default', action])
                    else:
                        pairs.extend([case_key, action])
                        
        except (KeyError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid dictionary format: {e}") from e
            
        return pairs

    def _parse_cases(self, *cases: Any) -> List:
        """Parsea casos en diferentes formatos"""
        if not cases:
            raise ValueError("At least one case must be provided")
            

        if len(cases) == 1 and isinstance(cases[0], dict):
            return self._convert_dict_to_pairs(cases[0])
        

        if len(cases) == 1 and isinstance(cases[0], (list, tuple)):
            return list(cases[0])
        

        return list(cases)

    def _validate_cases(self, cases: List) -> None:
        """Valida que los casos tengan el formato correcto"""
        if len(cases) % 2 != 0:
            raise ValueError("Cases must be defined in pairs: (condition, action)")
        

        default_count = cases.count('default')
        if default_count > 1:
            raise ValueError("Only one default case is allowed")
        

        if 'default' in cases:
            default_index = cases.index('default')
            if default_index % 2 != 0:
                raise ValueError("Default case must be a condition (even index)")

    def _log_match(self, condition: Any, switch_type: str) -> None:
        """Registra coincidencias en modo debug"""
        if self.debug:
            print(f"[{switch_type}] Matched case: {repr(condition)}")
            print(f"[{switch_type}] Value: {repr(self.value)}")

    def _log_default(self, switch_type: str) -> None:
        """Registra ejecución de default en modo debug"""
        if self.debug:
            print(f"[{switch_type}] Executing default case")


class Switch(BaseSwitch):
    """Implementación sincrónica del switch con múltiples formatos"""
    
    def __call__(self, *cases: Any) -> Any:
        """
        Ejecuta el switch con diferentes formatos:
        
        Formato 1: Pares tradicionales
            Switch(value)(cond1, action1, cond2, action2, default, default_action)
        
        Formato 2: Diccionario estructurado
            Switch(value)({
                "cases": [
                    {"case": cond1, "then": action1},
                    {"case": cond2, "then": action2}
                ],
                "default": default_action
            })
        
        Formato 3: Diccionario directo
            Switch(value)({cond1: action1, cond2: action2, "default": default_action})
        """
        try:
            parsed_cases = self._parse_cases(*cases)
            self._validate_cases(parsed_cases)
            
            matched_any = False
            results = []

            for i in range(0, len(parsed_cases), 2):
                condition = parsed_cases[i]
                action = parsed_cases[i + 1]

                if condition == "default":
                    continue

                if self._match_case(condition):
                    matched_any = True
                    self._log_match(condition, "Switch")

                    result = self._run_action(action)
                    results.append(result)
                    
                    if not self.match_all:
                        return result


            if not matched_any or self.match_all:
                default_result = self._handle_default(parsed_cases, matched_any)
                if default_result is not None:
                    if self.match_all:
                        results.append(default_result)
                        return results
                    return default_result

            if self.match_all:
                return results
                
            raise ValueError(f"No matching case found for: {repr(self.value)}")

        except Exception as e:
            if self.debug:
                print(f"[Switch] Error: {e}")
            raise

    def _handle_default(self, cases: List, matched_any: bool) -> Any:
        """Maneja la ejecución del caso default"""
        if "default" in cases:
            idx = cases.index("default")
            if not matched_any or self.match_all:
                self._log_default("Switch")
                return self._run_action(cases[idx + 1])
        return None

    def _run_action(self, action: Any) -> Any:
        """Ejecuta una acción sincrónica"""
        try:
            if callable(action):
                return action()
            return action
        except Exception as e:
            if self.debug:
                print(f"[Switch] Error executing action: {e}")
            raise


class AsyncSwitch(BaseSwitch):
    """Implementación asincrónica del switch con múltiples formatos"""
    
    async def __call__(self, *cases: Any) -> Any:
        """Versión asincrónica del switch con los mismos formatos"""
        try:
            parsed_cases = self._parse_cases(*cases)
            self._validate_cases(parsed_cases)
            
            matched_any = False
            results = []

            for i in range(0, len(parsed_cases), 2):
                condition = parsed_cases[i]
                action = parsed_cases[i + 1]

                if condition == "default":
                    continue

                if self._match_case(condition):
                    matched_any = True
                    self._log_match(condition, "AsyncSwitch")

                    result = await self._run_action(action)
                    results.append(result)
                    
                    if not self.match_all:
                        return result


            if not matched_any or self.match_all:
                default_result = await self._handle_default(parsed_cases, matched_any)
                if default_result is not None:
                    if self.match_all:
                        results.append(default_result)
                        return results
                    return default_result

            if self.match_all:
                return results
                
            raise ValueError(f"No matching case found for: {repr(self.value)}")

        except Exception as e:
            if self.debug:
                print(f"[AsyncSwitch] Error: {e}")
            raise

    async def _handle_default(self, cases: List, matched_any: bool) -> Any:
        """Maneja la ejecución del caso default asincrónico"""
        if "default" in cases:
            idx = cases.index("default")
            if not matched_any or self.match_all:
                self._log_default("AsyncSwitch")
                return await self._run_action(cases[idx + 1])
        return None

    async def _run_action(self, action: Any) -> Any:
        """Ejecuta una acción asincrónica"""
        try:
            if callable(action):
                if inspect.iscoroutinefunction(action):
                    return await action()
                result = action()
                return await result if inspect.isawaitable(result) else result
            return action
        except Exception as e:
            if self.debug:
                print(f"[AsyncSwitch] Error executing action: {e}")
            raise



def switch(value: Any, *cases: Any, **kwargs: Any) -> Any:
    """Función wrapper para uso más natural del switch"""
    return Switch(value, **kwargs)(*cases)

async def async_switch(value: Any, *cases: Any, **kwargs: Any) -> Any:
    """Función wrapper asincrónica para uso más natural"""
    return await AsyncSwitch(value, **kwargs)(*cases)
