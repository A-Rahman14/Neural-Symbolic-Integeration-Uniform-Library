import ltn
from gavel.dialects.tptp.parser import *
from gavel.logic.logic import *


# Connectives
Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
And = ltn.Connective(ltn.fuzzy_ops.AndProd())
Or = ltn.Connective(ltn.fuzzy_ops.OrProbSum())
Implies = ltn.Connective(ltn.fuzzy_ops.ImpliesReichenbach())
# Quantifiers
Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier="f")
Exists = ltn.Quantifier(ltn.fuzzy_ops.AggregPMean(p=2), quantifier="e")


def capitalize_first_letter(symbol):
    if symbol and symbol[0].islower():
        return symbol[0].upper() + symbol[1:]
    return symbol

def lowercase_first_letter(symbol):
    if symbol and symbol[0].isupper():
        return symbol[0].lower() + symbol[1:]
    return symbol

def convert_to_ltn(formula):
    if isinstance(formula, AnnotatedFormula):
        return convert_to_ltn(formula.formula)
    elif isinstance(formula, QuantifiedFormula):
        quantifier = formula.quantifier.name.lower()
        variable = lowercase_first_letter(formula.variables[0].symbol)
        subformula = convert_to_ltn(formula.formula)
        if quantifier == 'universal':
            return f"Forall({variable}, {subformula})"
        elif quantifier == 'existential':
            return f"Exists({variable}, {subformula})"
    elif isinstance(formula, BinaryFormula):
        left = convert_to_ltn(formula.left)
        right = convert_to_ltn(formula.right)
        operator = formula.operator.name.lower()
        if operator == 'conjunction':
            return f"And({left}, {right})"
        elif operator == 'disjunction':
            return f"Or({left}, {right})"
        elif operator == 'implication':
            return f"Implies({left}, {right})"
    elif isinstance(formula, UnaryFormula):
        subformula = convert_to_ltn(formula.formula)
        connective = formula.connective.name.lower()
        if connective == 'negation':
            return f"Not({subformula})"
    elif isinstance(formula, Constant):
        symbol = lowercase_first_letter(formula.symbol)
        return symbol
    elif isinstance(formula, PredicateExpression):
        predicate = capitalize_first_letter(formula.predicate)
        arguments = ', '.join([lowercase_first_letter(arg.symbol) for arg in formula.arguments])
        return f"{predicate}({arguments})"
    # Handle other types of formulas as needed.
    return ""

def convert_to_kbann_horn(formula):
    if isinstance(formula, AnnotatedFormula):
        return convert_to_kbann_horn(formula.formula)
    elif isinstance(formula, QuantifiedFormula):
        # Handling quantifiers (existential or universal)
        quantifier = formula.quantifier.name.lower()
        variable = lowercase_first_letter(formula.variables[0].symbol)
        subformula = convert_to_kbann_horn(formula.formula)
        if quantifier == 'universal':
            return f"Forall {variable}, {subformula}"
        elif quantifier == 'existential':
            return f"Exists {variable}, {subformula}"
    elif isinstance(formula, BinaryFormula):
        # Binary formulas could include implications which are direct candidates for Horn clauses
        operator = formula.operator.name.lower()
        if operator == 'implication':
            head = convert_to_kbann_horn(formula.right)  # head is the consequent of the implication
            body = convert_to_kbann_horn(formula.left)   # body is the antecedent
            if isinstance(body, tuple) and body[0] == 'conjunction':
                # Flatten the conjunction into a comma-separated string
                body = ', '.join(body[1:])
            return f"{head} :- {body}"
        else:
            # Other binary operations need to be handled appropriately
            left = convert_to_kbann_horn(formula.left)
            right = convert_to_kbann_horn(formula.right)
            return handle_binary_operator(operator, left, right)
    elif isinstance(formula, UnaryFormula):
        # Unary formulas like negation
        subformula = convert_to_kbann_horn(formula.formula)
        connective = formula.connective.name.lower()
        return (connective, subformula)
    elif isinstance(formula, Constant):
        # Constants directly return their symbol
        symbol = lowercase_first_letter(formula.symbol)
        return symbol
    elif isinstance(formula, PredicateExpression):
        # Predicate expressions are usually the leaves of the formula tree
        predicate = capitalize_first_letter(formula.predicate)
        arguments = ', '.join([lowercase_first_letter(arg.symbol) for arg in formula.arguments])
        return f"{predicate}({arguments})"

def handle_binary_operator(operator, left, right):
    if operator == 'conjunction':
        # This will handle nested conjunctions and return a flat list
        left_items = [left] if not isinstance(left, tuple) or left[0] != 'conjunction' else left[1:]
        right_items = [right] if not isinstance(right, tuple) or right[0] != 'conjunction' else right[1:]
        return ('conjunction', *left_items, *right_items)
    elif operator == 'disjunction':
        return f"({left} OR {right})"
    else:
        return f"({left} {operator.upper()} {right})"

def capitalize_first_letter(symbol):
    return symbol[0].upper() + symbol[1:] if symbol and symbol[0].islower() else symbol

def lowercase_first_letter(symbol):
    return symbol[0].lower() + symbol[1:] if symbol and symbol[0].isupper() else symbol






