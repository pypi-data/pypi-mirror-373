""" 
Programa : ADDA module for Canvas
Fecha Creacion : 05/08/2024
Fecha Update : 19/08/2024
Version : 1.1.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging
import pandas as pd
from .module import ModuleTemplateCourseCanvas 
from .module import  KEY_MOD_1, KEY_MOD_2
from .module import  LABEL_CLASS_MATERIALS
from .module import  TEMPLATE_SHORT_SESSION, TEMPLATE_SHORT_NRO_SESSION
from .discussion_topic import DiscussionTopics
from .course import Course , NAME

# METHODOLOGY ADDA

# -*- coding: utf-8 -*-
LABEL_METHOD_ADDA_BEFORE     = "Antes de la clase"  #"FASE ASÍNCRONA ( Antes )"
LABEL_METHOD_ADDA_BEFORE_POS = 1
LABEL_METHOD_ADDA_DURING     = "Durante la clase"  #"FASE SÍNCRONA ( Durante )"
LABEL_METHOD_ADDA_DURING_POS = 3
LABEL_METHOD_ADDA_AFTER      =  "Después de la clase"  # "FASE ASÍNCRONA ( Después )"
LABEL_METHOD_ADDA_AFTER_POS  = 6

LABEL_METHOD_ADDA_DEPRECATE = ("Antes de clase", 
                               "Durante clase", 
                               "Después de clase",
                               "Antes", 
                               "Durante", 
                               "Después",  
                               "FASE ASÍNCRONA",
                               "FASE SÍNCRONA", 
                               "FASE ASÍNCRONA",
                               "ANTES",
                               "DURANTE",
                               "DESPUÉS"
                               )


MOD_ADDA_NAME = "name"
MOD_ADDA_INCOMPLETE = "incomplete"

RES_STATUS_ADDA = "status_adda"
RES_COURSE = "course"
RES_TEACHERS = "teachers"
RES_MODULES = "modules"

# Create a logger for this module
logger = logging.getLogger(__name__)


class ModuleADDA :

    def __init__(self, nro_week, name):
        self.nro_week = nro_week
        self.name = name
        self.before = False
        self.during = False
        self.after = False

    def validate(self):
        return self.before and self.during and self.after

    def incomplete(self):
        data = list()
        if not self.before : data.append(LABEL_METHOD_ADDA_BEFORE)
        if not self.during : data.append(LABEL_METHOD_ADDA_DURING)
        if not self.after : data.append(LABEL_METHOD_ADDA_AFTER)
        return data        

class BasicModuleCourseCanvasADDA(ModuleTemplateCourseCanvas):

    def __init__(self, course_id,  access_token, api_rest_path):
        super().__init__(course_id, access_token, api_rest_path)

    def extract_item_adda_module_course(self, mod, nro_week):

        module_adda = ModuleADDA(nro_week, mod["name"])

        mod_items = mod["items"] 

        if len(mod_items) > 0 :
            
            df = pd.DataFrame(mod_items)                    

            # Strip leading and trailing spaces from the 'title' column
            df['title'] = df['title'].str.strip()

            # Exist the LABEL_METHOD_ADDA_BEFORE ?
            item_adda_before = df[df["title"] == LABEL_METHOD_ADDA_BEFORE]
            module_adda.before = len(item_adda_before) == 1

            # Exist the LABEL_METHOD_ADDA_DURING ?
            item_adda_during = df[df["title"] == LABEL_METHOD_ADDA_DURING]        
            module_adda.during = len(item_adda_during) == 1

            # Exist the LABEL_METHOD_ADDA_AFTER ?
            item_adda_after = df[df["title"] == LABEL_METHOD_ADDA_AFTER]        
            module_adda.after = len(item_adda_after) == 1

        return module_adda


    def is_valid_structure(self, w_from = 1, w_to = 16 ):

        response = dict()

        # Get course information
        course = Course(self.course_id, self.access_token, self.api_rest_path) 
        info_course = course.get_summary()
        logger.debug(info_course)

        # Get teacher information if ADD information is imcomplete
        teachers = course.get_teachers()
        logger.debug(teachers)

        # Validate ADDA structure
        modules = dict()
        for item in self.read_adda_module_course(w_from,w_to):
            logging.debug(f" {item.name} {item.validate()}")
            if not item.validate():
                modules[item.nro_week] = {
                                    MOD_ADDA_NAME : item.name,
                                    MOD_ADDA_INCOMPLETE : item.incomplete()
                                    } 
        # Are incomplete ADDA information
        status_adda = not bool(len(modules))

        # Create response
        response[RES_STATUS_ADDA] = status_adda
        response[RES_COURSE] = info_course
        response[RES_TEACHERS] = teachers

        # if not status_adda: response[RES_MODULES] = modules
        response[RES_MODULES] = modules

        return response


    def read_adda_module_course(self, w_from = 1, w_to = 16):

        module_course = list()

        # Parameters to include additional information
        params = {
#            'include[]': ['items', 'content_details']
            'include[]': ['items']
        }

        logger.debug("Begin : get module details")
        modules = self.get_modules(params)
        logger.debug("End : get module details")
        logger.debug(modules)
        
        for mod in modules:
            if (mod["name"].upper().startswith(KEY_MOD_1) or mod["name"].upper().startswith(KEY_MOD_2) ) :
                nro_week = self.get_nro_week(mod["name"])
                if  w_from <= nro_week <= w_to :
                    logger.debug(f"[{mod['position']}] : {mod['name']}")
                    module_course.append(self.extract_item_adda_module_course(mod, nro_week))  

        return module_course 

class ModuleCourseCanvasADDA(BasicModuleCourseCanvasADDA):
 
    def __init__(self, course_id, template_discussion_topic, access_token, api_rest_path ):
        super().__init__(course_id, access_token, api_rest_path)
        self.template_discussion_topic = template_discussion_topic

    def clean_module_course(self, mod, nro_week):
        
        flag = True
        mod_items = self.get_items(mod["id"])

        for item in mod_items:
            # Strip leading and trailing spaces from the 'title' column
            item['title'] = item['title'].strip()
            #    
            if (item["title"].startswith(LABEL_CLASS_MATERIALS) or
                item["title"].startswith(LABEL_METHOD_ADDA_DEPRECATE)) :
                flag = False
                print("DELETE ITEM ===> " , item["title"])
                self.delete_item_module(mod['id'], item["id"] )

        if flag : print("EMPTY ITEM TO DELETE")


    def config_module(self, mod): 
        """
            Configure the label of methodology ADDA
        """
        mod_items = self.get_items(mod["id"])
        df = pd.DataFrame(mod_items)
        #print("ITEMS ===> " , mod_items)

        if len(mod_items) > 0 :
  
            # Create
            if len(df[df["title"] == LABEL_METHOD_ADDA_BEFORE]) == 0:
                self.create_subheader_module(mod['id'], LABEL_METHOD_ADDA_BEFORE , LABEL_METHOD_ADDA_BEFORE_POS)
                # Refresh mod_items attributes
                mod_items = self.get_items(mod["id"])
                df = pd.DataFrame(mod_items)
            if len(df[df["title"] == LABEL_METHOD_ADDA_DURING]) == 0:
                self.create_subheader_module(mod['id'], LABEL_METHOD_ADDA_DURING , LABEL_METHOD_ADDA_DURING_POS)
                # Refresh mod_items attributes
                mod_items = self.get_items(mod["id"])
                df = pd.DataFrame(mod_items)
            if len(df[df["title"] == LABEL_METHOD_ADDA_AFTER]) == 0:
                self.create_subheader_module(mod['id'], LABEL_METHOD_ADDA_AFTER , LABEL_METHOD_ADDA_AFTER_POS)
                # Refresh mod_items attributes
                mod_items = self.get_items(mod["id"])
                df = pd.DataFrame(mod_items)
            
            # Update

        else: 
            # Module items empty
            self.create_subheader_module(mod['id'], LABEL_METHOD_ADDA_BEFORE , LABEL_METHOD_ADDA_BEFORE_POS)
            self.create_subheader_module(mod['id'], LABEL_METHOD_ADDA_DURING , LABEL_METHOD_ADDA_DURING_POS)
            self.create_subheader_module(mod['id'], LABEL_METHOD_ADDA_AFTER , LABEL_METHOD_ADDA_AFTER_POS)

    def create_discussion_topics_module(self, mod_id, content_id, pos = 1 ):
        data = {'module_item[content_id]'   : content_id ,
                'module_item[type]'         : 'Discussion',
                'module_item[position]'     : pos,
                'module_item[indent]'       : '1'}
        self.post_item(mod_id, data)

    def config_module_course(self, mod, nro_week):

        NRO_SESSION = "{:02d}".format(nro_week)
        S_NRO_SESSION = "S{:02d}".format(nro_week)

        mod_items = self.get_items(mod["id"])
        
        # print("ITEMS ===> " , pd.DataFrame(mod_items).head(10))

        if len(mod_items) > 0 :
            
            df = pd.DataFrame(mod_items)                    
            item_adda_before = df[df["title"] == LABEL_METHOD_ADDA_BEFORE]
        
            # Exist the LABEL_METHOD_ADDA_BEFORE ?
            if len(item_adda_before) == 1:
        
                pos_adda_before = item_adda_before['position'].values[0]

                # Verify if the forum before was create
                if df[df['title'].str.startswith(S_NRO_SESSION)].empty:
                        
                    #'''
                    # Create discussion topic
                    dt_before = DiscussionTopics(self.course_id, self.access_token)

                    title_discussion_topic_before = \
                        self.template_discussion_topic["before"]["title"].replace(TEMPLATE_SHORT_SESSION,S_NRO_SESSION)

                    title_discussion_topic_before = \
                        title_discussion_topic_before.replace(TEMPLATE_SHORT_NRO_SESSION,NRO_SESSION)
                    
                    res_dt_before = dt_before.create_topic(title_discussion_topic_before,
                                                                    self.template_discussion_topic["before"]["message"])
                    
                    # Create link to discussion topic in module
                    self.create_discussion_topics_module(mod['id'],res_dt_before['id'], pos_adda_before+1)            
                    #'''    
    
        # REFRESH : READ AGAIN BECAUSE POSITION CHANGE IN MODULE
        mod_items = self.get_items(mod["id"])
        #print("ITEMS ===> " , pd.DataFrame(mod_items).head())

        if len(mod_items) > 0 :
            
            df = pd.DataFrame(mod_items)                    
            item_adda_after = df[df["title"] == LABEL_METHOD_ADDA_AFTER]
        
            # Exist the LABEL_METHOD_ADDA_AFTER ?
            if len(item_adda_after) == 1:
        
                pos_adda_after = item_adda_after['position'].values[0]

                # Verify if the forum after was create
                if df[df['title'].str.startswith(S_NRO_SESSION + " : IA ->")].empty:
                    pass
                    #'''    
                    # Create discussion topic
                    dt_after = DiscussionTopics(self.course_id, self.access_token)

                    title_discussion_topic_after = \
                        self.template_discussion_topic["after"]["title"].replace(TEMPLATE_SHORT_SESSION,S_NRO_SESSION)
                    
                    res_dt_after = dt_after.create_topic(title_discussion_topic_after,
                                                                    self.template_discussion_topic["after"]["message"])

                    # Create link to discussion topic in module
                    self.create_discussion_topics_module(mod['id'],res_dt_after['id'], pos_adda_after+1)            
                    #'''
    def configure(self, w_from, w_to, action="R"):

        logging.info("===============> Create ADDA structure <================")

        super().configure(w_from, w_to, action)     

        logging.info("===============> Configure ADDA methodology <================")
        
        modules = self.get_modules()
        
        logging.debug(modules)
        
        for mod in modules:
            #print(mod)
            if (mod["name"].startswith(KEY_MOD_1) or mod["name"].upper().startswith(KEY_MOD_2) ) :
                #idx += 1
                nro_week = self.get_nro_week(mod["name"])
                if  w_from <= nro_week <= w_to :
                    logging.info(f"====> {mod['position']} : {mod['name']}")
                    #if action == "C":   self.config_module(mod)  
                    if action == "F":   self.config_module_course(mod, nro_week)  # Create foros
                    if action == "D":   self.clean_module_course(mod, nro_week)   # Delete items
