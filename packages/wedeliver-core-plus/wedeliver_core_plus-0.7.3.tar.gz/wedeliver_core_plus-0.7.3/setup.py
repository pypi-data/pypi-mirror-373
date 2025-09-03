from setuptools import setup, find_namespace_packages

# reading long description from file
# with open('DESCRIPTION.txt') as file:
#     long_description = file.read()


# specify requirements of your package here
REQUIREMENTS = [
    "SQLAlchemy",
    "Flask-SQLAlchemy",
    "flask-marshmallow",
    "confluent-kafka",
    "requests",
    "python-dotenv",
]

# Some more details
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Internet",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
]

setup(
    name="wedeliver_core_plus",
    version="0.7.3",
    description="wedeliver_core_plus package",
    long_description="""# Markdown supported!\n\n* wedeliver core plus\n* List of features\n""",
    long_description_content_type="text/markdown",
    url="https://thrivve.me/",
    author="Iyad Alfarra",
    author_email="info@thrivve.me",
    license="MIT",
    packages=find_namespace_packages(
        include=["wedeliver_core_plus", "wedeliver_core_plus.*"]
    ),
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
)
