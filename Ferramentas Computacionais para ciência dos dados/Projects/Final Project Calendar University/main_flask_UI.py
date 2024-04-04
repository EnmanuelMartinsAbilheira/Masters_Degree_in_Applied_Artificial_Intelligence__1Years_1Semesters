"""
    Course Scheduling System
    Authors:
        - Enmanuel Martins (16430)
        - Pedro Ferreira (17029)
        
"""

from class_scheduler import CourseScheduler
from custom_utils import Utils
import time
import pandas as pd
import os
import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from flask import Flask, redirect, url_for, render_template, request, session, flash
from forms import (
    NumberClasses, GeneralDataForm, SubjectForm, FieldList, FormField,
    ClassroomForm, PreferencesForm, StrictAssignForm, UnavailableForm, ClassroomUnavailableForm
)
from models import db, ClassData, GeneralData, Classroom, Penalties, Teacher, ClassroomUnavailable
from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList
from wtforms.validators import DataRequired, Length



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
# Db saved to folder -> cur_dir/instance/site.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['WTF_CSRF_ENABLED'] = True
db.init_app(app)


# Routes

@app.route("/")
def home():
    """
        Route handler for the home page.
        This function retrieves counts for various tables from the database and renders the home page template with the counts.
        Counts include the number of courses, classrooms, and classroom unavailabilities.
        
    """
    
    # Get counts for various tables
    course_count = db.session.query(ClassData.class_name).distinct().count()
    classroom_count = Classroom.query.count()
    classroom_unavailability_count = ClassroomUnavailable.query.count()

    return render_template("home.html", course_count=course_count, classroom_count=classroom_count,
                           classroom_unavailability_count= classroom_unavailability_count)
    
    
@app.route("/add_course", methods=["POST", "GET"])
def add_course():
    """
        Route handler for adding a new course.
        This function handles both GET and POST requests. When a GET request is made, it renders the template with a form to
        add a new course. When a POST request is made (after form submission), it validates the form data. 
        
    """

    form = NumberClasses()

    if request.method == "POST" and form.validate_on_submit():
        
        course_name = form.course_name.data.title()
        n_subjects = form.n_subjects.data
        
        # Check if course_name already exists in the database
        if ClassData.query.filter_by(class_name=course_name).first():
            flash('Course name already exists. Please choose a different name.', 'error')
            return redirect(url_for('add_course'))
        
        session['course_name']  = course_name
        session['n_subjects'] = n_subjects

        # Redirect to another page with a form for each class
        return redirect(url_for('class_page'))

    return render_template("index.html", form=form)


@app.route('/edit_course_name', methods=['POST'])
def edit_course_name():
    """
        Route handler for editing a course name.
        This function handles POST requests. When a POST request is made (after form submission), it validates the form data,
        updating the course name in the models ClassData and GeneralData.
        
    """
    
    if request.method == 'POST':
        current_course_name = request.form.get('current_course_name').title()
        new_course_name = request.form.get('new_course_name').title()
        # Retrieve all instances of ClassData with the specified class_name
        courses_to_edit = ClassData.query.filter_by(class_name=current_course_name).all()

        if courses_to_edit:
            # Update the course name for each matching instance
            for course in courses_to_edit:
                course.class_name = new_course_name

            # Update corresponding entry in GeneralData
            general_data_entry = GeneralData.query.filter_by(course_name=current_course_name).first()
            if general_data_entry:
                general_data_entry.course_name = new_course_name

            # Commit changes to the database
            db.session.commit()

            flash(f'Course name updated from {current_course_name} to {new_course_name} successfully!', 'success')
        else:
            flash(f'No courses found with course name "{current_course_name}". Nothing updated.', 'warning')

    # Redirect to the page where you display course details
    return redirect(url_for('get_classes'))


@app.route('/delete_course', methods=['GET', 'POST'])
def delete_course():
    """
        Route handler for deleting a course.
        This function handles both GET and POST requests. When a POST request is made (after form submission), it retrieves
        the input value from the form, checks if any course matches the input value in the database, and deletes all
        matching entries from the ClassData table. Additionally, it deletes the corresponding entry from the GeneralData
        table if it exists.
        
    """
    
    if request.method == 'POST':
        # Get the input value from the form
        confirmation_value = request.form.get('confirmation').title()

        # Check if the confirmation_value matches any class_name in the database
        matching_classes = ClassData.query.filter_by(class_name=confirmation_value).all()

        if matching_classes:
            # Delete all matching entries
            for matching_class in matching_classes:
                db.session.delete(matching_class)
                
            # Delete the corresponding entry in GeneralData
            general_data_entry = GeneralData.query.filter_by(course_name=confirmation_value).first()
            if general_data_entry:
                db.session.delete(general_data_entry)
                
            # Commit changes to the database
            db.session.commit()

            flash(f'Course with name "{confirmation_value}" deleted successfully!', 'success')
        else:
            flash(f'No courses found with the name "{confirmation_value}". Nothing deleted.', 'warning')

        return redirect(url_for('get_classes'))

    # If the request method is GET, simply render the template
    return render_template('classes.html')


@app.route('/edit_subject/<int:class_id>', methods=['GET', 'POST'])
def edit_subject(class_id):
    """ 
        Route handler for editing subject details.
        This function handles both GET and POST requests. When a GET request is made, it fetches the class data from the
        database based on the provided class ID and creates a `SubjectForm` pre-filled with the existing data for that class.
        When a POST request is made (after form submission), it updates the subject details based on the form data and commits
        the changes to the database.

    """
    # Fetch the class by ID from the database
    class_data = ClassData.query.get_or_404(class_id)
  
    # Create a SubjectForm for editing
    form = SubjectForm(obj=class_data)

    if request.method == 'POST' and form.validate_on_submit():
        # Update the subject details
        class_data.subject_name = form.sub_name.data.title()
        class_data.teacher = form.teacher.data.title()
        class_data.enrolled_students = form.enrolled_students.data
        class_data.min_days_classes = form.min_days_classes.data
        class_data.max_days_classes = form.max_days_classes.data
        class_data.min_classes_per_week = form.min_classes_per_week.data
        class_data.max_classes_per_week = form.max_classes_per_week.data

        # Commit changes to the database
        db.session.commit()
        return redirect(url_for('get_classes'))

    # Handle validation errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Validation error in {form[field].label.text}: {error}', "danger")
    return render_template('edit_subject.html', form=form, class_data=class_data, subject_name=class_data.subject_name)


@app.route('/delete_subject/<int:class_id>')
def delete_subject(class_id):
    """ 
        Route handler for deleting a subject from a course.
        This function retrieves the class data for the provided class ID from the database. It then checks the number of subjects
        associated with the same course. If deleting the subject would result in fewer than 4 subjects for the course, it flashes
        a warning message and redirects to the page displaying all classes. Otherwise, it deletes the class data from the
        database.
        
    """
    
    # Retrieve the class data by ID from the database
    class_data = ClassData.query.get_or_404(class_id)
    subject_name = class_data.subject_name
    course_name = class_data.class_name

    # Count the number of subjects for the course
    subjects_count = ClassData.query.filter_by(class_name=course_name).count()

    # Check if deleting the subject would result in fewer than 4 subjects
    if subjects_count <= 4:
        flash('Each course must have at least 4 subjects. Cannot delete this entry!', 'warning')
        return redirect(url_for('get_classes'))

    # Delete the class data
    db.session.delete(class_data)
    db.session.commit()

    flash(f'Subject {subject_name} deleted from Course {course_name} successfully!', 'success')

    return redirect(url_for('get_classes'))

    
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    """ 
        Route handler for adding a subject to a course.
        This function first retrieves the course name from the request arguments and checks if it would result in more than 7
        subjects for that course. If so, it flashes a warning message and redirects to the page displaying all classes.
        Otherwise, it checks if the provided course exists in the database. If not, it flashes a warning message and redirects
        to the page displaying all classes. If the request method is POST and the form validates, it creates a new instance of
        ClassData with the provided subject details.
        
    """
    
    course_name = request.args.get('course_name', '')
    if course_name:
        course_name = course_name.title()

    # Check if adding the subject would result in more than 6 subjects for that course
    subjects_count = ClassData.query.filter_by(class_name=course_name).count()
    if subjects_count >= 7:
        flash('Each course must have at most 7 subjects. Cannot add more subjects!', 'warning')
        return redirect(url_for('get_classes'))
    
    # Check of course exists
    matching_course = ClassData.query.filter_by(class_name=course_name).first()
    if not matching_course:
        flash(f'No Course {course_name} found. Cant add subject to non-existent Course!\n \
            Please add the course: {course_name} first', 'warning')
        return redirect(url_for('get_classes'))
    
    if request.method == 'POST':
        form = SubjectForm(request.form)

        if form.validate():
            # Check if a subject with the same name already exists for the course
            existing_subject = ClassData.query.filter_by(
                class_name=course_name,
                subject_name=form.sub_name.data.title()
            ).first()

            if existing_subject:
                flash(f"A subject with name '{form.sub_name.data.title()}' already exists for course '{course_name}'.",
                      'warning')
                return redirect(url_for('get_classes'))

            # Create a new instance of ClassData with the provided course name
            new_data = ClassData()

            # Retrieve subject details from the form
            new_data.class_name = course_name
            new_data.subject_name = form.sub_name.data.title()
            new_data.teacher = form.teacher.data.title()
            new_data.enrolled_students = form.enrolled_students.data
            new_data.min_days_classes = form.min_days_classes.data
            new_data.max_days_classes = form.max_days_classes.data
            new_data.min_classes_per_week = form.min_classes_per_week.data
            new_data.max_classes_per_week = form.max_classes_per_week.data

            # Add the new data to the session
            db.session.add(new_data)
            db.session.commit()

            flash(f"Subject added for course: {course_name}", 'success')
            return redirect(url_for('get_classes'))

        # If form validation fails, re-render the template with the form and course_name
        return render_template('add_subject.html', form=form, course_name=course_name)


@app.route("/class_page/", methods=["GET", "POST"])
def class_page():
    """ 
        Route handler for the page where classes are added for a course.
        This function renders a form for adding classes to a course. If the request method is POST and the form validates
        successfully, it iterates over the subject forms in the class form, creates new ClassData records with the provided
        subject details.
        If form validation fails, it iterates over the form errors and flashes validation errors.
        
    """

    course_name = session.get('course_name', 'default')
  
    class ClassForm(FlaskForm):
            class_name = StringField('Class Name', validators=[DataRequired(), Length(min=2, max=30)])
            subjects = FieldList(FormField(SubjectForm), min_entries=session.get('n_subjects', 5))
            
    class_form = ClassForm(class_name=course_name)
    
    if request.method == "POST" and class_form.validate_on_submit():
        
        for i, subject_form in enumerate(class_form.subjects.entries, start=1):
            # Create a new record in the database
            new_data = ClassData(
                class_name = course_name,
                subject_name = subject_form.sub_name.data.title(),
                teacher = subject_form.teacher.data.title(),
                enrolled_students = subject_form.enrolled_students.data,
                min_days_classes = subject_form.min_days_classes.data,
                max_days_classes = subject_form.max_days_classes.data,
                min_classes_per_week = subject_form.min_classes_per_week.data,
                max_classes_per_week = subject_form.max_classes_per_week.data
            )

            db.session.add(new_data)
        db.session.commit()  
  
        return redirect(url_for('general_data'))
    
    # Handle validation errors
    for field, errors in class_form.errors.items():
        # Remove empty dicts, because we have n_subjects
        errors = [error for error in errors if error]
        for error in errors:
            for key in error:
                flash(f'Validation error in {class_form[field].label.text}: {error[key][0]}', "danger")

    return render_template("form_template.html", class_form=class_form)


@app.route('/view_general_data')
def view_general_data():
    """ 
        Route handler for viewing general data.
        This function fetches all GeneralData objects from the database.
        
    """
    
    # Fetch all GeneralData objects from the database
    general_data = GeneralData.query.all()

    # Render the HTML template and pass the GeneralData objects to it
    return render_template('view_gendata.html', general_data=general_data)


@app.route('/edit_general_data/<int:id>', methods=['GET', 'POST'])
def edit_general_data(id):
    """
        Route handler for editing general data.
        This function fetches the GeneralData object with the given ID from the database, creates a GeneralDataForm instance, 
        populates it with the current data, and renders an HTML template for editing the data. 
        If the form is submitted with valid data, it updates the GeneralData object.

    """

    # Fetch the GeneralData object by ID from the database
    general_data = GeneralData.query.get_or_404(id)

    # Create a GeneralDataForm instance and populate it with the current data
    form = GeneralDataForm(obj=general_data)

    if form.validate_on_submit():
        # Update the GeneralData object with the form data
        form.populate_obj(general_data)
        db.session.commit()
        flash('General Data updated successfully!', 'success')
        return redirect(url_for('view_general_data'))
    
    # Handle validation errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Validation error in {form[field].label.text}: {error}', "danger")
            
    # Render the HTML template and pass the form and GeneralData object to it
    return render_template('general_data.html', form=form, general_data=general_data)


@app.route("/general_data", methods=["GET", "POST"])
def general_data():
    """ 
        Route handler for managing general data.
        This function handles both GET and POST requests for managing general data. 
        When a GET request is received, it renders a form for entering general data.
        When a POST request is received with valid form data, it saves the data to the GeneralData table.
        
    """
    
    form = GeneralDataForm()

    if request.method == "POST" and form.validate_on_submit():
        # Save the form data to the GeneralData table
        new_general_data = GeneralData(
            course_name=session.get('course_name', 'Default'),
            min_blocks_per_day=form.min_blocks_per_day.data,
            max_blocks_per_day=form.max_blocks_per_day.data,
            min_days_of_classes=form.min_days_of_classes.data,
            max_days_of_classes=form.max_days_of_classes.data,
            max_blocks_per_week=form.max_blocks_per_week.data,
            min_blocks_per_period=form.min_blocks_per_period.data,
        )

        db.session.add(new_general_data)
        db.session.commit()

        return redirect(url_for('home'))

    # Handle validation errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Validation error in {form[field].label.text}: {error}', "danger")

    return render_template("general_data.html", form=form)


@app.route('/classrooms', methods=['GET'])
def classrooms():
    """ 
        Route handler for viewing classrooms.
        This function fetches all Classroom objects from the database.
        
    """
    
    classrooms = db.session.query(Classroom).all()
    return render_template('classrooms.html', classrooms=classrooms)


@app.route('/classroom_form', methods=['GET', 'POST'])
def classroom_form():
    """ 
        Route handler for managing classroom data.
        This function handles both GET and POST requests for managing classroom data.
        When a GET request is received, it renders a form for adding or updating classroom information.
        When a POST request is received with valid form data, it either adds a new classroom or updates an existing one
        in the database.
        
    """
    
    form = ClassroomForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            if form.classroom_id.data:  # If classroom ID is present, it's an update
                classroom = db.session.get(Classroom, form.classroom_id.data)
                classroom.classroom_name = form.classroom_name.data.title()
                classroom.classroom_capacity = form.classroom_capacity.data
            else:  # If classroom ID is not present, it's an add
                classroom = Classroom(
                    classroom_name=form.classroom_name.data.title(),
                    classroom_capacity=form.classroom_capacity.data
                )

                db.session.add(classroom)

            db.session.commit()
            flash(f'Classroom {classroom.classroom_name} added successfully!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Error: Classroom with name {classroom.classroom_name} already exists.', 'danger')
        return redirect(url_for('classrooms'))  
    return render_template('classroom_form.html', form=form)


@app.route('/edit_classroom/<int:classroom_id>', methods=['GET', 'POST'])
def edit_classroom(classroom_id):
    """ 
        Route handler for editing classroom information.
        This function handles both GET and POST requests for editing classroom information.
        When a GET request is received, it fetches the existing classroom data from the database and populates the 
        ClassroomForm with that data.
        When a POST request is received with valid form data, it updates the corresponding classroom entry in the
        database with the new information.

    """
    
    classroom = db.session.get(Classroom, classroom_id)
    form = ClassroomForm(
        classroom_id=classroom.id,
        classroom_name=classroom.classroom_name,
        classroom_capacity=classroom.classroom_capacity
    )

    if request.method == 'POST' and form.validate_on_submit():
        # Update the classroom with the form data
        classroom.classroom_name = form.classroom_name.data.capitalize()
        classroom.classroom_capacity = form.classroom_capacity.data
        db.session.commit()

        flash('Classroom updated successfully!', 'success')
        return redirect(url_for('classrooms'))

    return render_template('classroom_form.html', form=form)


@app.route('/delete_classroom/<int:classroom_id>')
def delete_classroom(classroom_id):
    """ 
        Route handler for deleting a classroom.
        This function receives a classroom ID as a parameter and attempts to delete the corresponding classroom entry
        from the database.

    """
    
    classroom = db.session.get(Classroom, classroom_id)
    if classroom:
        db.session.delete(classroom)
        db.session.commit()
        flash(f'Classroom deleted successfully!', 'success')

    return redirect(url_for('classrooms'))


@app.route('/classes', methods=['GET'])
def get_classes():
    """ 
        Route handler for Course/Classes data.
        This function fetches all ClassData objects from the database.
        
    """
    
    # Retrieve all instances of ClassData from the database
    classes = ClassData.query.order_by(ClassData.class_name).all()

    # Render a template to display the classes
    return render_template('classes.html', classes=classes)


@app.route("/view_penalties")
def view_penalties():
    """ 
        Route handler for viewing penalties.
        This function fetches all Penalties objects (only exists one) from the database.
        If there are no objects it create by one with default values.
        
    """
    
    penalties_instance = Penalties.get_or_create()
    return render_template('view_penalties.html', penalties=penalties_instance)


@app.route("/edit_penalties", methods=['GET', 'POST'])
def edit_penalties():
    """ 
        Route handler for editing penalties information.
        This function handles both GET and POST requests for editing penalties information.
        When a GET request is received, it fetches the existing penaltie data from the database and populates the 
        form with that data.
        When a POST request is received with valid form data, it updates the corresponding penaltie entry in the
        database with the new information.

    """
    
    # Retrieve or create the Penalties record
    penalties_instance = Penalties.get_or_create()

    if request.method == 'POST':
        try:
            # Update the values based on the form data
            penalties_instance.dispersion_different_days = float(request.form['dispersion_different_days'])
            penalties_instance.gaps_in_a_day = float(request.form['gaps_in_a_day'])
            penalties_instance.gaps_between_days = float(request.form['gaps_between_days'])

            db.session.commit()

            flash('Penalties updated successfully!', 'success')
            return redirect(url_for('view_penalties'))
        
        except ValueError:
            flash('Invalid input. Please enter valid numbers.', 'danger')

    return render_template('edit_penalties.html', penalties=penalties_instance)
    
    
@app.route('/add_strictassign_form/<string:teacher_name>', methods=['GET'])
def add_strictassign_form(teacher_name):
    """ 
        Route handler for rendering the form to add a strict assignment for a teacher.
        This function receives the name of the teacher for whom the strict assignment is being added as a parameter.
        It initializes a StrictAssignForm and populates the subject choices for the form based on the subjects
        taught by the teacher.

    """

    form = StrictAssignForm()
    utils.populate_subject_choices(form, teacher_name)
  
    return render_template('add_strictassign_page.html', form=form, teacher_name=teacher_name)


@app.route('/add_unavailable_form/<string:teacher_name>', methods=['GET'])
def add_unavailable_form(teacher_name):
    """ 
        Route handler for rendering the form to add a unavailable slot for a teacher.
        This function receives the name of the teacher for whom the unavailable slot is being added.
        It initializes a UnavailableForm.

    """
    form = UnavailableForm()
    return render_template('add_unavailable_page.html', form=form, teacher_name=teacher_name)


@app.route('/add_preferences_form/<string:teacher_name>', methods=['GET'])
def add_preferences_form(teacher_name):
    """ 
        Route handler for rendering the form to add a preference for a teacher.
        This function receives the name of the teacher for whom the preference is being added as a parameter.
        It initializes a PreferencesForm and populates the subject choices for the form based on the subjects
        taught by the teacher.

    """
    
    form = PreferencesForm()
    utils.populate_subject_choices(form, teacher_name)
    
    return render_template('add_preferences_page.html', form=form, teacher_name=teacher_name)


@app.route('/add_unavailable/<string:teacher_name>', methods=['POST'])
def add_unavailable(teacher_name):
    """ 
        Route handler for adding a unavailable slot for a teacher.
        If the form data is valid, it retrieves the teacher from the database, updates the teacher's unavailable slot
        details by adding the new unavailable slot, and commits the changes to the database.

    """
    
    form = UnavailableForm(request.form)
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    if form.validate_on_submit():
        
        unavailable_str = teacher.unavailability
        # Convert the string to a Python list
        unavailable_list = json.loads(unavailable_str)
        # Create a tuple from the form data
        unavailable_tuple = (form.day.data, form.hour.data)
        # Append the new unavailable slot tuple to the list
        unavailable_list.append(unavailable_tuple)

        # Convert the list back to a JSON string
        updated_unavailable_str = json.dumps(unavailable_list)
        # Update the teacher's unavailability in the database
        teacher.unavailability = updated_unavailable_str
        db.session.add(teacher)
        db.session.commit()
        
        flash('Unavailability added successfully', 'success')
        utils.get_teachers()
        return redirect(url_for('teachers_subjects')) 

    flash('Something went wrong in the add process!!!', 'error')
  
    return redirect(url_for('add_unavailable_form', teacher_name=teacher_name))


@app.route('/add_strictassign/<string:teacher_name>', methods=['POST'])
def add_strictassign(teacher_name):
    """ 
        Route handler for adding a strict assignment for a teacher.
        If the form data is valid, it retrieves the teacher from the database, updates the teacher's strict assignment
        details by adding the new strict assignment, and commits the changes to the database.

    """

    form = StrictAssignForm(request.form)
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    utils.populate_subject_choices(form, teacher_name)
    
    if form.validate_on_submit():
        
        strictassign_str = teacher.strict_assignment

        # Convert the string to a Python list / Deserialize
        strictassign_list = json.loads(strictassign_str)
        # Create a tuple from the form data
        strict_tuple = (form.day.data, form.hour.data, form.subject.data)
        
        # Append the new strict assignment tuple to the list
        strictassign_list.append(strict_tuple)

        # Convert the list back to a JSON string
        updated_strict_str = json.dumps(strictassign_list)

        # Update the teacher's strict assignments in the database
        teacher.strict_assignment = updated_strict_str
        db.session.commit()
        
        flash('Strict Assignment added successfully', 'success')
        utils.get_teachers()
        return redirect(url_for('teachers_subjects')) 

    flash('Something went wrong in the add process!!!', 'error')
  
    return redirect(url_for('add_strictassign_form', teacher_name=teacher_name))

   
@app.route('/add_preferences/<string:teacher_name>', methods=['POST'])
def add_preferences(teacher_name):
    """ 
        Route handler for adding a preference for a teacher.
        If the form data is valid, it retrieves the teacher from the database, updates the teacher's preferences
        details by adding the new preferencet, and commits the changes to the database.

    """
    
    form = PreferencesForm(request.form)
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    if teacher:
        
        utils.populate_subject_choices(form, teacher_name)
        
        if form.validate_on_submit():
    
            preferences_str = teacher.preferences

            # Convert the string to a Python list
            preferences_list = json.loads(preferences_str)
            # Create a tuple from the form data
            preference_tuple = (form.day.data, form.hour.data, form.subject.data, form.weight.data)
            
            # Append the new preference tuple to the list
            preferences_list.append(preference_tuple)

            # Convert the list back to a JSON string
            updated_preferences_str = json.dumps(preferences_list)

            # Update the teacher's preferences in the database
            teacher.preferences = updated_preferences_str
            db.session.commit()
            
            flash('Preferences added successfully', 'success')
            utils.get_teachers()
            return redirect(url_for('teachers_subjects')) 

        flash('Form validation failed', 'error')
    else:
        flash('Teacher not found', 'error')

    return redirect(url_for('add_preferences_form', teacher_name=teacher_name))  
    

@app.route('/del_unavailability/<string:teacher_name>', methods=['POST'])
def del_unavailability(teacher_name):
    """
        Route handler for deleting unavailability settings for a teacher.
        If the teacher is found, their unavailability settings are set to an empty list, indicating no unavailability.
        The changes are then committed to the database, and a success flash message is displayed.

    """

    # Find the teacher in the database
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    if teacher:
        # Set to unavailability to an empty list
        teacher.unavailability = '[]'
        db.session.commit()
        flash('Unavailability deleted successfully', 'success')
    else:
        flash('Teacher not found', 'error')
    return redirect(url_for('teachers_subjects'))


@app.route('/del_preferences/<string:teacher_name>', methods=['POST'])
def del_preferences(teacher_name):
    """
        Route handler for deleting preferences settings for a teacher.
        If the teacher is found, their preference settings are set to an empty list, indicating no preferences.
        The changes are then committed to the database, and a success flash message is displayed.

    """
    
    # Find the teacher in the database
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    if teacher:
        # Set preferences to an empty list
        teacher.preferences = '[]'
        db.session.commit()
        flash('Preferences deleted successfully', 'success')
    else:
        flash('Teacher not found', 'error')
    return redirect(url_for('teachers_subjects'))


@app.route('/del_strict/<string:teacher_name>', methods=['POST'])
def del_strict(teacher_name):
    """
        Route handler for deleting strict assignment settings for a teacher.
        If the teacher is found, their strict assignment settings are set to an empty list, indicating no strict assignment.
        The changes are then committed to the database, and a success flash message is displayed.

    """
    
    # Find the teacher in the database
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    if teacher:
        # Set strict assignments to an empty list
        teacher.strict_assignment = '[]'
        db.session.commit()
        flash('Strict assign. deleted successfully', 'success')
    else:
        flash('Teacher not found', 'error')
    return redirect(url_for('teachers_subjects'))


@app.route('/teachers_subjects')
def teachers_subjects():
    """ 
        Route handler for displaying information about teachers and their subjects.
        This function retrieves data about teachers from the database, including their subjects, unavailability settings,
        strict assignments, and preferences. It then formats this data for rendering on the 'teachers.html' template.
        
    """

    # Get teachers
    utils.get_teachers()
    # Query the database for Teacher instances
    teachers_data = Teacher.query.all()
    # Format the data for rendering
    full_teachers_data = []
    for teacher in teachers_data:
        unavailability = json.loads(teacher.unavailability)
        strict_assignment = json.loads(teacher.strict_assignment)
        preferences = json.loads(teacher.preferences)
        full_teachers_data.append((
            teacher.teacher_name,
            teacher.subjects,
            unavailability,
            strict_assignment,
            preferences
        ))
                                
    return render_template('teachers.html', teachers_data=full_teachers_data)


@app.route('/add_classroom_unavailability', methods=['GET', 'POST'])
def add_classroom_unavailability():
    """ 
        Route handler for adding classroom unavailability.
        This route allows users to add unavailability slots for classrooms. If the form data provided is valid,
        a new entry for classroom unavailability is added to the database. 

    """
    
    form = ClassroomUnavailableForm()
    if form.validate_on_submit():
        classroom_unavailability = ClassroomUnavailable(day=form.day.data, hour=form.hour.data)
        db.session.add(classroom_unavailability)
        db.session.commit()
        flash('Classroom unavailability added successfully', 'success')
        return redirect(url_for('classroom_unavailability'))
    return render_template('add_classroom_unavailability.html', form=form)


@app.route('/delete_classroom_unavailability/<int:id>', methods=['POST'])
def delete_classroom_unavailability(id):
    """
        Route handler for deleting classroom unavailability.
        This route allows users to delete a specific entry for classroom unavailability from the database.

    """
    
    classroom_unavailability = ClassroomUnavailable.query.get_or_404(id)
    db.session.delete(classroom_unavailability)
    db.session.commit()
    flash('Classroom unavailability deleted successfully', 'success')
    return redirect(url_for('classroom_unavailability'))


@app.route('/edit_classroom_unavailability/<int:id>', methods=['GET', 'POST'])
def edit_classroom_unavailability(id):
    """ 
        Route handler for editing classroom unavailability.
        This route allows users to edit an existing entry for classroom unavailability.

    """
    
    classroom_unavailability = ClassroomUnavailable.query.get_or_404(id)
    form = ClassroomUnavailableForm(obj=classroom_unavailability)
    if form.validate_on_submit():
        form.populate_obj(classroom_unavailability)
        db.session.commit()
        flash('Classroom unavailability updated successfully', 'success')
        return redirect(url_for('classroom_unavailability'))
    return render_template('edit_classroom_unavailability.html', form=form, classroom_unavailability=classroom_unavailability)


@app.route('/classroom_unavailability', methods=['GET'])
def classroom_unavailability():
    """ 
        Route handler for getting classrooms unavailability data.
        This function fetches all ClassroomUnavailable objects from the database.
        
    """
    
    classroom_unavailabilities = ClassroomUnavailable.query.all()
    return render_template('classroom_unavailability.html', classroom_unavailabilities=classroom_unavailabilities)


@app.route("/solve")
def solve():
    """ 
        Route handler for solving the course scheduling problem.
        This route prepares the necessary data for solving the course scheduling problem, invoking the class
        CourseScheduler to solve the scheduling.
        It checks various conditions before proceeding with the scheduling process.
        The route redirects to the success route upon successful scheduling. 
        If the scheduling process encounters any issues or failures, it redirects to the unsuccess route.

    """
    
    utils.get_teachers()
    
    # Check some conditions before solving the problem
    if not utils.check_classrooms():
        return redirect(url_for('classrooms'))

    if not utils.check_courses():
        return redirect(url_for('get_classes'))

    if not utils.check_general_data():
        return redirect(url_for('general_data'))

    """
    if not utils.check_classroom_count():
        return redirect(url_for('classrooms'))
    """
        
    if not utils.check_largest_classroom_capacity():
        return redirect(url_for('classrooms'))
    
    if not utils.check_conflict_teacher_assign():
        return redirect(url_for('teachers_subjects'))
    
    # Unpack courses data dicts
    (classes, teacher_subject, enrolled_students, min_days_classes, max_days_classes, min_classes_per_week,
     max_classes_per_week, general_course_data) = utils.read_courses_data()
    
    # Unpack classrooms data dicts
    (_, classroom_capacities, unavailable_classrooms) = utils.read_classrooms_data()
    
    # Days and hours
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    hours = ['9-11', '11-13', '14-16', '16-18']
    
    # Get penalties weights (to all courses)
    penalties = Penalties.get_or_create()
    
    # Pack the weights on a list
    weights = [penalties.dispersion_different_days,
               penalties.gaps_in_a_day, penalties.gaps_between_days]
    
    # Max classes (2 hour blocks) of a teacher per day (all courses)
    max_classes_per_teacher = 3

    # Pack time objs/data on a time_ranges list
    time_ranges = [min_days_classes, max_days_classes, min_classes_per_week,
                   max_classes_per_week, max_classes_per_teacher, general_course_data]
    
    teachers = {}

    # Handle unavailability, strict assign and Preferences
    for teacher, subjects in teacher_subject.items():
        # Get Teacher from db table
        my_teacher = Teacher.query.filter_by(teacher_name=teacher).first()
        
        # Data on the table is a string representing a JSON array
        preferences_str = my_teacher.preferences
        strict_assign_str = my_teacher.strict_assignment
        unavailable_str = my_teacher.unavailability
        
        # Convert the strings/deserialize to Python lists of tuples
        preferences_list = json.loads(preferences_str)
        strict_list = json.loads(strict_assign_str)
        unavailable_list = json.loads(unavailable_str)
        preferences_tuple_list = [tuple(preference) for preference in preferences_list]
        strict_tuple_list = [tuple(strict) for strict in strict_list]
        
        # Check for incompabilities between strict_assign and unavailable classrooms slots
        # This is already checked, here its only to double check
        # If for some reason it passes, the strict assign entrie is deleted before going to the solver
        strict_tuple_list = utils.remove_unavailable_tuples(strict_tuple_list, unavailable_classrooms)
        unavailable_tuple_list = [tuple(unavailable) for unavailable in unavailable_list]
        
        # Build the final dict
        teachers[teacher] = {'subjects': subjects, 'unavailability': unavailable_tuple_list,
                             'strict_assign': strict_tuple_list, 'preferences': preferences_tuple_list}
    
    # Check for subjects with same name and then update
    teachers = utils.update_subjects_match(teachers)
  
    # Instanciate and solve
    scheduler = CourseScheduler(classes, days, hours, teacher_subject, teachers, unavailable_classrooms,
                            classroom_capacities, enrolled_students, time_ranges, weights)

    # Handle routes for success/unsuccess
    start_time = time.time()
    _, solver_status = scheduler.solve_schedule(mysolver='gurobi')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")
    # Something went wrong
    if not solver_status:
        return redirect(url_for('unsuccess'))
    
    return redirect(url_for('success'))


@app.route("/success")
def success():
    """ Route handler for displaying a success message after successful course scheduling. """
    
    return render_template("success.html")


@app.route("/unsuccess")
def unsuccess():
    """ Route handler for displaying an error message when course scheduling is unsuccessful. """
    
    return render_template("unsuccess.html")


@app.route("/display_schedules")
def display_schedules():
    """ 
        Route handler for displaying schedules of all courses.
        This route retrieves schedule data stored in Excel files for each course from the 'Schedules' folder.
        If the schedule data is available, it reads the Excel file into a DataFrame and converts it to HTML
        format for rendering in the template. If no schedule data is found for a course,
        it assigns 'None' to its entry in the dictionary.

    """

    class_names = [row.class_name for row in db.session.query(ClassData.class_name).distinct().all()]

    # Create a dictionary to store schedule DataFrames for each class
    schedule_data = {}
    for class_name in class_names:
        
        folder_path = os.path.join(os.getcwd(), 'Schedules')
        if not os.path.exists(folder_path):
            schedule_data[class_name] = None
              
        file_path = os.path.join(folder_path, f'Schedule_{class_name}.xlsx')

        if os.path.exists(file_path):
            # Read the Excel file into a DataFrame
            schedule_df = pd.read_excel(file_path, usecols='A:F', nrows=9)
            # Replace NaN values with empty strings
            schedule_df = schedule_df.fillna('')
            schedule_df = schedule_df.rename(columns={'Unnamed: 0': ''})
            schedule_data[class_name] = schedule_df.to_html(classes='table table-striped', index=False)
        else:
            schedule_data[class_name] = None

    return render_template("display_schedules.html", schedule_data=schedule_data)


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all() 
        # Create database tables before running the app
        db.create_all()
        existing_penalties = Penalties.get_or_create()
        # The utils object will be available in all routes.
        utils = Utils()
    app.run(debug=True)