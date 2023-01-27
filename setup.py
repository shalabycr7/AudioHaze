from setuptools import setup

setup(
    name='Audio-Signal-Processing-App-GUI-in-Python',
    version='0.1.1',
    packages=['AudioLib'],
    url='https://github.com/shalabycr7/Audio-Signal-Processing-App-GUI-in-Python',
    license='MIT',
    author='Abdulrahman Shalaby',
    author_email='abdoshalaby.dev@gmail.com',
    keywords=['gui', 'audio'],
    install_requires=['numpy==1.23.4', 'scipy==1.9.3', 'matplotlib==3.6.2', 'pyttsx3==2.90', 'ttkbootstrap==1.9.0',
                      'Pillow==9.3.0', 'pydub==0.25.1'],
    python_requires='>=3.10',

    description='Simple GUI Application To Manipulate Audio Files By Modifying The Audio Wave Form And Display It '
                'Using Python'
)
