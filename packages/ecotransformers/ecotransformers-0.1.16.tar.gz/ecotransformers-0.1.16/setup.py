from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='ecotransformers',   # PyPI project name
    version='0.1.16',
    description='Optimize LLM outputs and track emissions',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='',
    author_email='',
    url='https://github.com/viji123450/ecotransformers',
    license='MIT',
    packages=find_packages(),  # this will auto-detect ecotransformers/
    install_requires=[      
        'torch>=1.13.0',
        'transformers>=4.30.0',
        'codecarbon>=2.2.2',
        'evaluate>=0.4.0',
        'numpy>=1.24.0',
        'rouge_score>=0.1.2',
        'nltk>=3.8.0',
        'absl-py>=1.4.0'
    ],
    entry_points={
        'console_scripts': [
            'eco_transformer=ecotransformers.main:transformer',
        ],
    },
    python_requires='>=3.8',
)
