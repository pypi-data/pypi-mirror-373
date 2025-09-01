""" 
Programa : Course module for Canvas
Fecha Creacion : 11/08/2024
Fecha Update : None
Version : 1.0.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging
from .base import BaseCanvas
from .utils import get_course_info_from_raw_coursename

ID =  'id'
NAME =  'name'
SHORT_NAME =  'short_name'
SPECIALITIES =  'specialities'
CYCLES =  'cycles'
SECTIONS =  'sections'
EMAIL = 'email'
TEACHERS = 'teachers'

# Create a logger for this module
logger = logging.getLogger(__name__)

class Course(BaseCanvas):

    def __init__(self, course_id, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)
        # 
        self.course_id = course_id
        # CONNECTOR
        self.url_course        = '<path>/courses/<course_id>'
        self.url_course_users  = '<path>/courses/<course_id>/search_users'


    def get(self, params = None):
        url = self.url_course
        url = url.replace('<course_id>', self.course_id)
        return super().get(url,params)

    def get_summary(self, params = None):
        course =  self.get(params)

        raw_coursename =  course[NAME]
        course_info = get_course_info_from_raw_coursename(raw_coursename)
        return  {
                    ID : course[ID],
                    NAME : raw_coursename,
                    SHORT_NAME : course_info.get('course_name'),
                    SPECIALITIES : course_info.get('specialities'),
                    CYCLES : course_info.get('cycles'),
                    SECTIONS : course_info.get('sections')
                }

    def get_users(self, params = None):
        url = self.url_course_users
        url = url.replace('<course_id>', str(self.course_id))
        return self.get_all_pages(url,params)

    def get_teachers(self):
        
        teachers = list()
        
        # Parameters to filter by enrollment type 'teacher'
        params = {
            'enrollment_type[]': 'teacher',
            'enrollment_role[]': 'TeacherEnrollment'
        }
        
        _teachers = self.get_users(params)
        logger.debug(_teachers)

        for teacher in _teachers:
            
            info_teacher = {
                            ID  : teacher.get(ID), 
                            NAME  : teacher.get(NAME), 
                            EMAIL : teacher.get(EMAIL, "Not Available") 
                            }

            teachers.append(info_teacher)

        return teachers