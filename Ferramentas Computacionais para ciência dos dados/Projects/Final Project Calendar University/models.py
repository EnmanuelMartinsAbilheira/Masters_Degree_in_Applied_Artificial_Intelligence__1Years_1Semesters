"""
    Course Scheduling System
    Authors:
        - Enmanuel Martins (16430)
        - Pedro Ferreira (17029)
        
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ClassData(db.Model):
    """ Class to handle the db model for Courses (+ subjects). """
    
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    subject_name = db.Column(db.String(50), nullable=False)
    teacher = db.Column(db.String(50), nullable=False)
    enrolled_students = db.Column(db.Integer, nullable=False)
    min_days_classes = db.Column(db.Integer, nullable=False)
    max_days_classes = db.Column(db.Integer, nullable=False)
    min_classes_per_week = db.Column(db.Integer, nullable=False)
    max_classes_per_week = db.Column(db.Integer, nullable=False)
    

class GeneralData(db.Model):
    """ Class to handle the db model for Courses General Data. """
    
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(50), nullable=False, unique=True)
    min_blocks_per_day = db.Column(db.Integer, nullable=False)
    max_blocks_per_day = db.Column(db.Integer, nullable=False)
    min_days_of_classes = db.Column(db.Integer, nullable=False)
    max_days_of_classes = db.Column(db.Integer, nullable=False)
    max_blocks_per_week = db.Column(db.Integer, nullable=False)
    min_blocks_per_period = db.Column(db.Integer, nullable=False)
    

class Classroom(db.Model):
    """ Class to handle the db model for Classrooms. """
    
    id = db.Column(db.Integer, primary_key=True)
    classroom_name = db.Column(db.String(50), nullable=False, unique=True)
    classroom_capacity = db.Column(db.Integer, nullable=False)   


class ClassroomUnavailable(db.Model):
    """ Class to handle the db model for Classrooms Unavailability. """
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(50), nullable=False)
    hour = db.Column(db.String(50), nullable=False)   
    
class Penalties(db.Model):
    """ Class to handle the db model for Penalties. """
    
    id = db.Column(db.Integer, primary_key=True)
    dispersion_different_days = db.Column(db.Float, nullable=False, default=2.0)
    gaps_in_a_day = db.Column(db.Float, nullable=False, default=1.0)
    gaps_between_days = db.Column(db.Float, nullable=False, default=1.0)


    @classmethod
    def get_or_create(cls):
        """ Class method to get the penalties parameters or to create them for the first time its called.
            The first time its called creates the parameters with some default values. 
        """
        
        penalties_instance = cls.query.first()
        if penalties_instance is None:
            penalties_instance = cls()
            db.session.add(penalties_instance)
            db.session.commit()
        return penalties_instance
    

class Teacher(db.Model):
    """ Class to handle the db model for Teachers and its assignment details. """
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(255), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)
    unavailability = db.Column(db.String(255), default='[]')
    strict_assignment = db.Column(db.String(255), default='[]')
    preferences = db.Column(db.String(255), default='[]')