from setuptools import setup

setup(name='pymsb',
      version='0.1',
      packages=['pymsb'],
      entry_points={
          'console_scripts': [
              'py_msb_interpreter = pymsb.language.interpreter:main'
          ],
          'gui_scripts': [
              'pymsb = pymsb.__main__:main'
          ]
      }, requires=['requests']
      )
