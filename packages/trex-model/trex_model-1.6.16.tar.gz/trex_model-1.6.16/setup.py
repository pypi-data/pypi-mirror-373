import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='trex_model',  
     version='1.6.16',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex database module package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://bitbucket.org/lokjac/trex-model",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     include_package_data = True,
     install_requires=[            
          'google-cloud-firestore',
          'google_cloud_datastore',
          'google-cloud-ndb',
          'six',
          'trex-lib',
          'flask-login==0.6.2',
          #'ordered-set==4.1.0',
          
      ]
 )

