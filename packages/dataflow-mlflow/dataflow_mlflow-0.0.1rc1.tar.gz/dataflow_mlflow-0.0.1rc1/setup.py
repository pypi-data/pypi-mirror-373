from setuptools import setup, find_packages

mlflow_version = "3.1.1"

setup(
    name='dataflow-mlflow',
    version='0.0.1rc1',
    packages=find_packages(),
    author="Dataflow",
    description="MLflow customized for Dataflow",
    install_requires=[
        f'mlflow=={mlflow_version}'
    ],
    package_data={
        'mlflow': [
            'server/js/build/**/*',
        ]
    },
    include_package_data=True,
    url="https://github.com/Digital-Back-Office/dataflow-mlflow",
)