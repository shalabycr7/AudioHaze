from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='AudioHaze',
    version='0.2.1',
    package_dir={"": "AudioHaze"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shalabycr7/AudioHaze',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    license='MIT',
    author='Abdulrahman Shalaby',
    author_email='abdoshalaby.dev@gmail.com',
    keywords=['gui', 'audio'],
    install_requires=['numpy==1.24.1', 'scipy==1.10.0', 'matplotlib==3.6.3', 'pyttsx3==2.90', 'ttkbootstrap==1.10.1',
                      'Pillow==9.4.0', 'pydub==0.25.1'],
    python_requires='>=3.10',

    description='Simple GUI Application To Manipulate Audio Files By Modifying The Audio Wave Form And Display It '
                'Using Python'
)
