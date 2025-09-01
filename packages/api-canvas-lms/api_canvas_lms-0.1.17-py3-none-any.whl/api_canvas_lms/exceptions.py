""" 
Programa : Module for Exceptions
Fecha Creacion : 22/08/2024
Fecha Update : 
Version : 1.0.0
Actualizacion : 
Author : Jaime Gomez
"""

class ManyTeachersException(Exception):

    def __init__(self, message="There are many teachers", teachers=None, code=None):
        super().__init__(message)
        self.code = code
        self.teachers = teachers

    def __str__(self):
        if self.code:
            return f"[Error code {self.code}]: {super().__str__()}"
        else:
            return super().__str__() + str(self.teachers)
        
class NotFoundTeacherException(Exception):
        
    def __init__(self, message="Teacher doesn't exist",  code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            return f"[Error code {self.code}]: {super().__str__()}"
        else:
            return super().__str__()
        
class NotFoundCourseException(Exception):
        
    def __init__(self, message="Course doesn't exist", code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            return f"[Error code {self.code}]: {super().__str__()}"
        else:
            return super().__str__()

class NotFoundCoursesException(Exception):
        
    def __init__(self, message="Courses don't exist", code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            return f"[Error code {self.code}]: {super().__str__()}"
        else:
            return super().__str__()