from KBANN import *
from dimacs import *
from KBANN import dimacs_to_kbann_rules
from formula_class import FormulaConverter

def kbann_example():
    kbann_tptp = "fof(scholarship_candidate, axiom, ((take_course & has_supervisor) => scholarship_candidate)).fof(has_supervisor, axiom, (grad_student => has_supervisor)).fof(take_course, axiom,(grad_student => take_course))."
    LTNFormulaTest = FormulaConverter(kbann_tptp, 'kbann')
    print("LTNFormulaTest: ")
    formulas = LTNFormulaTest.convert()
    print(formulas)

    def format_formulas(formulas):
        formatted = []
        for formula in formulas:
            formatted.append(formula)
        file_data = '.\n'.join(formatted) + '.'
        with open('tptp_kbann_rules_horn.txt', 'w') as file:
            file.write(file_data)

    format_formulas(formulas)

    variable_mapping = {
        1: "grad_student",
        2: "has_supervisor",
        3: "take_course",
        4: "scholarship_candidate"
    }
    dimacs_formatter = DIMACSFormatter()
    dimacs_formatter.map_variable_names(variable_mapping)

    # Adding some clauses - for example purposes
    dimacs_formatter.add_clause([-3, -2, 4])  # scholarship_candidate :- take_course, has_superviser.
    dimacs_formatter.add_clause([-1, 2])  # has_superviser :- grad_student.
    dimacs_formatter.add_clause([-1, 3])  # take_course :- grad_student.

    dimacs_string = dimacs_formatter.generate_dimacs()
    print(dimacs_string)
    # kbann_rules = dimacs_to_kbann_rules(variable_mapping)
    # print(kbann_rules)

    CURRENT_DIRECTOR = os.getcwd()

    # Initial parameters
    training_epochs = 2000

    atoms_to_add = ["complete_course", "freshman", "sent_application", "high_gpa"]
    # Load training data
    data_file_path = os.path.join(CURRENT_DIRECTOR, "Datasets", "student.txt")
    X, y, feature_names = load_data(data_file_path)
    # Call main with the use_dimacs flag set to True
    main(
        X,
        y,
        feature_names,
        training_epochs,
        atoms_to_add=atoms_to_add,
        use_dimacs=True,
        mapping = variable_mapping,
        input_filename = "example1.dimacs"
    )
