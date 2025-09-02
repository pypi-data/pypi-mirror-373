import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='trex-web',  
     version='1.0.3',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex web package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     packages=setuptools.find_packages(),
     #package_data={'': ['templates/*', 'static/*.txt']},
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'flask',
          'Jinja2',
          'MarkupSafe',
          'phonenumbers',
          'requests',
          'testfixtures',
          'flask-babel',
          'Flask-CORS',
      ]
 )




