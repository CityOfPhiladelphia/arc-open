from distutils.core import setup

setup(name='ArcOpen',
	    version='1.0.2',
	    description='An ArcGIS toolbox to convert feature classes to open geodata formats',
	    author='City of Philadelphia',
	    author_email='data@phila.gov',
	    url='https://github.com/CityOfPhiladelphia/arc-open',
	    packages=['arc_open'],
	    package_dir={'arc_open': 'arc_open'},
	    package_data={'arc_open': ['../*.md', 'esri/toolboxes/*.*', './esri2open/*']}
	    )