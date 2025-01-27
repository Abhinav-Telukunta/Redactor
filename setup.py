from setuptools import setup, find_packages

setup(
	name='project1',
	version='1.0',
	author='Vijay Abhinav Telukunta',
	authour_email='vtelukunta@ufl.edu',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)