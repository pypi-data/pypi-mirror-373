import setuptools
import glob

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    #Application name and details
     name='trex_conf',
     description="TRex Configuration package",
     long_description=long_description,
     long_description_content_type="text/markdown",  
     url="https://bitbucket.org/lokjac/trex-conf",
     version='1.6.12',
     
     #Author details
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     
     #packages=setuptools.find_packages(),
     packages=setuptools.find_packages(),
     
     package_data={'': ['*.json','*.csv']},
     
     #include additional files
     #package_data = {
     #   # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.*'],
     #},
     
     include_package_data=True,
     
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
      ],
 )

