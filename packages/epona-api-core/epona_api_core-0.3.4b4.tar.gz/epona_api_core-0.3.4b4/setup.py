
import io
import os

from setuptools import setup, find_packages

# Package metadata
NAME = "epona-api-core"
DESCRIPTION = "Epona API-Core"
EMAIL = "marcos@eponaconsultoria.com.br"
AUTHOR = "Antonio Marcos"
REQUIRES_PYTHON = ">=3.9.0"
VERSION = "0.3.4-beta.4"  # "0.4.0-beta.0"  # login por email

# Required packages
REQUIRED = [
    "fastapi==0.115.12",
    "asyncpg==0.30.0",
    "boto3==1.28.18",
    "jinja2==3.1.6",
    "openpyxl==3.1.5",
    "pydantic==2.11.4",
    "python-multipart==0.0.20",
    "pyjwt==2.10.1",
    "pyshp==2.3.1",
    "tortoise-orm==0.25.0",
    "passlib[bcrypt]==1.7.4",
]

current_dir = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as long-description
try:
    with io.open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
        long_description = f"\n{f.read()}"
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(current_dir, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=["epona", "epona.auth", "epona.pessoas", "epona.layers"],  # TODO: atencao aqui
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    setup_requires=['wheel']
)
