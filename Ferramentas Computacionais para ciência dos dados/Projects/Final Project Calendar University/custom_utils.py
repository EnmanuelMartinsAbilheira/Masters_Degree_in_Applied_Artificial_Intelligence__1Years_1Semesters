"""
    Course Scheduling System
    Authors:
        - Enmanuel Martins (16430)
        - Pedro Ferreira (17029)
        
"""

from sqlalchemy.sql import func
from flask import session, flash
import json
from models import db, ClassData, GeneralData, Classroom, Teacher, ClassroomUnavailable


class Utils():

    """
        Class containing custom utility methods for performing some operations and logic,
        fundamental for the flask app.
        
    """
    def __init__(self) -> None:
        pass
    

    def check_subj_name_uniqueness(self, input_dict):
        """ Method to check subject name uniqueness in the input dictionary. """
        
        output_dict = {}
        existing_subjects = []

        for class_name, subjects in input_dict.items():
            new_subjects = {}

            for subject_name, sub_data in subjects.items():
                unique_subject_name = self.add_suffix_to_sub_name(subject_name, existing_subjects)
                new_subjects[unique_subject_name] = sub_data

            output_dict[class_name] = new_subjects

        return output_dict


    def add_suffix_to_sub_name(self, subject_name, existing_subjects):
        """ Method for appending a suffix (_int), starting at 2, to duplicate subject names. """
        
        original_name = subject_name
        suffix = 2

        if subject_name in existing_subjects:
            subject_name = f"{original_name}_{suffix}"
            suffix += 1

        existing_subjects.append(subject_name)
        return subject_name


    def update_subjects_match(self, teachers):
        """ 
            Method to U«update the subjects in strict assignments and preferences to match the available subjects for each teacher.
            Iterates through the provided dictionary of teachers and their information. For each teacher, it updates
            the subject in their strict assignments and preferences to match the available subjects associated with that teacher.

        """
        
        for teacher, info in teachers.items():
            subjects = info['subjects']
            # Update strict_assign
            for i, assign in enumerate(info['strict_assign']):
                day, time, subject = assign
                for sub in subjects:
                    if sub.split('_')[0] == subject:
                        teachers[teacher]['strict_assign'][i] = (day, time, sub)
            # Update preferences
            for i, preference in enumerate(info['preferences']):
                day, time, subject, weight = preference
                for sub in subjects:
                    if sub.split('_')[0] == subject:
                        teachers[teacher]['preferences'][i] = (day, time, sub, weight)
                        
        return teachers
    
    
    def get_subjects_list(self, teacher_name):
        """ Method to get the subjects lectured by a teacher from the db model/table Teachers. """
        
        teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
        if teacher:
            return [subject.strip() for subject in teacher.subjects.split(',')]
        else:
            return []
       

    def populate_subject_choices(self, form, teacher_name):
        """ 
            Method to populate the choices for the 'subject' field in the form
            with all the subjects taught by the given teacher.
            
        """

        subjects_list = self.get_subjects_list(teacher_name)
        for subject in subjects_list:
            form.subject.choices.append(subject)
    
    
    def remove_unavailable_tuples(self, strict_tuple_list, unavailable_classrooms):
        """ 
            Method to remove tuples from strict_tuple_list if their first two elements
            match any key in unavailable_classrooms.
            
        """
        
        # Get all unavailable time slots from the values of unavailable_classrooms dict
        unavailable_times = [time for times_list in unavailable_classrooms.values() for time in times_list]

        # Remove tuples from strict_tuple_list if their first two elements match any unavailable times
        return [strict_tuple for strict_tuple in strict_tuple_list
                if (strict_tuple[0], strict_tuple[1]) not in unavailable_times]
            
            
    def read_courses_data(self):
        """ Method to get courses info present in models ClassData and GeneralData. """
        
        class_data_records = ClassData.query.all()

        # Aux dictionary to store the course/classes data
        aux_dict = {}
        # Store general data by each course
        general_course_data = {}
        
        for record in class_data_records:
            class_name = record.class_name
            subject_name = record.subject_name

            # Check if course_name exists in the dict, if not initialize it
            if class_name not in aux_dict:
                aux_dict[class_name] = {}

            # Add subject data to the dict
            aux_dict[class_name][subject_name] = {
                'teacher': record.teacher,
                'enrolled_students': record.enrolled_students,
                'min_days_classes': record.min_days_classes,
                'max_days_classes': record.max_days_classes,
                'min_classes_per_week': record.min_classes_per_week,
                'max_classes_per_week': record.max_classes_per_week,
            }
            aux_dict = self.check_subj_name_uniqueness(aux_dict)
            # Individual dicts that will be passed to ScheduleSolver class
            teacher_subject = {}
            enrolled_students = {}
            min_days_classes = {}
            max_days_classes = {}
            min_classes_per_week = {}
            max_classes_per_week = {}

            classes = {name: list(class_data.keys()) for name, class_data in aux_dict.items()}
            
            for _, value in aux_dict.items():
                # Iterate over the subjects for each key
                for subject, data in value.items():
                    # Add subjects to the respective lists
                    # Iterate over the subjects for each key
                    teacher = data['teacher']
                    if teacher not in teacher_subject:
                        teacher_subject[teacher] = [subject]
                    else:
                        teacher_subject[teacher].append(subject)
                    enrolled_students[subject] = data['enrolled_students']
                    min_days_classes[subject] = data['min_days_classes']
                    max_days_classes[subject] = data['max_days_classes']
                    min_classes_per_week[subject] = data['min_classes_per_week']
                    max_classes_per_week[subject] = data['max_classes_per_week']

            # Convert teacher_subject values to tuples
            teacher_subject = {key: tuple(value) for key, value in teacher_subject.items()}
            
            # Get general data for the course
            general_data_entry = GeneralData.query.filter_by(course_name=class_name).first()
            # General data (referent to a Course -> all classes/subjects)
            if general_data_entry:
                min_blocks_per_day = general_data_entry.min_blocks_per_day
                max_blocks_per_day = general_data_entry.max_blocks_per_day
                min_days_of_classes = general_data_entry.min_days_of_classes
                max_days_of_classes = general_data_entry.max_days_of_classes
                max_blocks_per_week = general_data_entry.max_blocks_per_week
                min_blocks_per_period = general_data_entry.min_blocks_per_period
                
            # Check if course_name exists in the dict, if not initialize it
            if class_name not in aux_dict:
                general_course_data[class_name] = {}
            # Add general data to the dict
            general_course_data[class_name] = {
                'min_blocks_per_day': min_blocks_per_day,
                'max_blocks_per_day': max_blocks_per_day,
                'min_days_of_classes': min_days_of_classes,
                'max_days_of_classes': max_days_of_classes,
                'max_blocks_per_week': max_blocks_per_week,
                'min_blocks_per_period': min_blocks_per_period
            } 
            
        # Pack the dicts on a list
        dicts_list = [classes, teacher_subject, enrolled_students, min_days_classes, max_days_classes,
                    min_classes_per_week, max_classes_per_week, general_course_data]
        
        return dicts_list


    def get_teachers(self):
        """ Method to get/update teachers from the db model/table Teachers. """
        
        # Query the database
        teachers_data = db.session.query(ClassData.teacher, 
                                        db.func.group_concat(ClassData.subject_name)).group_by(ClassData.teacher).all()

        # Get the list of existing teachers and subjects
        existing_teachers = Teacher.query.all()

        # Create a dictionary to store existing teacher objects by name
        existing_teachers_dict = {teacher.teacher_name: teacher for teacher in existing_teachers}
        
        new_teacher_names = {teacher_name for teacher_name, _ in teachers_data}
        # Find teachers to delete
        teachers_to_delete = [teacher for teacher in existing_teachers if teacher.teacher_name not in new_teacher_names]

        # Delete teachers that are not present in ClassData model
        for teacher in teachers_to_delete:
            db.session.delete(teacher)

        # Iterate over the new data from ClassData 
        for teacher_name, subjects_str in teachers_data:
            # Check if the teacher already exists in the database
            if teacher_name in existing_teachers_dict:
                # Update the subjects field for the existing teacher
                existing_teacher = existing_teachers_dict[teacher_name]
                existing_teacher.subjects = subjects_str.replace(',', ', ')
                # Clear strict_assignment and preferences if subjects are not in subjects_str
                subjects = set(subjects_str.split(','))
                
                
                # Deserialize the string into a Python object (list of lists)
                # For strict assignments
                strict_assignment_list = json.loads(existing_teacher.strict_assignment)

                # Filter out sublists that contain subjects not in the subjects set
                filtered_subjects_from_assignments = [sub_list for sub_list in strict_assignment_list
                                                    if sub_list[2] in subjects]
                # Serialize the filtered list back to a string
                existing_teacher.strict_assignment = json.dumps(filtered_subjects_from_assignments)
                        
                # Deserialize the string into a Python object (list of lists)
                # For the preferences
                pref_list = json.loads(existing_teacher.preferences)
                # Filter out sublists that contain subjects not in the subjects set
                filtered_subjects_from_pref = [sub_list for sub_list in pref_list
                                                    if sub_list[2] in subjects]
                # Serialize the filtered list back to a string
                existing_teacher.preferences = json.dumps(filtered_subjects_from_pref)
                        
                
            else:
                # If the teacher doesn't exist, create a new one with both teacher_name and subjects
                new_teacher = Teacher(teacher_name=teacher_name, subjects=subjects_str.replace(',', ', '))
                db.session.add(new_teacher)

        # Commit the changes to the database
        db.session.commit()
    
    
    def read_classrooms_data(self):
        """ 
            Method to get classrooms from the db model/table Classrooms
            and populate  unavailable classrooms dict with unavailable slots.
            
        """
        
        classroom_records = Classroom.query.all()
        classroom_capacities = {}
        classrooms = []
        for record in classroom_records:
            classroom_name = record.classroom_name
            classroom_capacity = record.classroom_capacity
            classrooms.append(classroom_name)
            if classroom_name not in classroom_capacities:
                classroom_capacities[classroom_name] = classroom_capacity

        classroom_unavailable_records = ClassroomUnavailable.query.all()
        # Initialize dict
        unavailable_classrooms = {classroom: [] for classroom in classrooms}
        # Populate unavailable classrooms dictionary with unavailable slots
        for classroom in classrooms:
            for unavailable_record in classroom_unavailable_records:
                classroom_name = classroom
                unavailable_classrooms[classroom_name].append((unavailable_record.day, unavailable_record.hour))
                
        return [classrooms, classroom_capacities, unavailable_classrooms]


    def check_classrooms(self):
        """ Method to check if there are Classrooms available before solving. """
        
        if not Classroom.query.first():
            flash('No classrooms available. Add Classrooms before attempting to use the solver!', 'warning')
            return False
        return True


    def check_courses(self):
        """ Method to check if there are Courses available before solving. """
         
        if not ClassData.query.first():
            flash('No courses available. Add Courses before attempting to use the solver!', 'warning')
            return False
        return True


    def check_general_data(self):
        """ Method to check if the Courses have general data associated before solving. """
        
        unique_class_names = db.session.query(ClassData.class_name).distinct().all()
        for class_name in unique_class_names:
            has_entry = GeneralData.query.filter_by(course_name=class_name[0]).first()
            if not has_entry:
                flash(f'The course {class_name[0]} has no general data associated!\nPlease insert some data',
                      'warning')
                # session['course_name'] = class_name
                return False
        return True


    def check_classroom_count(self):
        """ Method to check if there are sufficient classrooms for the number of courses before solving. """
        
        course_count = db.session.query(ClassData.class_name).distinct().count()
        classroom_count = Classroom.query.count()
        if course_count > classroom_count:
            flash(f'There are insufficient classrooms (Total = {classroom_count}) for the number of courses ({course_count})!\n \
                Please add some more classrooms!', 'warning')
            return False
        return True
    

    def check_largest_classroom_capacity(self):
        """ Method to check if the subject on db with most students enrolled can be placed on any of the classrooms. """
        
        largest_enrollment = db.session.query(func.coalesce(func.max(ClassData.enrolled_students), 0)).scalar()
        largest_classroom = db.session.query(func.coalesce(func.max(Classroom.classroom_capacity), 0)).scalar()
        
        if largest_enrollment > largest_classroom:
            flash(f'There are no classrooms that can hold the largest value of enrolled students present \
                on the database: ({largest_enrollment})!\n Please add a classroom with that capacity!', 'warning')
            return False
        return True
    
    
    def check_conflict_teacher_assign(self):
        """ Check for conflicts between strict assignments of different teachers and unavailable classroom slots.
    
            This method ensures that strict assignments made by different teachers do not conflict with each other
            and also verifies that these assignments do not conflict with unavailable classroom slots.
            
        """
        
        teachers_data = Teacher.query.all()
        all_strict_slots = set()
        (_, _, unavailable_classrooms) = self.read_classrooms_data()
    
        # Get all unavailable time slots from the values of unavailable_classrooms dict
        unavailable_times = [time for times_list in unavailable_classrooms.values() for time in times_list]
        unique_slots = list(set(unavailable_times))
     
        for teacher in teachers_data:
            unavailability = json.loads(teacher.unavailability)
            strict_assignment = json.loads(teacher.strict_assignment)
            strict_tuple_list = [tuple(strict) for strict in strict_assignment]
            for unavail_slot in unavailability:
                day, time = unavail_slot[:2]
                
                # Check if any sublist in strict_assignment matches the day and time
                for strict_slot in strict_assignment:
                    if strict_slot[:2] == [day, time]:
                        flash(f'Detected strict assignment conflicts with unavailability in teacher:\
                            {teacher.teacher_name}', 'warning')
                        return False
                    
            # Check if any strict tuple matches any unavailable classroom times
            for strict_tuple in strict_tuple_list:
                if (strict_tuple[0], strict_tuple[1]) in unique_slots:
                    flash(f'Strict assignment conflicts with unavailable classroom slots in teacher: {teacher.teacher_name}. '
                        f'The classroom unavailable slot that is in conflict is: '
                        f'day: {strict_tuple[0]} and hour: {strict_tuple[1]}', 'warning')
                    return False
                
            # Update the set of all strict assignment slots
            all_strict_slots.update(tuple(slot[:2]) for slot in strict_assignment)
        
        # Check conflicts between strict assignments of different teachers
        for teacher in teachers_data:
            strict_assignment = json.loads(teacher.strict_assignment)
            
            for strict_slot in strict_assignment:
                day, time = strict_slot[:2] 
                
                # Check if this strict assignment slot matches any slot from other teachers
                for other_teacher in teachers_data:
                    if other_teacher != teacher:  # Skip comparing with the same teacher
                        other_strict_assignment = json.loads(other_teacher.strict_assignment)
                        if (day, time) in set(tuple(slot[:2]) for slot in other_strict_assignment):
                            flash(f'Detected conflict between strict assignments of teacher: {teacher.teacher_name} and \
                                teacher: {other_teacher.teacher_name}', 'warning')
                            return False 
                        
        return True 