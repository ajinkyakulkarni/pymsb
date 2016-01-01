from setuptools import setup, find_packages

print("asdf",find_packages())

setup(name='pymsb',
      author='Simon Tang',
      url='https://github.com/Simon-Tang/pymsb',
      description="TODO",
      version='0.1.2',
      packages=find_packages(),
      install_requires=['requests', 'nose'],
      entry_points={
          'console_scripts': [
              'pymsb = pymsb:__main__.main']
      },
      package_data={
          '': ['*.xml', '*.ini'],
          'pymsb': ['*.sb'],
      },
      )
