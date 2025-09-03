from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='kozhindev_clearml_wrapper',
  version='0.0.1',
  author='YVoskanyan',
  author_email='yuvoskanyan@team.kozhin.dev',
  description='Wrapper over clearml, developed by ML team of KozhinDev company',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=['clearm>=2.0.2'],
  classifiers=[
    'Programming Language :: Python :: 3.12',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='clearml-wrapper clearml wrapper',
  python_requires='>=3.9'
)