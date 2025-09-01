""" 
Programa :  Accounts module for Canvas
Fecha Creacion : 05/08/2024
Fecha Update : None
Version : 1.0.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging
from .base import BaseCanvas
from .course import Course
from .utils import remove_tilde
from .utils import get_course_info_from_raw_coursename
import pandas as pd

# Create a logger for this module
logger = logging.getLogger(__name__)

class Account(BaseCanvas):

    def __init__(self, account_id, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)
        # 
        self.account_id = account_id
        self.courses = None
        # CONNECTOR
        self.url_accounts               = '<path>/accounts/<account_id>'
        self.url_accounts_terms         = '<path>/accounts/<account_id>/terms'
        self.url_accounts_item_term     = '<path>/accounts/<account_id>/terms/<term_id>'
        self.url_accounts_courses       = '<path>/accounts/<account_id>/courses'
        self.url_accounts_sub_accounts  = '<path>/accounts/<account_id>/sub_accounts'
        self.url_accounts_users         = '<path>/accounts/<account_id>/users'

    def get_details(self, params = None):
        url = self.url_accounts
        url = url.replace('<account_id>', self.account_id)
        logger.debug(url)
        return self.get_all_pages(url,params)

    def get_courses_raw(self, params = None):
        url = self.url_accounts_courses
        url = url.replace('<account_id>', self.account_id)
        logger.debug(url)
        return self.get_all_pages(url,params)

    
    def get_courses(self):
        # Parameters to specify the number of results per page
        params = {
            'per_page': 100  # Maximum allowed per page
        }
        return self.get_courses_raw(params)
    

    def get_courses_by_enrollment_term(self, enrollment_term_id):

        courses = list()

        # Parameters to specify the number of results per page
        params = {
            'per_page': 200 , # Maximum allowed per page
            'enrollment_term_id' : int(enrollment_term_id),
            "include[]":"active_teachers"
        }

        for course in self.get_courses_raw(params):
            logging.debug(course)
            raw_coursename =  course["name"]
            course_info = get_course_info_from_raw_coursename(raw_coursename)
            teachers = self.get_teachers_by_course(course)    
            info_course =  { 
                            "id" : course["id"] , 
                            "name" : course["name"],
                            "short_name" : course_info.get('course_name'),
                            "specialities" : course_info.get('specialities'),
                            "cycles" : course_info.get('cycles'),                                
                            "sections" : course_info.get('sections'),
                            "teachers" : teachers
                            }

            courses.append(info_course)

        return courses

    def get_courses_by_term_and_sub_account(self, enrollment_term_id, 
                                            sub_account_id, include_teachers = False):

        courses = list()

        # Parameters to specify the number of results per page
        params = {
            'per_page': 100 , # Maximum allowed per page
            'with_enrollments': True,
            'enrollment_type[]': "teacher",
            'enrollment_term_id' : int(enrollment_term_id),
            'by_subaccounts[]' : int(sub_account_id),
            "state[]": "available"  # Filter to only show active courses

        }

        for course in self.get_courses_raw(params):
            raw_coursename =  course["name"]
            course_info = get_course_info_from_raw_coursename(raw_coursename)
            logging.debug(course) 
            if include_teachers :
                teachers = self.get_teachers_by_course(course)    
                info_course =  { 
                                "id" : course["id"] , 
                                "name" : course["name"],
                                "short_name" : course_info.get('course_name'),
                                "specialities" : course_info.get('specialities'),
                                "cycles" : course_info.get('cycles'),                                
                                "sections" : course_info.get('sections'),
                                "teachers" : teachers
                                }
            else:
                info_course =  { 
                                "id" : course["id"] , 
                                "name" : course["name"],
                                "short_name" : course_info.get('course_name'),
                                "specialities" : course_info.get('specialities'),
                                "cycles" : course_info.get('cycles'),                                
                                "sections" : course_info.get('sections')
                                }

            courses.append(info_course)

        return courses

    def get_teachers_by_course(self, course):
        teachers = []
        teachers_raw = course.get("teachers", [])
        if not teachers_raw:
            course = Course(course['id'], self.access_token, self.api_rest_path)
            teachers = course.get_teachers()
        else :
            teachers = [{'id' : teacher_raw.get('id'),
                        'name' : teacher_raw.get('display_name')} 
                        for teacher_raw in teachers_raw]


        return teachers

    def get_sub_accounts_raw(self, params = None):
        url = self.url_accounts_sub_accounts
        url = url.replace('<account_id>', self.account_id)
        logger.debug(url)
        return self.get_all_pages(url,params)
    
    def get_sub_accounts(self, params = None):

        sub_accounts = list()

        for sub_account in self.get_sub_accounts_raw(params):
            sub_accounts.append( { "id" : sub_account["id"] , "name" : sub_account["name"]} )

        return sub_accounts

    def get_terms(self, params = None):
        url = self.url_accounts_terms
        url = url.replace('<account_id>', self.account_id)
        logger.info(url)
        return self.get_all_pages(url,params)

    def get_term(self, term_id, params = None):
        url = self.url_accounts_item_term
        url = url.replace('<account_id>', self.account_id)
        url = url.replace('<term_id>', term_id)
        logger.info(url)
        return self.get_all_pages(url,params)

    def get_users_by_name(self, search_name):
        url = self.url_accounts_users
        url = url.replace('<account_id>', self.account_id)

        params = {
            "search_term": search_name
        }

        return self.get(url,params)
    

    def set_courses(self, courses):
        self.courses = courses

    def get_teachers_by_enrollment_term(self, enrollment_term_id):

        #courses = self.get_courses_by_enrollment_term(enrollment_term_id)

        teachers = dict()
        for course in self.courses:

            for teacher in course.get("teachers"):
                
                if teacher.get("id") not in teachers :    
                    teachers[teacher.get("id")] = {
                        "name" : teacher.get("name"),
                        "name_search" : remove_tilde(teacher.get("name")).lower()
                        }

        return teachers


    def get_courses_by_enrollment_term_and_teacher(self, enrollment_term_id, teacher_id):

        #courses = self.get_courses_by_enrollment_term(enrollment_term_id)

        courses_of_teacher = []

        for course in self.courses:
            
            logging.debug(teacher_id)
            logging.debug(course.get("teachers"))

            teacher_ids = {teacher["id"] for teacher in course.get("teachers")}

            if teacher_id in teacher_ids:
                courses_of_teacher.append(course)

        logging.debug(courses_of_teacher)

        return courses_of_teacher
