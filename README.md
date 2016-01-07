# pymsb
An open-source, cross-platform interpreter for the Microsoft Small Basic language.  

The goal is to create a more stable and bug-free implementation of the language than Microsoft's proprietary IDE, that will work in Windows, Mac OS X and Linux (Ubuntu, at the very least).  Currently, the interpreter works for a subset of the language features, with the most notable omission being multimedia support.

## Installation
PyMSB is currently being tested on Windows 7 and Linux Mint.  Mac OS X testing will wait until development is at least feature-complete on Windows and Linux.

1. Install Python 3.  
    * On Linux, use the command `sudo apt-get install python3` in the terminal.
    * On Windows, download the latest version of Python 3 from https://www.python.org/download/, and run the downloaded setup file.

2. Install PyMSB.
    * On Linux, open a terminal in the same folder as `setup.py` and run the command `sudo python3 setup.py install`.
    * On Windows, open Command Prompt with administrative permissions, navigate to the same folder as `setup.py` and run the command `python setup.py install`.
        - You may need to add `python` to the system PATH variable.

(More instructions to come soon...)

### Quick testing (in lieu of finished instructions)
After following steps #1 and #2 to install PyMSB, the following Python script will print `Hello World!`:

    import pymsb
    
    code = """
    TextWindow.WriteLine("Hello world!")
    """
    
    i = pymsb.Interpreter()
    i.execute_code(code)

Of course, future instructions will describe how to invoke the PyMSB interpreter as a standalone program without having to write a Python script, and be able to execute the contents of a file containing only Microsoft Small Basic code.

## Future
Efficiency.

Eventually, Small Basic could become a subset of another language that supports features like function arguments for user-defined functions.  This future language is tentatively named _Small Medium_.