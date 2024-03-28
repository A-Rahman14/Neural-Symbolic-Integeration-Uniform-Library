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

# Assuming you have a parser and the string is parsed to 'structure',
# which is a list containing your TPTP parsed objects.
# parser = TPTPParser()

# string = "fof(mortal_humans, axiom, ![X]: ((cube(X) & small(X)) => ?[Y]: leftOf(X,Y)))."
# string = "cnf(a1, axiom, a | b).cnf(a1, axiom, ~a).cnf(a2, negated_conjecture, b)."
#
# for line in parser.stream_lines(string):
#     structure = parser.parse(line)
#     if structure:
#         ltn_formula = convert_to_ltn(structure[0].formula)
#         print(ltn_formula)
#         # print(structure[0].formula)

