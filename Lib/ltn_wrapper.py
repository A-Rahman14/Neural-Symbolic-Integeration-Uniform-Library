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


def convert_to_ltn(formula):
    if isinstance(formula, AnnotatedFormula):
        # Handle the annotated formula case.
        return convert_to_ltn(formula.formula)
    elif isinstance(formula, QuantifiedFormula):
        quantifier = formula.quantifier.name.lower()
        if quantifier == 'universal':
            # Convert to Forall.
            variable = formula.variables[0].symbol
            subformula = convert_to_ltn(formula.formula)
            return f"Forall({variable}, {subformula})"
        elif quantifier == 'existential':
            # Convert to Exists.
            variable = formula.variables[0].symbol
            subformula = convert_to_ltn(formula.formula)
            return f"Exists({variable}, {subformula})"
    elif isinstance(formula, BinaryFormula):
        # Handle binary connectives (And, Or, Implies, etc.).
        left = convert_to_ltn(formula.left)
        right = convert_to_ltn(formula.right)
        operator = formula.operator.name.lower()
        if operator == 'conjunction':
            return f"And({left}, {right})"
        elif operator == 'implication':
            return f"Implies({left}, {right})"
        # Add other operators as needed.
    elif isinstance(formula, PredicateExpression):
        # Handle predicate expressions.
        predicate = formula.predicate
        arguments = ', '.join([arg.symbol for arg in formula.arguments])
        return f"{predicate}({arguments})"
    # Handle other types of formulas as needed.

    return ""

# Assuming you have a parser and the string is parsed to 'structure',
# which is a list containing your TPTP parsed objects.
parser = TPTPParser()

string = "fof(mortal_humans, axiom, ![X]: ((cube(X) & small(X)) => ?[Y]: leftOf(X,Y)))."
for line in parser.stream_lines(string):
    structure = parser.parse(line)
    if structure:
        ltn_formula = convert_to_ltn(structure[0].formula)
        print(ltn_formula)
