import torch
from sklearn.metrics import accuracy_score
import numpy as np
import ltn

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
Not = ltn.Connective(ltn.fuzzy_ops.NotStandard())
Forall = ltn.Quantifier(ltn.fuzzy_ops.AggregPMeanError(p=2), quantifier="f")
SatAgg = ltn.fuzzy_ops.SatAgg()
dataset = torch.rand((100, 2))
labels_dataset = torch.sum(torch.square(dataset - torch.tensor([.5, .5])), dim=1) < .09

def compute_sat_level(loader, formulas):
    mean_sat = 0
    for data, labels in loader:
        x_A = ltn.Variable("x_A", data[torch.nonzero(labels)])  # positive examples
        x_not_A = ltn.Variable("x_not_A", data[torch.nonzero(torch.logical_not(labels))])  # negative examples

        # Create the context dictionary correctly, including the variables
        args_list = []
        for formula in formulas:
            args_list.append(eval(formula))

        # Aggregate satisfaction levels
        mean_sat += SatAgg(*args_list)

    mean_sat /= len(loader)
    return mean_sat


def compute_accuracy(loader):
    mean_accuracy = 0.0
    for data, labels in loader:
        predictions = A.model(data).detach().numpy()
        predictions = np.where(predictions > 0.5, 1, 0).flatten()
        mean_accuracy += accuracy_score(labels, predictions)
    return mean_accuracy / len(loader)

class DataLoader(object):
    def __init__(self, data, labels, batch_size=1, shuffle=True):
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

def main(
    formulas,
    training_epochs
    ):

    train_loader = DataLoader(dataset[:50], labels_dataset[:50], 64, True)
    test_loader = DataLoader(dataset[50:], labels_dataset[50:], 64, False)
    optimizer = torch.optim.Adam(A.parameters(), lr=0.001)

    for epoch in range(training_epochs):
        train_loss = 0.0
        for _, (data, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            x_A = ltn.Variable("x_A", data[torch.nonzero(labels)])
            x_not_A = ltn.Variable("x_not_A", data[torch.nonzero(torch.logical_not(labels))])
            args_list = []
            for formula in formulas:
                args_list.append(eval(formula))
            sat_agg = SatAgg(*args_list)
            loss = 1. - sat_agg
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)
        if epoch % 20 == 0:
            print("epoch %d | loss %.4f | Train Sat %.3f | Test Sat %.3f | Train Acc %.3f | Test Acc %.3f"
                    % (epoch, train_loss, compute_sat_level(train_loader, formulas),
                        compute_sat_level(test_loader, formulas),
                        compute_accuracy(train_loader), compute_accuracy(test_loader)))
