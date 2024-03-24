class DIMACSFormatter:
    def __init__(self, filepath=None):
        self.variables = set()
        self.clauses = []
        if filepath:
            self.load_from_file(filepath)

    def add_clause(self, clause):
        """
        Adds a clause to the DIMACS problem.
        Clauses are given as lists of integers, where each integer represents a variable.
        Positive integers indicate the variable, and negative integers indicate the negation of the variable.
        """
        for var in clause:
            self.variables.add(abs(var))
        self.clauses.append(clause)

    def generate_dimacs(self, filename="example.dimacs"):
        """
        Generates the DIMACS string for the current set of clauses and variables and saves it to a file.
        """
        header = f"p cnf {len(self.variables)} {len(self.clauses)}\n"
        clauses_str = "\n".join(" ".join(map(str, clause)) + " 0" for clause in self.clauses)
        dimacs_string = header + clauses_str

        with open(filename, 'w') as file:
            file.write(dimacs_string)

        print(f"Saved DIMACS to {filename}")
        return dimacs_string

    def load_from_file(self, filepath):
        """
        Loads clauses from a DIMACS format file.
        """
        with open(filepath, 'r') as file:
            for line in file:
                if line.startswith('p') or line.startswith('c'):
                    # Skip problem line and comments
                    continue
                # Convert DIMACS line to a clause and add it
                clause = [int(x) for x in line.strip().split()[:-1]]  # Exclude the trailing 0
                self.add_clause(clause)

    def reset(self):
        """
        Resets the formatter to allow for a new problem to be defined.
        """
        self.variables.clear()
        self.clauses.clear()
