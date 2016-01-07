from setuptools import setup, find_packages
import platform


def find_pyuserinput_requirements():
    # TODO: Verify that these values work across all supported platforms.
    plat = platform.system()
    if plat == "Windows":
        return ["pywin32", "pyHook"]
    if plat == "Darwin":  # This is actually Mac OS X.
        return ["pyobjc-framework-Quartz", "AppKit"]
    if plat == "Linux":
        return ["python3-xlib"]

setup(name='pymsb',
      author='Simon Tang',
      url='https://github.com/Simon-Tang/pymsb',
      description="TODO",
      version='0.1.2',
      packages=find_packages(),
      install_requires=['requests', 'nose', 'PyUserInput'] + find_pyuserinput_requirements(),
      entry_points={
          'console_scripts': [
              'pymsb = pymsb:__main__.main']
      },
      package_data={
          '': ['*.xml', '*.ini'],
          'pymsb': ['*.sb'],
      },
      )
