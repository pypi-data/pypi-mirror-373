# # setup.py
# from setuptools import setup, find_packages

# setup(
#     name='autocleans',
#     version='0.1.0',
#     author='SUDIPTA BISWAS',
#     author_email='sudiptabiswas394@gmail.com',
#     description='An advanced and automated data cleaning toolkit for Python.',
#     long_description=open('README.md').read(),
#     long_description_content_type='text/markdown',
#     url='https://github.com/sudipta9749/autocleans',
#     packages=find_packages(),
#     include_package_data=True, # Important for including non-Python files
#     install_requires=[
#         'pandas>=1.3.0',
#         'numpy>=1.20.0',
#         'scikit-learn>=1.0.0',
#         'matplotlib>=3.4.0',
#         'seaborn>=0.11.0',
#         'jinja2>=3.0.0',
#     ],
#     classifiers=[
#         'Development Status :: 3 - Alpha',
#         'Intended Audience :: Developers',
#         'Intended Audience :: Science/Research',
#         'License :: OSI Approved :: MIT License',
#         'Programming Language :: Python :: 3.8',
#         'Programming Language :: Python :: 3.9',
#         'Programming Language :: Python :: 3.10',
#         'Topic :: Scientific/Engineering :: Information Analysis',
#         'Topic :: Software Development :: Libraries :: Python Modules',
#     ],
#     python_requires='>=3.8',
#     keywords='data cleaning, data preprocessing, machine learning, data science, automation',
# )


from setuptools import setup

# All configuration is now in pyproject.toml
# This file is kept for compatibility with older tools.
setup()