from dimacs import *
from KBANN import *
from gavel.dialects.tptp.parser import *
import torch
from ltn_wrapper import *
from sklearn.metrics import accuracy_score
import numpy as np


nr_samples = 100
dataset = torch.rand((nr_samples, 2))
labels_dataset = torch.sum(torch.square(dataset - torch.tensor([.5, .5])), dim=1) < .09


if __name__ == "__main__":

    parser = TPTPParser()

    string = "fof(all_A, axiom, ![X_A]: ((a(X_A)))).fof(all_not_A, axiom, ![X_not_A]: ((~a(X_not_A))))."
    formulas = []
    for line in parser.stream_lines(string):
        structure = parser.parse(line)
        if structure:
            ltn_formula = convert_to_ltn(structure[0].formula)
            formulas.append(ltn_formula)
    print(formulas)


    class ModelA(torch.nn.Module):
        def __init__(self):
            super(ModelA, self).__init__()
            self.sigmoid = torch.nn.Sigmoid()
            self.layer1 = torch.nn.Linear(2, 16)
            self.layer2 = torch.nn.Linear(16, 16)
            self.layer3 = torch.nn.Linear(16, 1)
            self.elu = torch.nn.ELU()

        def forward(self, x):
            x = self.elu(self.layer1(x))
            x = self.elu(self.layer2(x))
            return self.sigmoid(self.layer3(x))


    A = ltn.Predicate(ModelA())

    # we define the connectives, quantifiers, and the SatAgg
    Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
    Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier="f")
    SatAgg = ltn.fuzzy_ops.SatAgg()


    # this is a standard PyTorch DataLoader to load the dataset for the training and testing of the model
    class DataLoader(object):
        def __init__(self,
                     data,
                     labels,
                     batch_size=1,
                     shuffle=True):
            self.data = data
            self.labels = labels
            self.batch_size = batch_size
            self.shuffle = shuffle

        def __len__(self):
            return int(np.ceil(self.data.shape[0] / self.batch_size))

        def __iter__(self):
            n = self.data.shape[0]
            idxlist = list(range(n))
            if self.shuffle:
                np.random.shuffle(idxlist)

            for _, start_idx in enumerate(range(0, n, self.batch_size)):
                end_idx = min(start_idx + self.batch_size, n)
                data = self.data[idxlist[start_idx:end_idx]]
                labels = self.labels[idxlist[start_idx:end_idx]]

                yield data, labels


    # define metrics for evaluation of the model

    # it computes the overall satisfaction level on the knowledge base using the given data loader (train or test)
    def compute_sat_level(loader):
        mean_sat = 0
        for data, labels in loader:
            x_A = ltn.Variable("x_A", data[torch.nonzero(labels)])  # positive examples
            x_not_A = ltn.Variable("x_not_A",
                                   data[torch.nonzero(torch.logical_not(labels))])  # negative examples
            # mean_sat += SatAgg(
            #     Forall(x_A, A(x_A)),
            #     Forall(x_not_A, Not(A(x_not_A)))
            # )
            # Define an empty list to store evaluated arguments
            args_list = []

            # Loop through each formula in the list and evaluate it
            for formula in formulas:
                args_list.append(eval(formula))

            # Create a SatAgg instance with the evaluated arguments
            mean_sat += SatAgg(*args_list)

            # formulas_str = [
            #     "Forall(x_A, A(x_A))",
            #     "Forall(x_not_A, Not(A(x_not_A)))"
            # ]

            # mean_sat = 0

            # for formula_str in formulas_str:
            #     context = {
            #         'Forall': Forall,
            #         'Not': Not,
            #         'A': A  # Assume 'A' is some predicate defined elsewhere in your code
                    
            #     }
            #     exec(f"formula_obj = {formula_str}", context, context)
            #     mean_sat += SatAgg(context['formula_obj'])

            # print("Mean Satisfaction Level:", mean_sat)

        mean_sat /= len(loader)
        return mean_sat


    # it computes the overall accuracy of the predictions of the trained model using the given data loader
    # (train or test)
    def compute_accuracy(loader):
        mean_accuracy = 0.0
        for data, labels in loader:
            predictions = A.model(data).detach().numpy()
            predictions = np.where(predictions > 0.5, 1., 0.).flatten()
            mean_accuracy += accuracy_score(labels, predictions)

        return mean_accuracy / len(loader)


    # create train and test loader, 50 points each
    # batch size is 64, meaning there is only one batch for epoch
    train_loader = DataLoader(dataset[:50], labels_dataset[:50], 64, True)
    test_loader = DataLoader(dataset[50:], labels_dataset[50:], 64, False)

    optimizer = torch.optim.Adam(A.parameters(), lr=0.001)

    # training of the predicate A using a loss containing the satisfaction level of the knowledge base
    # the objective it to maximize the satisfaction level of the knowledge base
    for epoch in range(1000):
        train_loss = 0.0
        for batch_idx, (data, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            # we ground the variables with current batch data
            x_A = ltn.Variable("x_A", data[torch.nonzero(labels)])  # positive examples
            x_not_A = ltn.Variable("x_not_A", data[torch.nonzero(torch.logical_not(labels))])  # negative examples
            # sat_agg = SatAgg(
            #     Forall(x_A, A(x_A)),
            #     Forall(x_not_A, Not(A(x_not_A)))
            # )
            # Define an empty list to store evaluated arguments
            args_list = []

            # Loop through each formula in the list and evaluate it
            for formula in formulas:
                args_list.append(eval(formula))

            # Create a SatAgg instance with the evaluated arguments
            sat_agg = SatAgg(*args_list)
            loss = 1. - sat_agg
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss = train_loss / len(train_loader)

        # we print metrics every 20 epochs of training
        if epoch % 20 == 0:
            print(" epoch %d | loss %.4f | Train Sat %.3f | Test Sat %.3f | Train Acc %.3f | Test Acc %.3f"
                  % (epoch, train_loss, compute_sat_level(train_loader), compute_sat_level(test_loader),
                     compute_accuracy(train_loader), compute_accuracy(test_loader)))





    parser = TPTPParser()
    # string = "cnf(name, axiom, a | b)."
    # structure = parser.parse(string)
    # 'Formula' is in the list of elements returned by the parse function

    # string = "cnf(name, axiom, a | b).cnf(name, axiom, d | e)."
    # string = "cnf(a1, axiom, a | b).cnf(a1, axiom, ~a).cnf(a2, negated_conjecture, b)."
    # string = "fof(mortal_humans, axiom, ![X]: (human(X) => mortal(X)))."
    # string = "fof(some_unicorn, conjecture, ?[X]: unicorn(X))."
    # string = "fof(mortal_humans, axiom, ![X]: ((cube(X) & small(X)) => ?[Y]: leftOf(X,Y)))."
    # Forall(x, Implies(And(cube(x), small(x)), Exists(y, leftof(x, y))))

    # string = "fof(mortal_humans, axiom, ![X]: ((cube(X) & small(X)) => ?[Y]: leftOf(X,Y)))."
    # string = "cnf(a1, axiom, a | b).cnf(a1, axiom, ~a).cnf(a2, negated_conjecture, b)."

    # string = "fof(all_A, axiom, ![X_A]: (A(X_A))).fof(all_not_A, axiom, ![X_not_A]: (~A(X_not_A)))."

    # string = "fof(mortal_humans, axiom, ![X]: ((cube(X) & small(X)) => ?[Y]: leftOf(X,Y))).fof(mortal_humans, axiom, ![X]: ((cube(X) & small(X)) => ?[Y]: leftOf(X,Y)))."
    # string = "fof(all_A, axiom, ![X_A]: ((a(X_A)))).fof(all_not_A, axiom, ![X_not_A]: ((~a(X_not_A))))."
    # string = "fof(all, axiom, ![X]: a(X))."

    # Forall(x_A, A(x_A)),
    # Forall(x_not_A, Not(A(x_not_A)))



    # for line in parser.stream_lines(string):
    #     structure = parser.parse(line)
    #     if structure:
    #         ltn_formula = convert_to_ltn(structure[0].formula)
    #         print(ltn_formula)
            # print(structure[0].formula)

    # Example usage:

    # variable_mapping = {
    #     1: "grad_student",
    #     2: "has_supervisor",
    #     3: "take_course",
    #     4: "scholarship_candidate"
    # }
    # dimacs_formatter = DIMACSFormatter()
    # dimacs_formatter.map_variable_names(variable_mapping)

    # Adding some clauses - for example purposes
    # dimacs_formatter.add_clause([-3, -2, 4])  # scholarship_candidate :- take_course, has_superviser.
    # dimacs_formatter.add_clause([-1, 2])  # has_superviser :- grad_student.
    # dimacs_formatter.add_clause([-1, 3])  # take_course :- grad_student.

    # dimacs_string = dimacs_formatter.generate_dimacs()
    # print(dimacs_string)
    # kbann_rules = dimacs_to_kbann_rules(variable_mapping)
    # print(kbann_rules)

    # CURRENT_DIRECTOR = os.getcwd()

    # Initial parameters
    # training_epochs = 2000

    # atoms_to_add = ["complete_course", "freshman", "sent_application", "high_gpa"]
    # Load training data
    # data_file_path = os.path.join(CURRENT_DIRECTOR, "Datasets", "student.txt")
    # X, y, feature_names = load_data(data_file_path)
    # Call main with the use_dimacs flag set to True
    # main(
    #     X,
    #     y,
    #     feature_names,
    #     training_epochs,
    #     atoms_to_add=atoms_to_add,
    #     use_dimacs=True,
    #     mapping = variable_mapping
    # )

