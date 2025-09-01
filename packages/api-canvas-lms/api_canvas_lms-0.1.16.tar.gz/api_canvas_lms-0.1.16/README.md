# API_CANVAS_LMS

Una biblioteca para Canvas LMS

# Estructura del Proyecto

```
|--api_canvas_lms/        <-- Archivos de python
|     |--account.py         
|     |--adda.py         
|     |--base.py         
|     |--course.py         
|     |--discussion_topic.py         
|     |--enrollment.py          
|     |--module.py          
|     |--mvc.py          
|     |--user.py          
|     |--utils.py          
|
|--setup.py               <-- Define el Python build
```

# Uso

Un ejemplo de como usar la biblioteca

```
import api_canvas_lms.adda as adda 
```

```

if __name__ == "__main__":

    course_id = "your id course of Canvas"
    TOKEN = "your token"
    API_REST_PATH = "your URL"

    #''' 
    print("Start process ... !")
    mccsa = adda.BasicModuleCourseCanvasADDA(course_id, TOKEN, API_REST_PATH)
    data = mccsa.is_valid_structure()    
    print(data)
    #'''
```

