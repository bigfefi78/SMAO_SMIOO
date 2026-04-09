"""
Valutatore formule per misure
"""

import re
from typing import Dict, Optional, Tuple


class FormulaEvaluator:
    """
    Valuta formule matematiche sostituendo placeholder con valori sensori

    Esempio:
        formula = "{T-01} - {T-02}"
        values = {"T-01": 50.5, "T-02": 30.2}
        result = evaluate(formula, values)  # 20.3
    """

    def __init__(self):
        # Pattern per trovare placeholder: {LABEL}
        self.placeholder_pattern = re.compile(r"\{([^}]+)\}")

    def evaluate(
        self, formula: str, sensor_values: Dict[str, float]
    ) -> Tuple[bool, Optional[float], str]:
        """
        Valuta formula sostituendo valori sensori

        Args:
            formula: Formula con placeholder (es. "{T-01} - {T-02}")
            sensor_values: Dizionario {label: valore} (es. {"T-01": 50.5, "T-02": 30.2})

        Returns:
            (success, result, error_message)
            - success: True se calcolo riuscito
            - result: Valore calcolato (None se errore)
            - error_message: Messaggio di errore (vuoto se ok)
        """
        if not formula or not formula.strip():
            return False, None, "Formula vuota"

        # Trova tutti i placeholder
        placeholders = self.placeholder_pattern.findall(formula)

        if not placeholders:
            return False, None, "Nessun placeholder trovato nella formula"

        # Verifica che tutti i sensori abbiano valori
        missing_sensors = []
        for label in placeholders:
            if label not in sensor_values:
                missing_sensors.append(label)

        if missing_sensors:
            return False, None, f"Sensori mancanti: {', '.join(missing_sensors)}"

        # Sostituisci placeholder con valori
        evaluated_formula = formula
        for label in placeholders:
            value = sensor_values[label]
            # Sostituisci {LABEL} con valore numerico
            evaluated_formula = evaluated_formula.replace(f"{{{label}}}", str(value))

        # Valuta espressione matematica
        try:
            # Usa eval in modo sicuro (solo operazioni matematiche base)
            result = self._safe_eval(evaluated_formula)
            return True, result, ""

        except Exception as ex:
            return False, None, f"Errore calcolo: {str(ex)}"

    def _safe_eval(self, expression: str) -> float:
        """
        Valuta espressione matematica in modo sicuro

        Args:
            expression: Espressione (es. "50.5 - 30.2")

        Returns:
            Risultato numerico

        Raises:
            ValueError: Se espressione non valida
        """
        # Permetti solo operatori matematici base e numeri
        allowed_chars = set("0123456789+-*/().eE ")

        if not all(c in allowed_chars for c in expression):
            raise ValueError("Caratteri non permessi nell'espressione")

        # Valuta
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as ex:
            raise ValueError(f"Errore valutazione: {ex}")

    def get_required_sensors(self, formula: str) -> list:
        """
        Estrae lista sensori richiesti dalla formula

        Args:
            formula: Formula con placeholder

        Returns:
            Lista di label sensori (es. ["T-01", "T-02"])
        """
        return self.placeholder_pattern.findall(formula)

    def validate_formula(self, formula: str) -> Tuple[bool, str]:
        """
        Valida sintassi formula

        Args:
            formula: Formula da validare

        Returns:
            (is_valid, error_message)
        """
        if not formula or not formula.strip():
            return False, "Formula vuota"

        placeholders = self.placeholder_pattern.findall(formula)

        if not placeholders:
            return False, "Nessun placeholder trovato (usa {LABEL})"

        # Crea valori fittizi per test
        test_values = {label: 1.0 for label in placeholders}

        success, _, error = self.evaluate(formula, test_values)

        if not success:
            return False, error

        return True, ""


# ===== TEST =====
if __name__ == "__main__":
    evaluator = FormulaEvaluator()

    # Test 1: Differenza
    formula1 = "{T-01} - {T-02}"
    values1 = {"T-01": 50.5, "T-02": 30.2}
    success, result, error = evaluator.evaluate(formula1, values1)
    print(f"Test 1: {formula1}")
    print(f"  Risultato: {result if success else error}")

    # Test 2: Media
    formula2 = "({T-01} + {T-02} + {T-03}) / 3"
    values2 = {"T-01": 10, "T-02": 20, "T-03": 30}
    success, result, error = evaluator.evaluate(formula2, values2)
    print(f"\nTest 2: {formula2}")
    print(f"  Risultato: {result if success else error}")

    # Test 3: Formula complessa
    formula3 = "({T-01} - {T-02}) * 2 + {T-03}"
    values3 = {"T-01": 50, "T-02": 30, "T-03": 5}
    success, result, error = evaluator.evaluate(formula3, values3)
    print(f"\nTest 3: {formula3}")
    print(f"  Risultato: {result if success else error}")

    # Test 4: Sensore mancante
    formula4 = "{T-01} - {T-99}"
    values4 = {"T-01": 50}
    success, result, error = evaluator.evaluate(formula4, values4)
    print(f"\nTest 4: {formula4}")
    print(f"  Risultato: {result if success else error}")
