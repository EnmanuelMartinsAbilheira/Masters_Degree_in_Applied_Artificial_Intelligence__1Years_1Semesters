"""
    Course Scheduling System
    Authors:
        - Enmanuel Martins (16430)
        - Pedro Ferreira (17029)
        
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, FormField, FieldList, HiddenField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, InputRequired, ValidationError


class NumberClasses(FlaskForm):
    """ Class to handle the form for Course name and number of subjects. """
    
    course_name = StringField('Select Course Name',  validators=[
        DataRequired(),
        Length(min=2, max=30)
    ])
    n_subjects = IntegerField('Select Number of Subjects', validators=[
        DataRequired(),
        NumberRange(min=4, message='Number of subjects must be at least 4!'),
        NumberRange(max=7, message='Number of subjects must be at most 7!')
    ])
    
    
class SubjectForm(FlaskForm):
    """ Class to handle the form for Subjects (fields). """
    
    sub_name = StringField('Name', validators=[DataRequired(), Length(min=2, max=30)])
    teacher = StringField('Teacher', validators=[DataRequired(), Length(min=2, max=30)])
    enrolled_students = IntegerField('Number Enrolled Students', validators=[
        DataRequired(),
        NumberRange(min=10, message='Number of enrolled students must be at least 10!'),
        NumberRange(max=50, message='Number of enrolled students must be at most 50!')
        ])
    min_days_classes = IntegerField('Min Days of Classes', validators=[
        DataRequired(),
        NumberRange(min=1, message='Number of min_days_classes must be at least 1!'),
        NumberRange(max=4, message='Number of min_days_classes must be at most 4!')
        ])
    max_days_classes = IntegerField('Max Days of Classes', validators=[
        DataRequired(),
        NumberRange(min=2, message='Number of max_days_classes must be at least 2!'),
        NumberRange(max=5, message='Number of max_days_classes must be at most 5!')
        ])
    min_classes_per_week = IntegerField('Min Classes per Week', validators=[
        DataRequired(),
        NumberRange(min=1, message='Number of min_classes_per_week must be at least 1!'),
        NumberRange(max=4, message='Number of min_classes_per_week must be at most 4!')
        ])
    max_classes_per_week = IntegerField('Max Classes per Week', validators=[
        DataRequired(),
        NumberRange(min=2, message='Number of max_classes_per_week must be at least 2!'),
        NumberRange(max=5, message='Number of max_classes_per_week must be at most 5!')
        ])
    
    
    def validate_max_days_classes(form, field):
        """ Custom validation to ensure max_days_classes >= min_days_classes."""
 
        min_days_classes = form.min_days_classes.data

        if field.data is not None and field.data < min_days_classes:
            raise ValidationError('Max Days of Classes must be greater than or equal to Min Days of Classes.')
        
    def validate_max_classes_per_week(form, field):
        """ Custom validation to ensure max_classes_per_week >= min_classes_per_week. """
        
        min_classes_per_week = form.min_classes_per_week.data

        if field.data is not None and field.data < min_classes_per_week:
            raise ValidationError('Max Classes per Week must be greater than or equal to Min Classes per Week.')
        
    def validate_min_days_classes(form, field):
        """ Custom validation to ensure min_days_classes >= min_classes_per_week. """
        
        min_classes_per_week = form.min_classes_per_week.data

        if field.data is not None and field.data < min_classes_per_week:
            raise ValidationError('Min Days of Classes must be greater than or equal to Min Classes per Week.')
        
           
class ClassForm(FlaskForm):
    """ Class to handle the form for Courses (class_name + subjects FieldList). """
    
    class_name = StringField('Class Name', validators=[DataRequired(), Length(min=2, max=30)])
    subjects = FieldList(FormField(SubjectForm))

    
class GeneralDataForm(FlaskForm):
    """ Class to handle the form for Course General Data fields. """
    
    min_blocks_per_day = IntegerField('Min Blocks per Day', validators=[
        DataRequired(),
        NumberRange(min=1, message='Number of min_blocks_per day must be at least 1!'),
        NumberRange(max=4, message='Number of min_blocks_per day must be at most 4!')
        ])
    max_blocks_per_day = IntegerField('Max Blocks per Day', validators=[
        DataRequired(),
        NumberRange(min=1, message='Number of max_blocks_per_day must be at least 1!'),
        NumberRange(max=4, message='Number of max_blocks_per_day must be at most 4!')
        ])
    min_days_of_classes = IntegerField('Min Days of Classes', validators=[
        DataRequired(),
        NumberRange(min=1, message='Number of min_days_of_classes must be at least 1!'),
        NumberRange(max=4, message='Number of min_days_of_classes must be at most 4!')
        ])
    max_days_of_classes = IntegerField('Max Days of Classes', validators=[
        DataRequired(),
        NumberRange(min=2, message='Number of max_days_of_classes must be at least 2!'),
        NumberRange(max=5, message='Number of max_days_of_classes must be at most 5!')
        ])
    max_blocks_per_week = IntegerField('Max Blocks per Week', validators=[
        DataRequired(),
        NumberRange(min=10, message='Number of max_blocks_per_week must be at least 10!'),
        NumberRange(max=20, message='Number of max_blocks_per_week must be at most 20!')
        ])
    min_blocks_per_period = IntegerField('Min Blocks per Period', validators=[
        DataRequired(),
        NumberRange(min=1, message='Number of min_blocks_per_period must be at least 1!'),
        NumberRange(max=2, message='Number of min_blocks_per_period must be at most 2!')
        ])
    
    
    def validate_max_blocks_per_day(form, field):
        """ Custom validation to ensure max_blocks_per_day >= min_blocks_per_day. """
        
        min_blocks_per_day = form.min_blocks_per_day.data

        if field.data is not None and field.data < min_blocks_per_day:
            raise ValidationError('Max Blocks per Day must be greater than or equal to Min Blocks per Day.')

    
    def validate_max_days_of_classes(form, field):
        """ Custom validation to ensure max_days_of_classes >= min_days_of_classes. """
        
        min_days_of_classes = form.min_days_of_classes.data

        if field.data is not None and field.data < min_days_of_classes:
            raise ValidationError('Max Days of Classes must be greater than or equal to Min Days of Classes.')


class ClassroomForm(FlaskForm):
    """ Class to handle the form for Classrooms fields. """
    
    classroom_id = HiddenField('Classroom ID')
    classroom_name = StringField('Classroom Name', validators=[DataRequired(), Length(min=2, max=30)])
    classroom_capacity = IntegerField('Classroom Capacity', validators=[DataRequired(), NumberRange(min=20, max=100)])
    

class ClassroomUnavailableForm(FlaskForm):
    """ Class to handle the form for Classroom Unavailability fields. """
    
    day = SelectField('Day', choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
                                      ('Thu', 'Thursday'), ('Fri', 'Friday')],
                      validators=[InputRequired()])
    hour = SelectField('Hour', choices=[('9-11', '9-11 AM'), ('11-13', '11 AM - 1 PM'),
                                        ('14-16', '2-4 PM'), ('16-18', '4-6 PM')],
                       validators=[InputRequired()])
    
    
class PreferencesForm(FlaskForm):
    """ Class to handle the form for Teacher Preferences fields. """
    
    day = SelectField('Day', choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
                                      ('Thu', 'Thursday'), ('Fri', 'Friday')],
                      validators=[InputRequired()])
    hour = SelectField('Hour', choices=[('9-11', '9-11 AM'), ('11-13', '11 AM - 1 PM'),
                                        ('14-16', '2-4 PM'), ('16-18', '4-6 PM')],
                       validators=[InputRequired()])
    subject = SelectField('Subject', choices=[], validators=[InputRequired()])
    weight = IntegerField('Weight', validators=[InputRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Add Preferences')
    
    
class StrictAssignForm(FlaskForm):
    """ Class to handle the form for Teacher Strict Assignment fields. """
    
    day = SelectField('Day', choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
                                      ('Thu', 'Thursday'), ('Fri', 'Friday')],
                      validators=[InputRequired()])
    hour = SelectField('Hour', choices=[('9-11', '9-11 AM'), ('11-13', '11 AM - 1 PM'),
                                        ('14-16', '2-4 PM'), ('16-18', '4-6 PM')],
                       validators=[InputRequired()])
    subject = SelectField('Subject', choices=[], validators=[InputRequired()])
    submit = SubmitField('Add Strict Assign')
    

class UnavailableForm(FlaskForm):
    """ Class to handle the form for Teacher Unavailability fields. """
    
    day = SelectField('Day', choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
                                      ('Thu', 'Thursday'), ('Fri', 'Friday')],
                      validators=[InputRequired()])
    hour = SelectField('Hour', choices=[('9-11', '9-11 AM'), ('11-13', '11 AM - 1 PM'),
                                        ('14-16', '2-4 PM'), ('16-18', '4-6 PM')],
                       validators=[InputRequired()])
    submit = SubmitField('Add Unavailability')