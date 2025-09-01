""" 
Programa : Module for Canvas
Fecha Creacion : 15/04/2024
Fecha Update : 05/08/2024
Version : 1.2.0
Actualizacion : Support ADDA structure
Author : Jaime Gomez
"""

import logging
import pandas as pd
from datetime import timedelta
from .base import BaseCanvas
from .utils import find_first_number

# Constants for ModuleCourseCanvas
# MODULES
 
KEY_MOD_1 = 'MÓDULO'
KEY_MOD_2 = 'SEMANA'

# SXX, Estructuras de Datos y Algoritmos, [3C24-A], LAB, [Mon-DD], [09:40-12:10], Jaime Gómez
TEMPLATE_SHORT_NRO_SESSION  = "XX"
TEMPLATE_SHORT_SESSION      = "SXX"
TEMPLATE_SHORT_DATE_CLASS   = "Mon-DD"

#PASS_RECORD                 = "XXXXX"
TEMPLATE_RECORD_URL         = "http://TU_GRABACION_WEBEX"

LABEL_CLASS_MATERIALS       = 'Material de clase'
LABEL_CLASS_MATERIALS_POS   = 1

SUB_LABEL_WEEK              = 'Semana'
SUB_LABEL_WEEK_POS          = 2
SUB_LABEL_WEEK_INDENT       = 1
SUB_LABEL_MODULE_LAB        = 'Laboratorio'
SUB_LABEL_LAB_POS           = 3
SUB_LABEL_LAB_INDENT        = 1

LABEL_VIDEO_CONFERENCES     = 'Videoconferencias ONLINE'
LABEL_VIDEO_CONFERENCES_POS = 4
LABEL_RECORDS               = 'Grabaciones de clase'
LABEL_RECORDS_POS           = 5
LABEL_RESOURCES             = 'Recursos adicionales'
LABEL_RESOURCES_POS         = 6

# Create a logger for this module
logger = logging.getLogger(__name__)

class ModuleTemplateCourseCanvas(BaseCanvas):

    def __init__(self, course_id, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)
        # 
        self.course_id = course_id
        # CONNECTOR
        self.url_modules       = '<path>/courses/<course_id>/modules?per_page=100'
        self.url_items         = '<path>/courses/<course_id>/modules/<module_id>/items?per_page=100'
        self.url_item_update   = '<path>/courses/<course_id>/modules/<module_id>/items/<item_id>'
        self.url_item_delete   = '<path>/courses/<course_id>/modules/<module_id>/items/<item_id>'

    def get_modules(self, params = None):
        url = self.url_modules
        url = url.replace('<course_id>', self.course_id)
        return self.get_all_pages(url,params)

    def get_items(self, module):
        url = self.url_items
        url = url.replace('<course_id>', self.course_id)
        url = url.replace('<module_id>', str(module))
        return self.get_all_pages(url)

    def post_item(self, mod_id, item):
        url = self.url_items
        url = url.replace('<course_id>', self.course_id)
        url = url.replace('<module_id>', str(mod_id))
        return  self.post(url, item)

    def put_item(self, mod_id, item_id, item):
        url = self.url_item_update
        url = url.replace('<course_id>', self.course_id)
        url = url.replace('<module_id>', str(mod_id))
        url = url.replace('<item_id>', str(item_id))
        return  self.put(url, item)

    def delete_item(self, mod_id, item_id):
        url = self.url_item_delete
        url = url.replace('<course_id>', self.course_id)
        url = url.replace('<module_id>', str(mod_id))
        url = url.replace('<item_id>', str(item_id))
        return  self.delete(url)

    def create_subheader_module(self, mod_id, title, pos ):
        data = {'module_item[title]'    : title ,
                'module_item[type]'     : 'SubHeader',
                'module_item[position]' : pos,
                'module_item[indent]'   : '0' }
        self.post_item(mod_id, data)

    def create_page_module(self, mod_id, title, pos, ind ):
        data = {'module_item[title]'    : title ,
                'module_item[type]'     : 'Page',
                'module_item[position]' : pos,
                'module_item[indent]'   : ind }
        self.post_item(mod_id, data)

    def create_assignment_module(self, mod_id, title, pos, ind ):
        data = {'module_item[title]'    : title ,
                'module_item[type]'     : 'Assignment',
                'module_item[position]' : pos,
                'module_item[indent]'   : ind }
        self.post_item(mod_id, data)

    def update_item_module(self, mod_id, item_id, pos, ind ):
        data = {'module_item[position]' : pos,
                'module_item[indent]'   : ind }
        self.put_item(mod_id, item_id, data)

    def delete_item_module(self, mod_id, item_id ):
        self.delete_item(mod_id, item_id)

    def config_module(self, mod):

        mod_items = self.get_items(mod["id"])
        df = pd.DataFrame(mod_items)
        # print("ITEMS ===> " , mod_items)
       
        if len(mod_items) > 0 :

            # Create
            if len(df[df["title"] == LABEL_CLASS_MATERIALS]) == 0:
                self.create_subheader_module(mod['id'], LABEL_CLASS_MATERIALS , LABEL_CLASS_MATERIALS_POS)
                # Refresh mod_items attributes
                mod_items = self.get_items(mod["id"])
                df = pd.DataFrame(mod_items)
            if len(df[df["title"] == LABEL_VIDEO_CONFERENCES]) == 0:
                self.create_subheader_module(mod['id'], LABEL_VIDEO_CONFERENCES , LABEL_VIDEO_CONFERENCES_POS)
                # Refresh mod_items attributes
                mod_items = self.get_items(mod["id"])
                df = pd.DataFrame(mod_items)
            if len(df[df["title"] == LABEL_RECORDS]) == 0:
                self.create_subheader_module(mod['id'], LABEL_RECORDS , LABEL_RECORDS_POS)
                # Refresh mod_items attributes
                mod_items = self.get_items(mod["id"])
                df = pd.DataFrame(mod_items)
            if len(df[df["title"] == LABEL_RESOURCES]) == 0:
                self.create_subheader_module(mod['id'], LABEL_RESOURCES , LABEL_RESOURCES_POS)   
                # Refresh mod_items attributes
                mod_items = self.get_items(mod["id"])
                df = pd.DataFrame(mod_items)
            
            #print(mod_items)
            #print(df[["id","title","position","indent","type"]].head(15))

            # Update
            item_week = df[df["title"].str.startswith(SUB_LABEL_WEEK)]
            if len(item_week) == 1: 
                if item_week["position"].values[0] != SUB_LABEL_WEEK_POS or \
                    item_week["indent"].values[0] != SUB_LABEL_WEEK_INDENT :
                    self.update_item_module(mod['id'], item_week["id"].values[0], \
                        SUB_LABEL_WEEK_POS , SUB_LABEL_WEEK_INDENT)

            item_lab = df[df["title"].str.startswith(SUB_LABEL_MODULE_LAB)]
            if len(item_lab) == 1: 
                if item_lab["position"].values[0] != SUB_LABEL_LAB_POS or \
                    item_lab["indent"].values[0] != SUB_LABEL_LAB_INDENT :
                    self.update_item_module(mod['id'], item_lab["id"].values[0], \
                        SUB_LABEL_LAB_POS , SUB_LABEL_LAB_INDENT)

        else: 
            # Module items empty
            self.create_subheader_module(mod['id'], LABEL_CLASS_MATERIALS , LABEL_CLASS_MATERIALS_POS)
            self.create_subheader_module(mod['id'], LABEL_VIDEO_CONFERENCES , LABEL_VIDEO_CONFERENCES_POS)
            self.create_subheader_module(mod['id'], LABEL_RECORDS , LABEL_RECORDS_POS)
            self.create_subheader_module(mod['id'], LABEL_RESOURCES , LABEL_RESOURCES_POS)   
            
    def get_nro_week(self, mod_name):
        '''
        print("MODULE NAME ==>", mod_name)
        week = mod_name.split(":")[0]
        nro_week = week[len(KEY_MOD_1):len(week)]
        print("MODULE NAME ==>", nro_week)
        try:
            nro_week = int(nro_week)
        except ValueError as err:
            print("ERROR = ",err.args)
            nro_week = -1
        '''
        nro_week = find_first_number(mod_name)
        logging.debug(f"nro_week = {nro_week}")
        return nro_week

    def configure(self, w_from, w_to, action="R"):
        #idx = 0
        for mod in self.get_modules():
            #print(mod)
            if (mod["name"].upper().startswith(KEY_MOD_1) or mod["name"].upper().startswith(KEY_MOD_2) ) :
                #idx += 1
                nro_week = self.get_nro_week(mod["name"])
                if  w_from <= nro_week <= w_to :
                    print(f"\n====> [{mod['position']}] : {mod['name']} \n")
                    if action == "C": self.config_module(mod)    


class ModuleCourseCanvas(ModuleTemplateCourseCanvas):

    def __init__(self, course_id, template_name_meeting, template_name_record, url_class, access_token):
        super().__init__(course_id, access_token)
        self.template_name_meeting = template_name_meeting
        self.template_name_record = template_name_record
        self.url_class = url_class

    def create_external_url_module(self, mod_id, title, pos, url ):
        data = {'module_item[title]'        : title ,
                'module_item[type]'         : 'ExternalUrl',
                'module_item[position]'     : pos,
                'module_item[indent]'       : '1',
                'module_item[external_url]' : url,
                'module_item[new_tab]'      : 1}
        self.post_item(mod_id, data)

    def update_external_url_module(self, mod_id, item_id, url ):
        data = {'module_item[external_url]' : url}
        self.put_item(mod_id, item_id, data)

    def config_module_course(self, mod, first_date, nro_week):

        nro_session = "S{:02d}".format(nro_week)
        short_date_class = (first_date + timedelta(days = 7 * (nro_week-1))).strftime("%b-%d")

        mod_items = self.get_items(mod["id"])
        #print("ITEMS ===> " , pd.DataFrame(mod_items).head())
       
        if len(mod_items) > 0 :
            df = pd.DataFrame(mod_items)
            # Create link to conference
            item_lvc = df[df["title"] == LABEL_VIDEO_CONFERENCES]
            if len(item_lvc) == 1:
                #print(item_lvc)
                pos = item_lvc['position'].values[0]
                name_meeting = self.template_name_meeting.replace(TEMPLATE_SHORT_SESSION,nro_session)
                name_meeting = name_meeting.replace(TEMPLATE_SHORT_DATE_CLASS,short_date_class)
                print(name_meeting)
                item_nm = df[df["title"] == name_meeting ]
                if len(item_nm) == 0 : 
                    print("Dont exist label webconference")    
                    self.create_external_url_module(mod['id'], name_meeting , pos+1, self.url_class)
                elif len(item_nm) == 1 :
                    print("Update URL of label webconference")
                    self.update_external_url_module(mod['id'], item_nm["id"].values[0], self.url_class)

        # REFRESH : READ AGAIN BECAUSE POSITION CHANGE IN MODULE
        mod_items = self.get_items(mod["id"])
        #print("ITEMS ===> " , pd.DataFrame(mod_items).head())

        if len(mod_items) > 0 :
            df = pd.DataFrame(mod_items)
            # Create link to record
            item_lr = df[df["title"] == LABEL_RECORDS]
            if len(item_lr) == 1:
                pos = item_lr['position'].values[0]
                name_record = self.template_name_record.replace(TEMPLATE_SHORT_SESSION,nro_session)
                name_record = name_record.replace(TEMPLATE_SHORT_DATE_CLASS,short_date_class)
                print(name_record)
                item_nr = df[df["title"] == name_record ]
                if len(item_nr) == 0 : 
                    print("Dont exist label record")    
                    self.create_external_url_module(mod['id'], name_record , pos+1, TEMPLATE_RECORD_URL)
                
    def clean_module_course(self, mod, first_date, nro_week):
        flag = True
        mod_items = self.get_items(mod["id"])
        #print("ITEMS ===> " , pd.DataFrame(mod_items).head())
        #print("ITEMS ===> " , mod_items)

        for item in mod_items:
            if (item["title"].startswith("S0") or 
                item["title"].startswith("S1") or 
                #item["title"].startswith("https://") or 
                item["title"].startswith("Videoconferencia") or 
                item["title"].startswith("Grabaci") ) :
                flag = False
                print("DELETE ITEM ===> " , item["title"])
                self.delete_item_module(mod['id'], item["id"] )

        if flag : print("EMPTY ITEM TO DELETE")


    def configure(self, first_date, w_from, w_to, action="R"):
        super().configure(w_from, w_to, action)
        print("===============> Configure Link <================")
        for mod in self.get_modules():
            #print(mod)
            if (mod["name"].upper().startswith(KEY_MOD_1) or mod["name"].startswith(KEY_MOD_2) ) :
                #idx += 1
                nro_week = self.get_nro_week(mod["name"])
                if  w_from <= nro_week <= w_to :
                    print("\n====> [%s] : %s \n"%(mod["position"] , mod["name"]))
                    if action == "C": self.config_module_course(mod, first_date, nro_week)  
                    if action == "D": self.clean_module_course(mod, first_date, nro_week)  

