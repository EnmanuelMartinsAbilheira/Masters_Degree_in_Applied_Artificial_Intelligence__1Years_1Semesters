"""
    Course Scheduling System
    Authors:
        - Enmanuel Martins (16430)
        - Pedro Ferreira (17029)
        
"""

from class_scheduler import CourseScheduler
import sys
import time


class SubjectsMismatchError(Exception):
    """Exception raised when Subjects mismatch in the different dictionaries. """
    
    def __init__(self):
        self.message = "Subjects mismatch in the different dictionaries!\nCheck the subject names entered!!!"
        super().__init__(self.message)


# Custom exception for course names mismatch
class CoursesMismatchError(Exception):
    """Exception raised when Course names mismatch in the different dictionaries."""
    
    def __init__(self):
        self.message = "Course names mismatch in the different dictionaries!\nCheck the course names entered!!!"
        super().__init__(self.message)


class NonNegativeError(Exception):
    """Exception raised when one or more values are negative. """

    def __init__(self, value):
        self.message = f"The values for the weights can not be negative!\nFound a negative value for a weight: {value}."
        super().__init__(self.message)


def check_subject_uniqueness_values(input_dict):
    """Function to check subject name uniqueness in the dict values. """
    
    global_subject_counts = {}
    output_dict = {}

    for key, subjects in input_dict.items():
        updated_subjects = []
        for subject in subjects:
            if subject not in global_subject_counts:
                global_subject_counts[subject] = 1
                updated_subjects.append(subject)
            else:
                count = global_subject_counts[subject]
                updated_subject = f"{subject}_{count + 1}"
                updated_subjects.append(updated_subject)
                global_subject_counts[subject] += 1

        output_dict[key] = tuple(updated_subjects)

    return output_dict


def check_if_subjects_match(classes_dict, teacher_subj_dict, dicts_list):
    """ Function to check if the subjects match between the different dicts. """
    
    # Get the set of values from the first dictionary (classes)
    all_classes_subjects = set(subject for subjects in classes_dict.values() for subject in subjects)
    # Get the set of values from the second dictionary (teacher_subject)
    all_teacher_subjects = set(subject for subjects in teacher_subj_dict.values() for subject in subjects)
    
    # Other dicts
    # Check if the subjects (classes and teacher_subject) match for all other dictionaries keys
    for d in dicts_list:
        if set(d.keys()) != all_classes_subjects or set(d.keys()) != all_teacher_subjects:
            raise SubjectsMismatchError()
    

def check_if_coursesname_match(dict1, dict2):
    """ Function to check if the course names (keys) match between two dicts. """
    
    # Get the sets of keys (course_names) for both dictionaries
    cname_set1 = {key.lower() for key in dict1.keys()}
    cname_set2 = {key.lower() for key in dict2.keys()}

    # Check if the sets of keys match
    if cname_set1 != cname_set2:
        raise CoursesMismatchError()


def check_non_negative_weights(*values):
    """ Function to check if negative weights are present """
    
    for value in values:
        if value < 0:
            raise NonNegativeError(value=value)
    return True


# Days and hours (2hour blocks for classes)
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
hours = ['9-11', '11-13', '14-16', '16-18']

# Solver to use
solver = 'gurobi'

# Attention on how to introduce the subject names.
# This situation doesnt occur on main_flask_UI.py
# Particularly in the dicts students_enrolled, min_days_classes_subject, max_days_classes_subject,
# max_blocks_per_week_subject and min_blocks_per_week_subject.
# Dicts dont allow duplicate keys:
# To differentiate use 'Math': value, 'Math2': value, ...  it will be printed/saved 'Math' and 'Math2' on schedules. 
# Alternatively you can use 'Math': value, 'Math_2': value, ...., the ScheduleSolver class, then removes the
# suffix: _somecharacters and it prints/saves 'Math_2' as 'Math'

# Subjects, classrooms, and capacities
classes = {'Lesi': ['Math', 'Physics', 'Chemistry', 'Programming', 'Algorithms'],
           'Leec': ['Math', 'Algebra', 'IA', 'Electronics', 'Robotics']}
classes = check_subject_uniqueness_values(classes)

# Note:
# In this hard coded main, we dont check the number of classrooms vs courses.
# Neither the classroom capacities vs number of enrolled students of each subject.
# That is done on the main Ui (flask).
# So before solving check if the number of classrooms and its capacities are enough to handle the courses/subjects.

classrooms = ['Classroom1', 'Classroom2', 'Classroom3', 'Classroom4']
classroom_capacities = {'Classroom1': 25, 'Classroom2': 25, 'Classroom3': 30, 'Classroom4': 30}

# Dictionary to map teachers to subjects
teacher_subject = {
    'teacher1': ('Math', 'Math'), # on the hard-coded main we need to repeat the subject with same name on the tuple.
    'teacher2': ('Physics', 'Algebra'),
    'teacher3': ('Chemistry', 'IA'),
    'teacher4': ('Programming', 'Electronics', 'Algorithms', 'Robotics')
}
teacher_subject = check_subject_uniqueness_values(teacher_subject)

    
# Teachers and their assignment details
teachers = {
    'teacher1': {'subject': teacher_subject['teacher1'], 'unavailability': [('Mon', '14-16'), ('Fri', '11-13')],
                 'preferences': [('Mon', '9-11', teacher_subject['teacher1'][0], 4),
                                 ('Tue', '11-13', teacher_subject['teacher1'][0], 4)]},
    
    'teacher2': {'subject': teacher_subject['teacher2'], 'unavailability': [('Tue', '9-11'), ('Thu', '14-16')],
                 'strict_assign': [('Wed', '9-11', teacher_subject['teacher2'][0])]},
    
    'teacher3': {'subject': teacher_subject['teacher3'], 'unavailability': [('Wed', '9-11'), ('Thu', '14-16')],
                 'preferences': [('Thu', '9-11', teacher_subject['teacher3'][0], 3),
                                 ('Wed', '9-11', teacher_subject['teacher3'][0], 4)]},
    
    'teacher4': {'subject': teacher_subject['teacher4'], 'unavailability': [('Tue', '14-16')]},
}


# Dictionary to represent unavailable classrooms for each (day, hour)
# Pass as a list of tuples (1 or more slots of unavailability of classrooms)
unavailable_classrooms = {
'Classroom1': [('Mon', '14-16')],
'Classroom2': [('Mon', '14-16'), ('Wed', '9-11')],
'Classroom3': [('Mon', '14-16')],
'Classroom4': [('Mon', '14-16')],
'Classroom5': [('Mon', '14-16')],
}


# ------------------------------------Parameters for individual Subjects--------------------------------------
# All classes take 2 hours -> 1 block/slot

# Number of students enrolled in each subject
students_enrolled = {'Math': 25, 'Math_2': 25, 'Physics': 30, 'Algebra': 30 , 'Chemistry': 20, 'IA': 20, \
    'Programming': 20, 'Electronics': 20, 'Algorithms': 30, 'Robotics': 30}


# Maximum / Minimum number of days that the specific subject has classes
min_days_classes_subject = {'Math': 2, 'Physics': 1, 'Chemistry': 1, 'Programming': 1, 'Algorithms': 1, 'Math_2': 1, \
    'Algebra': 1, 'IA': 1, 'Electronics': 1, 'Robotics': 1}
max_days_classes_subject = {'Math': 3, 'Physics': 2, 'Chemistry': 2, 'Programming': 2, 'Algorithms': 2, 'Math_2': 2, \
    'Algebra': 2, 'IA': 2, 'Electronics': 2, 'Robotics': 2}

# Maximum / Minimum blocks (2-hour classes) per week for each Subject
max_blocks_per_week_subject = {'Math': 3, 'Physics': 2, 'Chemistry': 2, 'Programming': 2, 'Algorithms': 2, 'Math_2': 2, \
    'Algebra': 2, 'IA': 2, 'Electronics': 2, 'Robotics': 2}
min_blocks_per_week_subject = {'Math': 2, 'Physics': 1, 'Chemistry': 1, 'Programming': 1, 'Algorithms': 1, 'Math_2': 2, \
    'Algebra': 1, 'IA': 1, 'Electronics': 1, 'Robotics': 1}


# ------------------------------------Parameters for each Course/Class---------------------------------------

# General (all subjects) time related parameters for each course
general_course_data = {'Lesi': {'min_blocks_per_day': 2, 'max_blocks_per_day': 3, 'max_blocks_per_week': 12, \
    'max_days_of_classes': 5, 'min_days_of_classes': 4, 'min_blocks_per_period': 1},
                       
                       'Leec': {'min_blocks_per_day': 2, 'max_blocks_per_day': 3, 'max_blocks_per_week': 12, \
    'max_days_of_classes': 5, 'min_days_of_classes': 4, 'min_blocks_per_period': 1}}


# ----------------------------------Parameter across all Courses---------------------------------------------
# Max classes (2 hour blocks) of a teacher per day (all courses)
max_blocks_per_day_teacher = 3

    
# -----------------------------------------------------------------------------------------------------------
# Pack all (Subject + Course) time related params on a time_ranges list
time_ranges = [min_days_classes_subject, max_days_classes_subject, min_blocks_per_week_subject,
               max_blocks_per_week_subject, max_blocks_per_day_teacher, general_course_data]

# Weights for the objective (applied for each Course/Class)

# Penaltie weight for dispersion of classes across different days.
# Penalize classes dispersion between != days
# Purpose: Minimize the number of days of classes (attempts to schedule classes on as few days as possible).
penalty_weight_dispersion = 2.0


# Penaltie weight for gaps in the schedule within the same day.
# Purpose: Minimize the gaps of classes in a day (attempts to schedule classes closer together on the same day).
gap_penalty_weight = 1.0

# Consecutive days
# Penaltie weight for gaps between consecutive days in the schedule.
# Purpose: Maximize the number of consecutive days with classes (attempts to schedule classes on consecutive days).
# As a consequence, the solver will prioritize empty days (no classes) at the extremities (Mon/Fri).
# You can disable this, by setting the value to 0.0.
gap_between_days = 1.0 

# Pack the weights on a list
weights = [penalty_weight_dispersion, gap_penalty_weight, gap_between_days]


# Before solving we have to:
try:
    # Check if the subjects for the different dictionaries match
    check_if_subjects_match(classes_dict=classes, teacher_subj_dict=teacher_subject,
                            dicts_list=[students_enrolled, min_days_classes_subject, max_days_classes_subject,
                                        max_blocks_per_week_subject, min_blocks_per_week_subject])
    
    # Check if the course name matches between the keys of the dicts classes and general_course_data
    check_if_coursesname_match(classes, general_course_data)
    
    # Check if there are negative values for weights
    check_non_negative_weights(penalty_weight_dispersion, gap_penalty_weight, gap_between_days)
    
except SubjectsMismatchError as sme:
    print(f"Caught SubjectsMismatchError: {sme.message}")
    sys.exit(1)  # Exit with a non-zero status code
except CoursesMismatchError as cme:
    print(f"Caught KeysMismatchError: {cme.message}")
    sys.exit(1)
except NonNegativeError as nne:
    print(f"Caught NonNegativeError: {nne.message}")
    sys.exit(1)
except ValueError as val_e:
    print(f"Caught ValueError: {val_e}")
    sys.exit(1)


# Instanciate and solve
# Schedules using this main hard coded will be saved on the folder Schedules(Main_HardCoded)
# Using src_flask=False
scheduler = CourseScheduler(classes, days, hours, teacher_subject, teachers, unavailable_classrooms,
                        classroom_capacities, students_enrolled, time_ranges, weights, src_flask=False)


start_time = time.time()
solver_results = scheduler.solve_schedule(mysolver=solver)
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Elapsed Time: {elapsed_time} seconds")