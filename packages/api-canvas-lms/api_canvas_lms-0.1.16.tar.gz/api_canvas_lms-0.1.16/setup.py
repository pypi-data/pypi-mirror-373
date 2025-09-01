from setuptools import setup, find_packages

setup(
    name='api_canvas_lms',
    version='0.1.16',
    package_data={'api_canvas_lms': ['files/*.*']}, 
    packages=find_packages(),
    author='Jaime Gomez',
    author_email="jgomezz@gmail.com",
    description='Una biblioteca de Python para Canvas LMS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jgomezz/api_canvas_lms',

)


