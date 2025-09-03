from setuptools import setup

setup(
   name='PyQuantimClient',
   packages=['PyQuantimClient'],
   package_dir={'PyQuantimClient': 'src'},
   version='2.0.51',
   description='Python client to access quantIM services',
   author='Daniel Velasquez',
   author_email='daniel.velasquez@sura-im.com',
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
   python_requires='>=3.7',
)
