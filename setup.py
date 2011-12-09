from distutils.core import setup
import uniquify

setup(
    name='uniquify',
    py_modules=['uniquify'],
    description='Uniquify - '
    'get unique, short and easy-to-read names and paths',
    version=uniquify.__version__,
    long_description=uniquify.__doc__,
    author=uniquify.__author__,
    license=uniquify.__license__,
    url='https://github.com/tkf/uniquify',
    author_email='aka.tkf@gmail.com',
    keywords='text, unique',
    classifiers=[
        "Topic :: Text Processing",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        ],
    )
