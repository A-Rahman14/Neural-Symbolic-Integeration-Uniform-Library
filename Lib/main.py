from gavel.dialects.tptp.parser import TPTPParser
from gavel.logic.problem import AnnotatedFormula

from ltn_example import *
from kbann_example import *

# parser = TPTPParser()
# # string = "cnf(name, axiom, a | b)."
# string = "fof(scholarship_rule, axiom, (take_course & has_superviser) => scholarship_candidate)."
# formulas = []
#
# for line in parser.stream_lines(string):
#     structure = parser.parse(line)
#     if structure:
#         ltn_formula = convert_to_kbann_horn(structure[0].formula)
#         formulas.append(ltn_formula)
# print(formulas)


# for line in parser.stream_lines(string):
#     structure = parser.parse(line)
#     if structure:  # Check if structure is not empty
#         for formula in structure:
#             if isinstance(formula, AnnotatedFormula):
#                 # Assuming the formula data is accessible directly or via a specific method
#                 print("Formula Name:", formula.name)
#                 print("Formula Role:", formula.role)
#                 if hasattr(formula, 'formula'):
#                     # Check if it has a formula attribute and print it
#                     print("Formula Content:", formula.formula)
#                 else:
#                     # If no direct formula attribute, print available attributes
#                     print("Available Attributes:", dir(formula))
#     else:
#         print("No parsed formula found.")






# from gavel.dialects.tptp.parser import TPTPParser
# from gavel.dialects.tptp.parser import *
# from gavel.logic.logic import *
#
# parser = TPTPParser()
# string = "cnf(name, axiom, a | b)."
# formulas = []
# for line in parser.stream_lines(string):
#     structure = parser.parse(line)
#     # print(structure.formula)
# help(structure)
# help(parser)
    # if structure:
    #     ltn_formula = convert_to_ltn(structure[0].formula)
    #     formulas.append(ltn_formula)
# print(formulas)
# print(structure)






#
#
if __name__ == "__main__":
    # kbann_example()
    ltn_example()


import trace
import sys

# # Import your modules
# from ltn_example import *
# from kbann_example import *
# from KBANN import *
#
# def trace_calls(frame, event, arg):
#     if event != 'call':
#         return
#     co = frame.f_code
#     filename = co.co_filename
#     # Check if the filename ends with one of your specified files
#     if filename.endswith(('main.py', 'kbann_example.py', 'KBANN.py')):
#         print('Call to {} on line {} of {}'.format(co.co_name, frame.f_lineno, filename))
#         return trace_calls
#     return None
#
# if __name__ == "__main__":
#     # Set the trace function
#     sys.settrace(trace_calls)
#     # Call the function you want to trace
#     kbann_example()
#     # Disable tracing
#     sys.settrace(None)