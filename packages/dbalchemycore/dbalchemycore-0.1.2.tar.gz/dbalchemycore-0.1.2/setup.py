from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r', encoding='UTF-8') as f:
        return f.read()

setup(
    name='dbalchemycore',
    version='0.1.2',
    author='tktturik',
    author_email='tktturik@gmail.com',
    description='Asynchronous database library using SQLAlchemy Core with CRUD operations',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/tktturik/db-alchemy-core',
    packages=find_packages(),
    install_requires=[
        'SQLAlchemy==2.0.41',
        'pydantic==2.11.7',
        'pydantic-core==2.33.2',
        'annotated-types==0.7.0',
        'asyncpg==0.30.0',
        'typing-inspection==0.4.1',
        'typing_extensions==4.14.1',
        'alembic==1.16.4',
        'pydantic-settings==2.5.2'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='database async sqlalchemy postgresql crud alembic pydantic fastapi',
    project_urls={
        'Documentation': 'https://github.com/tktturik/db-alchemy-core'  
    },
    python_requires='>=3.8'
)