""" 
Programa : Enrollment module for Canvas
Fecha Creacion : 12/08/2024
Fecha Update : None
Version : 1.0.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging
from .base import BaseCanvas

# Create a logger for this module
logger = logging.getLogger(__name__)

class Enrollments(BaseCanvas):

    def __init__(self, course_id, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)
        # 
        self.course_id = course_id
        # CONNECTOR
        self.url_enrollments        = '<path>/courses/<course_id>/enrollments'

    def get(self, params = None):
        url = self.url_enrollments
        url = url.replace('<course_id>', self.course_id)
        return super().get(url,params)