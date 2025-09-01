import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
     name='trex_lib',  
     version='1.6.14',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex Core library package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://bitbucket.org/lokjac/trex-lib",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'python-dateutil',
          'cryptography',
          'urllib3',
          'phonenumbers',
          'email_validator',
          'Flask-Script',
          'basicauth',
          #'protobuf==3.17.3',
          #'pyopenssl>=22.0.0',
          #'firebase-admin>=5.3.0',
          #'google-cloud-storage==2.0.0',
          #'google-cloud-tasks==2.8.1',
          #'google-auth==1.35.0',
          #'google-cloud-core==1.7.3',
          #'flask-babel',
          #'flask-restful>=0.3.9',
          #'flask-wtf',
          #'six',
      ],
     
 )

