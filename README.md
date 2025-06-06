# Atomic Red Team Runner - GUI Mode

Run Automic Red Team atomics with Graphical User Interface

![Alt text](UI/ART_Runner.jpg?raw=true "ART Runner")

## Build Environment For Windows
The tool will be build using Python 32-bit platform to be able to run on both Win32 and Win64 Windows OS

Note: Better to install Visual Studio 2015 with enabled C++ build environment. Some of the required python modules 
will be compiled during requirements installation using pip. 

1. Download and install Python 3.7.9 (choose 32-bit platform)
2. Install Python's Virtual Environment module
```sh
       pip install virtualenv
```
3. Create a python virtual environment
```sh
       python -m venv c:\virtualpython\PYTHON3.7.9-X32
```
4. Activate the python virtual environment
```sh
       c:\virtualpython\PYTHON3.7.9-X32\Scripts\activate.bat
```
5. Change folder to Automic_Red_Team_Runner source codes path
```sh
       cd C:\github\Atomic_Red_Team_Runner
```
6. Install the required modules
```sh
       pip install -r requirements.txt
```
7. Overwrite the original atomic_operator in Python Lib. The modified atomic_operator Lib is created fot this GUI runner.
```sh
    copy C:\github\Atomic_Red_Team_Runner\atomic_operator to C:\virtualpython\PYTHON3.7.9-X32\Lib\site-packages\atomic_operator
```
8. Run build.bat



| Software | Location |
| ------ | ------ |
| Python | [Python 32-bit][PlDb] |


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks!)

   [PlDb]: <https://www.python.org/downloads/windows/>