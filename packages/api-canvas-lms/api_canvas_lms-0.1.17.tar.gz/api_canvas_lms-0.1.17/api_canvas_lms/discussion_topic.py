""" 
Programa :  Discussion Topic module for Canvas
Fecha : 14/04/2024
Version : 1.0.0
Author : Jaime Gomez
"""

from .base import BaseCanvas
from .utils import clean_html

class DiscussionTopics(BaseCanvas):
    
    def __init__(self, course_id, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)
        # 
        self.course_id = course_id
        # CONNECTOR
        self.url_discussion_topics        = '<path>/courses/<course_id>/discussion_topics'
        self.url_discussion_posts         = '<path>/courses/<course_id>/discussion_topics/<topic_id>/entries'

    def get_topics(self):
        params = {
            'per_page': 100  # Maximum allowed per page
        }
        url = self.url_discussion_topics
        url = url.replace('<course_id>', self.course_id)
        return  super().get_all_pages(url, params)

    def get_posts(self, topic_id):
        params = {
            'per_page': 100  # Maximum allowed per page
        }
        url = self.url_discussion_posts
        url = url.replace('<topic_id>', topic_id)
        url = url.replace('<course_id>', self.course_id)
        return  super().get_all_pages(url, params)

    def get_entries(self):
        entries = []
        for topic in self.get_topics():
            topic_id = str(topic['id'])
            for post in self.get_posts(topic_id):
                entries.append({
                      'topic_id': topic_id,
                       'message': clean_html(post['message']),
                        'author': post['user_name'],
                    'created_at': post['created_at']
        })
                
        return entries


    def post(self, data):
        url = self.url_discussion_topics
        url = url.replace('<course_id>', self.course_id)
        return super().post(url, data)

    def create_topic(self, title, message):
        data = {'title'            : title ,
                'message'          : message,
                'discussion_type'  : "threaded",
                'published'        : 'false'}
        return self.post(data)