from setuptools import setup, find_packages

setup(
    name="django-mailupy",
    version="0.1.0",
    description="Django app wrapping the MailUp Python client",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Lotrèk",
    author_email="dimmitutto@lotrek.it",
    url="https://github.com/lotrekagency/django-mailupy",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "Django>=4.0",
        "mailupy>=0.1.0"
    ],
    extras_require={
        "drf": ["djangorestframework>=3.12"]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
