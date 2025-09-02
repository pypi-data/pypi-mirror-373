import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='trex_analytic',  
     version='1.6.9',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex analytics package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://bitbucket.org/lokjac/trex-analytic",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'flask',
          'Jinja2',
          'requests',
          'google-oauth',
          'google-cloud-bigquery',
          'google-cloud-tasks',
          'flask-restful',
          'webargs',
      ]
 )



