import numpy as np
from tabulate import tabulate
from fractions import Fraction

class LPSolver:
    def __init__(self):
        self.A = None
        self.b = None
        self.c = None
        self.tableau = None
        self.basic_vars = None
        self.non_basic_vars = None
        self.problem_type = "max"
        self.artificial_vars = []
        self.artificial_indices = []
        self.M = None
        self.num_constraints = 0
        self.num_variables = 0
        self.use_fractions = True
        self.verbose = True
        self.epsilon = 1e-12
        self.original_vars = []
        self.slack_vars = []
        self.art_vars = []

    def set_objective(self, coefficients, problem_type="max"):
        self.c = np.array(coefficients, dtype=float)
        self.num_variables = len(coefficients)
        self.problem_type = problem_type.lower()
        if self.problem_type == "min":
            self.c = -self.c
        self.original_vars = list(range(self.num_variables))

    def add_constraints(self, A, b, inequalities):
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        self.num_constraints = len(b)
        if self.A is None:
            self.A = A
            self.b = b
            self.inequalities = inequalities
        else:
            self.A = np.vstack((self.A, A))
            self.b = np.concatenate((self.b, b))
            self.inequalities.extend(inequalities)

    def _calculate_big_m(self):
        max_obj = np.max(np.abs(self.c)) if len(self.c) > 0 else 1
        max_constr = np.max(np.abs(self.A)) if self.A is not None and self.A.size > 0 else 1
        max_rhs = np.max(np.abs(self.b)) if self.b is not None and self.b.size > 0 else 1
        max_value = max(max_obj, max_constr, max_rhs)
        M = 1000 * max_value
        M = max(1000, M)
        if self.verbose:
            print(f"Calculated Big M value: {M}")
        return M

    def _convert_to_standard_form(self):
        if self.M is None:
            self.M = self._calculate_big_m()
        
        num_slack_surplus = 0
        num_artificial = 0
        
        for inequality in self.inequalities:
            if inequality == "<=":
                num_slack_surplus += 1
            elif inequality == ">=":
                num_slack_surplus += 1
                num_artificial += 1
            elif inequality == "=":
                num_artificial += 1

        new_cols = self.num_variables + num_slack_surplus + num_artificial
        new_A = np.zeros((self.num_constraints, new_cols))
        new_A[:, :self.num_variables] = self.A
        new_c = np.zeros(new_cols)
        new_c[:self.num_variables] = self.c

        self.basic_vars = [None] * self.num_constraints
        self.non_basic_vars = []
        slack_idx = self.num_variables
        artificial_idx = self.num_variables + num_slack_surplus

        for i, inequality in enumerate(self.inequalities):
            if inequality == "<=":
                new_A[i, slack_idx] = 1
                self.basic_vars[i] = slack_idx
                self.slack_vars.append(slack_idx)
                slack_idx += 1
            elif inequality == ">=":
                new_A[i, slack_idx] = -1
                self.slack_vars.append(slack_idx)
                slack_idx += 1
                new_A[i, artificial_idx] = 1
                self.basic_vars[i] = artificial_idx
                self.artificial_vars.append(artificial_idx)
                self.artificial_indices.append(artificial_idx)
                self.art_vars.append(artificial_idx)
                new_c[artificial_idx] = -self.M
                artificial_idx += 1
            elif inequality == "=":
                new_A[i, artificial_idx] = 1
                self.basic_vars[i] = artificial_idx
                self.artificial_vars.append(artificial_idx)
                self.artificial_indices.append(artificial_idx)
                self.art_vars.append(artificial_idx)
                new_c[artificial_idx] = -self.M
                artificial_idx += 1

        # Normalize basic variables
        for i in range(self.num_constraints):
            basic_var = self.basic_vars[i]
            if basic_var is not None:
                if new_A[i, basic_var] != 1:
                    new_A[i, :] = new_A[i, :] / new_A[i, basic_var]
                for j in range(self.num_constraints):
                    if j != i and new_A[j, basic_var] != 0:
                        new_A[j, :] = new_A[j, :] - new_A[j, basic_var] * new_A[i, :]

        self.non_basic_vars = list(set(range(new_cols)) - set(self.basic_vars))
        self.A = new_A
        self.c = new_c

        # Handle negative RHS
        for i in range(len(self.b)):
            if self.b[i] < 0:
                self.A[i] = -self.A[i]
                self.b[i] = -self.b[i]
                if self.inequalities[i] == ">=":
                    self.inequalities[i] = "<="
                elif self.inequalities[i] == "<=":
                    self.inequalities[i] = ">="

    def _create_initial_tableau(self):
        rows = self.num_constraints + 1
        cols = self.A.shape[1] + 1
        self.tableau = np.zeros((rows, cols))
        
        self.tableau[:self.num_constraints, :self.A.shape[1]] = self.A
        self.tableau[:self.num_constraints, -1] = self.b
        self.tableau[self.num_constraints, :self.A.shape[1]] = -self.c

        # Apply Big M method for artificial variables
        if len(self.artificial_vars) > 0:
            if self.verbose:
                print("\nApplying Big M method for artificial variables")
            for art_idx in self.artificial_indices:
                for j in range(self.num_constraints):
                    if art_idx == self.basic_vars[j]:
                        coeff = self.tableau[self.num_constraints, art_idx]
                        self.tableau[self.num_constraints, :] += (-coeff) * self.tableau[j, :]
                        break

    def _display_tableau(self, iteration=None):
        if not self.verbose:
            return
            
        tableau = self.tableau.copy()
        rows, cols = tableau.shape
        
        # Reorganize columns
        orig_idx = self.original_vars
        slack_idx = self.slack_vars
        art_idx = self.art_vars
        rhs_idx = [cols - 1]
        new_col_order = orig_idx + slack_idx + art_idx + rhs_idx
        
        reorg_tableau = np.zeros((rows, len(new_col_order)))
        for i, old_idx in enumerate(new_col_order):
            reorg_tableau[:, i] = tableau[:, old_idx]

        # Create headers
        headers = []
        for i in orig_idx:
            headers.append(f"x{i+1}")
        for i in slack_idx:
            headers.append(f"x{i+1}")
        for i, idx in enumerate(art_idx):
            headers.append(f"a{i+1}")
        headers.append("LD")

        # Create row labels
        base_labels = []
        for i in range(rows - 1):
            basic_idx = self.basic_vars[i]
            if basic_idx in self.original_vars:
                base_labels.append(f"x{basic_idx+1}")
            elif basic_idx in self.slack_vars:
                base_labels.append(f"x{basic_idx+1}")
            elif basic_idx in self.art_vars:
                base_labels.append(f"a{self.art_vars.index(basic_idx)+1}")
        base_labels.append("z")

        if self.use_fractions:
            str_tableau = np.zeros_like(reorg_tableau, dtype=object)
            for i in range(rows):
                for j in range(len(new_col_order)):
                    frac = Fraction(reorg_tableau[i, j]).limit_denominator()
                    if frac.denominator == 1:
                        str_tableau[i, j] = str(frac.numerator)
                    else:
                        str_tableau[i, j] = f"{frac.numerator}/{frac.denominator}"
            display_tableau = tabulate(str_tableau, headers=headers, showindex=base_labels, tablefmt="grid")
        else:
            display_tableau = tabulate(reorg_tableau, headers=headers, showindex=base_labels, tablefmt="grid")

        title = f"Iteration {iteration}" if iteration is not None else "Initial Tableau"
        print(f"\n{title}")
        print(display_tableau)

    def _select_pivot_column(self):
        objective_row = self.tableau[self.num_constraints, :-1]
        min_idx = np.argmin(objective_row)
        if objective_row[min_idx] >= -self.epsilon:
            return -1
        return min_idx

    def _select_pivot_row(self, pivot_col):
        ratios = []
        for i in range(self.num_constraints):
            if self.tableau[i, pivot_col] <= self.epsilon:
                ratios.append(float('inf'))
            else:
                ratios.append(self.tableau[i, -1] / self.tableau[i, pivot_col])
        
        if all(r == float('inf') for r in ratios):
            return -1
        
        min_ratio = float('inf')
        min_idx = -1
        for i, ratio in enumerate(ratios):
            if 0 <= ratio < min_ratio:
                min_ratio = ratio
                min_idx = i
        return min_idx

    def _pivot(self, pivot_row, pivot_col):
        pivot_element = self.tableau[pivot_row, pivot_col]
        
        if self.verbose:
            print(f"  R{pivot_row+1} -> R{pivot_row+1} / {pivot_element:.4f}")
        
        self.tableau[pivot_row] = self.tableau[pivot_row] / pivot_element
        
        for i in range(self.tableau.shape[0]):
            if i != pivot_row:
                factor = self.tableau[i, pivot_col]
                if self.verbose:
                    print(f"  R{i+1} -> R{i+1} - {factor:.4f} * R{pivot_row+1}")
                self.tableau[i] = self.tableau[i] - factor * self.tableau[pivot_row]

        # Update basic variables
        leaving_var = self.basic_vars[pivot_row]
        entering_var = pivot_col
        self.basic_vars[pivot_row] = entering_var
        
        if leaving_var in self.artificial_vars:
            self.artificial_vars.remove(leaving_var)
        
        self.non_basic_vars = list(set(range(self.tableau.shape[1] - 1)) - set(self.basic_vars))

    def solve(self):
        self._convert_to_standard_form()
        self._create_initial_tableau()
        self._display_tableau(iteration=0)
        
        iteration = 1
        max_iterations = 100
        
        while iteration <= max_iterations:
            pivot_col = self._select_pivot_column()
            if pivot_col == -1:
                print("\nOptimal solution found!")
                break
            
            pivot_row = self._select_pivot_row(pivot_col)
            if pivot_row == -1:
                print("\nProblem is unbounded!")
                break
            
            if self.verbose:
                print(f"\nPivot: Row {pivot_row+1}, Column {pivot_col+1}")
            
            self._pivot(pivot_row, pivot_col)
            self._display_tableau(iteration=iteration)
            iteration += 1
        
        if iteration > max_iterations:
            print("\nWarning: Maximum iterations reached. Solution may not be optimal.")

        # Extract solution
        solution = np.zeros(self.num_variables)
        for i, var in enumerate(self.basic_vars):
            if var < self.num_variables:
                solution[var] = self.tableau[i, -1]

        # Check for artificial variables in solution
        has_artificial_in_solution = False
        for i, var in enumerate(self.basic_vars):
            if var in self.artificial_indices and abs(self.tableau[i, -1]) > self.epsilon:
                has_artificial_in_solution = True
                break

        if has_artificial_in_solution:
            print("\nWarning: Artificial variable remains in final solution with non-zero value.")
            print("This indicates the problem is infeasible.")

        objective_value = self.tableau[self.num_constraints, -1]
        if self.problem_type == "min":
            objective_value = -objective_value

        return solution, objective_value


def parse_fraction(s):
    if '/' in s:
        num, denom = s.split('/')
        return float(num) / float(denom)
    else:
        return float(s)


def parse_input():
    solver = LPSolver()
    
    print("\n===== LINEAR PROGRAMMING SOLVER =====")
    
    # Get problem type
    print("Enter problem type (max/min):")
    while True:
        problem_type = input().strip().lower()
        if problem_type in ("max", "min"):
            break
        else:
            print("Error: Enter 'max' or 'min'.")
    
    # Get number of variables
    print("\nEnter the number of decision variables:")
    while True:
        try:
            num_vars = int(input())
            if num_vars > 0:
                break
            else:
                print("Error: Enter a positive integer.")
        except ValueError:
            print("Error: Enter a valid integer.")
    
    # Get objective coefficients
    print(f"\nEnter {num_vars} objective function coefficients (space-separated, decimals or fractions like 1/3):")
    while True:
        c_input = input().split()
        if len(c_input) != num_vars:
            print(f"Error: Enter exactly {num_vars} coefficients.")
            continue
        try:
            c = [parse_fraction(coef) for coef in c_input]
            break
        except ValueError:
            print("Error: Enter valid numbers or fractions.")
    
    solver.set_objective(c, problem_type)
    
    # Get number of constraints
    print("\nEnter the number of constraints:")
    while True:
        try:
            num_constraints = int(input())
            if num_constraints > 0:
                break
            else:
                print("Error: Enter a positive integer.")
        except ValueError:
            print("Error: Enter a valid integer.")
    
    # Get constraints
    A = []
    b = []
    inequalities = []
    
    print("\nFor each constraint, enter coefficients, inequality type (<=, >=, =), and RHS value:")
    print("Example: 2 3 <= 10  (means 2x₁ + 3x₂ <= 10)")
    print("You can use decimal values (3.14) or fractions (1/3)")
    
    for i in range(num_constraints):
        print(f"\nConstraint {i+1}:")
        while True:
            constraint = input().strip()
            parts = constraint.split()
            
            if len(parts) < 3:
                print("Error: Invalid format. Enter coefficients, inequality (<=, >=, =), and RHS.")
                continue
            
            ineq = parts[-2]
            if ineq not in ("<=", ">=", "="):
                print("Error: Inequality must be <=, >=, or =.")
                continue
            
            try:
                coeffs = [parse_fraction(x) for x in parts[:-2]]
                rhs = parse_fraction(parts[-1])
                break
            except ValueError:
                print("Error: Enter valid numbers or fractions for coefficients and RHS.")
        
        if len(coeffs) < num_vars:
            coeffs.extend([0] * (num_vars - len(coeffs)))
        
        A.append(coeffs)
        b.append(rhs)
        inequalities.append(ineq)
    
    solver.add_constraints(A, b, inequalities)
    return solver


def main():
    solver = parse_input()
    
    # Ask about fraction display
    while True:
        use_fractions = input("\nDisplay results as fractions? (y/n): ").strip().lower()
        if use_fractions in ("y", "n"):
            use_fractions = use_fractions == "y"
            break
        else:
            print("Error: Please enter 'y' or 'n'.")
    
    solver.use_fractions = use_fractions
    
    print("\n===== SOLVING PROBLEM =====")
    solution, objective_value = solver.solve()
    
    print("\n===== SOLUTION =====")
    for i, val in enumerate(solution):
        if use_fractions:
            frac = Fraction(val).limit_denominator()
            if frac.denominator == 1:
                print(f"x{i+1} = {frac.numerator}")
            else:
                print(f"x{i+1} = {frac.numerator}/{frac.denominator}")
        else:
            print(f"x{i+1} = {val:.4f}")
    
    if use_fractions:
        obj_frac = Fraction(objective_value).limit_denominator()
        if obj_frac.denominator == 1:
            print(f"Optimal value = {obj_frac.numerator}")
        else:
            print(f"Optimal value = {obj_frac.numerator}/{obj_frac.denominator}")
    else:
        print(f"Optimal value = {objective_value:.4f}")


if __name__ == "__main__":
    main()