
import setuptools

setuptools.setup(

    name='py2be',
    version='0.0.3',

    author='Matt Wilson',
    author_email='matthew@synesis.com.au',
    classifiers=[

        'Intended Audience :: Developers',
        "License :: OSI Approved :: BSD License",
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    description='Simple Python library determining whether strings indicate truey or falsy values',
    keywords='configuration environment string traits',
    license='BSD-3-Clause',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=[
        'py2be',
        'py2be/internal',
        'examples',
        'tests',
    ],
    url='https://github.com/synesissoftware/diagnosticism.Python',
)

