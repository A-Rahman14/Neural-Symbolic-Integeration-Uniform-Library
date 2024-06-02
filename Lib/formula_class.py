import ltn
from gavel.dialects.tptp.parser import *
from gavel.logic.logic import *
# from lnn import Proposition, And, Or, Not, Implies, Fact


class FormulaConverter:
    # Initialize LTN specific components
    Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
    And = ltn.Connective(ltn.fuzzy_ops.AndProd())
    Or = ltn.Connective(ltn.fuzzy_ops.OrProbSum())
    Implies = ltn.Connective(ltn.fuzzy_ops.ImpliesReichenbach())
    Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier="f")
    Exists = ltn.Quantifier(ltn.fuzzy_ops.AggregPMean(p=2), quantifier="e")

    # Parser initialization
    parser = TPTPParser()

    def __init__(self, input_data, method, is_file=False):
        self.method = method
        if is_file:
            self.input_data = self._read_file
        else:
            self.input_data = input_data

    def _capitalize_first_letter(self, symbol):
        return symbol[0].upper() + symbol[1:] if symbol and symbol[0].islower() else symbol

    def _lowercase_first_letter(self, symbol):
        return symbol[0].lower() + symbol[1:] if symbol and symbol[0].isupper() else symbol

    def convert(self):
        formulas = []
        for line in self.parser.stream_lines(self.input_data):
            structure = self.parser.parse(line)
            if structure:
                formula = self._convert_formula(structure[0].formula)
                formulas.append(formula)
        return formulas

    def _read_file(self):
        with open(self.input_data, "r") as file:
            return file.read()

    def _convert_formula(self, formula):
        if self.method == "ltn":
            return self._convert_to_ltn(formula)
        elif self.method == "kbann":
            return self._convert_to_kbann_horn(formula)
        else:
            raise ValueError("Unsupported conversion method")

    def _convert_to_ltn(self, formula):
        if isinstance(formula, AnnotatedFormula):
            return self._convert_to_ltn(formula.formula)
        elif isinstance(formula, QuantifiedFormula):
            quantifier = formula.quantifier.name.lower()
            variable = self._lowercase_first_letter(formula.variables[0].symbol)
            subformula = self._convert_to_ltn(formula.formula)
            if quantifier == "universal":
                return f"Forall({variable}, {subformula})"
            elif quantifier == "existential":
                return f"Exists({variable}, {subformula})"
        elif isinstance(formula, BinaryFormula):
            left = self._convert_to_ltn(formula.left)
            right = self._convert_to_ltn(formula.right)
            operator = formula.operator.name.lower()
            if operator == "conjunction":
                return f"And({left}, {right})"
            elif operator == "disjunction":
                return f"Or({left}, {right})"
            elif operator == "implication":
                return f"Implies({left}, {right})"
        elif isinstance(formula, UnaryFormula):
            subformula = self._convert_to_ltn(formula.formula)
            connective = formula.connective.name.lower()
            if connective == "negation":
                return f"Not({subformula})"
        elif isinstance(formula, Constant):
            symbol = self._lowercase_first_letter(formula.symbol)
            return symbol
        elif isinstance(formula, PredicateExpression):
            predicate = self._capitalize_first_letter(formula.predicate)
            arguments = ", ".join([self._lowercase_first_letter(arg.symbol) for arg in formula.arguments])
            return f"{predicate}({arguments})"
        # Handle other types of formulas as needed.
        return ""

    def _convert_to_kbann_horn(self, formula):
        if isinstance(formula, AnnotatedFormula):
            return self._convert_to_kbann_horn(formula.formula)
        elif isinstance(formula, QuantifiedFormula):
            quantifier = formula.quantifier.name.lower()
            variable = self._lowercase_first_letter(formula.variables[0].symbol)
            subformula = self._convert_to_kbann_horn(formula.formula)
            if quantifier == "universal":
                return f"Forall {variable}, {subformula}"
            elif quantifier == "existential":
                return f"Exists {variable}, {subformula}"
        elif isinstance(formula, BinaryFormula):
            operator = formula.operator.name.lower()
            if operator == "implication":
                head = self._convert_to_kbann_horn(formula.right)
                body = self._convert_to_kbann_horn(formula.left)
                if isinstance(body, tuple) and body[0] == "conjunction":
                    body = ", ".join(body[1:])
                return f"{head} :- {body}"
            else:
                left = self._convert_to_kbann_horn(formula.left)
                right = self._convert_to_kbann_horn(formula.right)
                return self._handle_binary_operator(operator, left, right)
        elif isinstance(formula, UnaryFormula):
            subformula = self._convert_to_kbann_horn(formula.formula)
            connective = formula.connective.name.lower()
            return (connective, subformula)
        elif isinstance(formula, Constant):
            symbol = self._lowercase_first_letter(formula.symbol)
            return symbol
        elif isinstance(formula, PredicateExpression):
            predicate = self._capitalize_first_letter(formula.predicate)
            arguments = ", ".join([self._lowercase_first_letter(arg.symbol) for arg in formula.arguments])
            return f"{predicate}({arguments})"

    def _handle_binary_operator(self, operator, left, right):
        if operator == "conjunction":
            left_items = [left] if not isinstance(left, tuple) or left[0] != "conjunction" else left[1:]
            right_items = [right] if not isinstance(right, tuple) or right[0] != "conjunction" else right[1:]
            return "conjunction", *left_items, *right_items
        elif operator == "disjunction":
            return f"({left} OR {right})"
        else:
            return f"({left} {operator.upper()} {right})"
