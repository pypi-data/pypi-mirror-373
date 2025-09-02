from setuptools import setup, find_packages
from flake8_jira_ticket_checker.__version__ import __version__


# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


setup(
    name="flake8-jira-ticket-checker",
    version=__version__,
    description="Flake8 plugin to check JIRA ticket status",
    author="Nikita Lauer",
    author_email="lauernik@gmail.com",
    url="https://github.com/lauernik/flake8-jira-ticket-checker",
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        "flake8.extension": [
            "JTC = flake8_jira_ticket_checker.jira_checker:JiraTicketChecker",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    keywords="flake8 jira ticket checker linter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
