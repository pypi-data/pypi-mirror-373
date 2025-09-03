from setuptools import setup, find_packages

version="0.0.3"

setup(
    name='dataflow-dbt',
    version='0.0.3rc1',
    packages=find_packages(),
    author="Dataflow",
    description="DBT customized for Dataflow",
    install_requires=[
        'dbt-core==1.9.3',
        'dbt-postgres==1.9.0'
    ],
    package_data={
        'dbt': [
            'dataflow_config/*',
        ]   
    },
    include_package_data=True,
    url="https://github.com/Digital-Back-Office/dataflow-dbt"
)