#python setup.py sdist
# twine upload dist/*
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="for-django-projects",
    version="1.4.3",
    author="Jasmany Sanchez Mendez",
    author_email="jasmanysanchez97@gmail.com",
    description="Package of libraries for Django projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jasmanysanchez/for-django-projects",
    packages=setuptools.find_packages(),
    py_modules=['for_django_projects'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'Django>=2.2',
    ],
    include_package_data=True
)