from formula_class import FormulaConverter
from ltn_wrapper import main

def ltn_example():
    formulas = []
    string = "fof(all_A, axiom, ![X_A]: ((a(X_A)))).fof(all_not_A, axiom, ![X_not_A]: ((~a(X_not_A))))."

    LTNFormulaTest = FormulaConverter(string, 'ltn')
    print("LTNFormulaTest: ")
    formulas = LTNFormulaTest.convert()
    print(formulas)

    training_epochs=1000

    main(
        formulas=formulas,
        training_epochs=training_epochs
    )
