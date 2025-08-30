from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='iLaplace',
  version='2.0.2',
  description="A minimal Python interface for computing inverse Laplace transforms using Talbot’s method — designed as a clean and practical wrapper around sympy & mpmath",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='',  
  author='Mohammad Hossein Rostami',
  author_email='MHRo.R84@GMAIL.Com',
  license='MIT', 
  classifiers=classifiers,
  keywords='laplace inverse, numerical inverse laplace transform, talbot method, mpmath, sympy, iLaplace',
  packages=find_packages(),
  install_requires=['mpmath','sympy']
)
