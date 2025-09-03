from setuptools import setup, find_packages

setup(
    name="spark-sink-connector",
    version="0.11.3",
    description="A connector for reading data from Kafka and writing to S3 in Delta or Hudi format.",
    author="Navid",
    author_email="navid.farhadi@snapp.cab",
    url="https://gitlab.snapp.ir/navid.farhadi/spark-sink-connector",
    packages=find_packages(),
    install_requires=[
    ],
    python_requires=">=3.7",
)