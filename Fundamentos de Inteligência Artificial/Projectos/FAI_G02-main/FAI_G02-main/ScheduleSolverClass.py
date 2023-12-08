from constraint import Problem, BacktrackingSolver                       
from itertools import islice


class ScheduleSolver:
    """
    Class created to encapsulate the process of solving a Schedule-like csp problem

    Example:

    >>> solver_backtracking = ScheduleSolver(subjects=Lesi + Leec, teachers=teachers,
    solver=BacktrackingSolver(forwardcheck=True))
    >>> solver_backtracking.add_variables(Lesi + Leec)
    >>> ....
    """
    # Instance Methods
    def __init__(self, subjects, teachers, subset_size=4, solver=BacktrackingSolver()):
        """
        Constructor for the ScheduleSolver class

        Args:
            subjects (list): List of the variables to add to the problem
            teachers (dict): Dictionary mapping teachers to the correspondent classes they lecture
            subset_size (int, optional): Size of subsets. Defaults to 4.
            solver (Solver, optional): Algorithm/Solver to use. Defaults to BacktrackingSolver().
        """
        self.problem = Problem(solver)
        self.subjects = subjects
        self.teachers = teachers
        self.subset_size = subset_size
        self.my_set = set(range(1, 21))
    
    
    def add_variables(self, variables):
        """
        Method to add variables to the problem

        Args:
            variables (list): List of the variables to add to the problem
        """
        for var in variables:
            self.problem.addVariable(var, list(self.my_set))


    def add_constraints(self, *constraints):
        """
        Method to add constraints to the problem
        
        Args:
            constraints (list[tuple]): List of the tuple constraints to add to the problem
        """
        for constraint in constraints:
            self.problem.addConstraint(*constraint)      
      
        
    def solve(self, from_iterator = False, max_solutions = 10):
        """
        Method to solve the problem

        Args:
            from_iterator (bool, optional): Check if the return should be an iterator. Defaults to False.
            max_solutions (int, optional): Max number of solutions on the iterator. Defaults to 10.

        Returns:
            solution (Union[iterator, dict]): Returns a dictionary or an iterator(dicts)
        """
        if from_iterator:
            solutions_iter = islice(self.problem.getSolutionIter(), max_solutions)
            return solutions_iter
        
        solution = self.problem.getSolution()  
        return solution
    
    
    # Custom Constraint Methods
    @staticmethod
    def distinct_val(n):
        """
        Constraint method to check n distinct values for the variables passed

        Args:
            n (int): Number of distinct values
            
        Returns:
            A function that is True when the count of distinct values is <= n, False otherwise
        """
        def distval(*values):
            return len(set(values)) >= n
        distval.__name__ = f"distval({n})"
        return distval
    
    
    @staticmethod
    def atleast_per_week(min_assignments, *values):
        """
        Constraint method to check if a class has at least a min number of classes
        per week

        Args:
            variable_list (list): List of vars
            min_assignments (int): Number of minimum assignments

        Returns:
            bool: True when the total assignments are >= min_assignments, False otherwise
        """
        total_assignments = sum(1 for value in set(values) if value is not None)
        return total_assignments >= min_assignments
    
    
    @staticmethod
    def atmost_per_week(max_assignments, *values):
        """
        Constraint method to check if a class has at most a max number of classes
        per week

        Args:
            variable_list (list): List of vars
            max_assignments (int): Number of maximum assignments

        Returns:
            bool: True when the total assignments are <= max_assignments, False otherwise
        """
        total_assignments = sum(1 for value in set(values) if value is not None)
        return total_assignments <= max_assignments
    
    # This old version is currently not being used, but works as the new one
    @staticmethod
    def atmost4_days_per_week_oldversion(*values):
        """
        Constraint method to check if a class has at most 4 days of classes
        in a week
        
        Returns:
            bool: True when the assigned_ranges_count are <= 4, False otherwise
        """
        ranges = [(i, i + 3) for i in range(1, 21, 4)]  # Each tuple represents 1 day (Monday to Friday)
        assigned_ranges_count = sum(any(start <= value <= end for value in set(values)) for start, end in ranges)
        return assigned_ranges_count <= 4
    
    @staticmethod
    def atmost4_days_per_week(*values, target_values):
        """
        Constraint method to check if a class has at most 4 days of classes
        in a week

        Args:
            target_values (list[set]): List with all the target_subsets

        Returns:
            bool: True when the count_trues is <= 4, False otherwise
        """
        # Remember True=1, False=0
        # Any returns bool accordingly with the expression (if there is at least one element)
        # count_trues counts the trues
        count_trues = sum(any(v in target_set for v in set(values)) for target_set in target_values)
        return count_trues <= 4
    
    @staticmethod
    def atmost_3lessons_per_day(*values, target_values):
        """
        Constraint method to check if a class has at most 3 lessons
        per day

        Args:
            target_values (set): Set representing the values correspondent to each day.
            Example: {1,2,3,4} corresponds to Monday

        Returns:
            bool: True when the count of values in target_values are <= 3, False otherwise
        """
        count = sum(1 for v in set(values) if v in target_values) 
        return count <= 3
    
    
    @staticmethod
    def atleast_2lessons_per_day(*values, target_values):
        """
        Constraint method to check if a class has at least 2 lessons
        per day, if in that day has lessons

        Args:
            target_values (set): Set representing the values correspondent to each day.

        Returns:
            bool: True when the count of values in target_values are > 1 or there are no values assigned
            to that day, False otherwise
        """
        day_values = set(values) & set(target_values)

        # Check if there are no values on that day or if there is return count > 1
        return not day_values or len(day_values) > 1
    
    @staticmethod
    def atmost_1lessonTorTp_perday(*values, target_values):
        """
        Constraint method to check if a lesson T or TP (example 'D1_T' and 'D1_TP') has at most 1 lesson
        per day. 'D1_T' and 'D1_TP' must be assigned to different days.

        Args:
            target_values (set): Set representing the values correspondent to each day.
            Example: {1,2,3,4} corresponds to Monday
            
        Returns:
            bool: True when the count of values in target_values are < 2, False otherwise
        """
        count = sum(1 for v in set(values) if v in target_values)
        return count < 2  
    
    
    @staticmethod
    def minimize_absolute_difference(*values):
        """
        Constraint method to minimize the absolute difference (gaps) on the values assigned
        We made this very flexible (with a "relaxed" threshold range), because if not the solver
        would take too much time to achieve all the other constraints.
        In some cases if the threshold was too "tight" the solver woud not give a solution at all.
        
        Returns:
            bool: True when all differences between consecutive values are <= threshold, False otherwise
            We defined the threshold to start with value = 1 and can be incremented to int((len(sorted_values)-1)
        """
        unique_elements = set(values)
        unique_elements_list = list(unique_elements)
        # Elements sorted (Asc) so no need for abs
        sorted_values = sorted(unique_elements_list)
        threshold = 1
        while threshold <= int((len(sorted_values)-1)):
            differences = [sorted_values[i+1] - sorted_values[i] for i in range(len(sorted_values)-1)]
            if all(diff <= threshold for diff in differences):
                return True
            threshold += 1
        return False