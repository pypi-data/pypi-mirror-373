import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
     name='trex_apis',  
     version='1.6.17',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex APIs package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://bitbucket.org/lokjac/trex-apis",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'cryptography',
          'basicauth',
          'trex_conf',
          'trex_model',
          'trex_lib',
          'trex_program',
      ],
 )

