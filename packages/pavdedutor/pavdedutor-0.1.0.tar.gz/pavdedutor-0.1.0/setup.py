from setuptools import setup

with open("README.md", encoding="utf-8") as arq:
    readme = arq.read()

setup(
    name='pavdedutor',
    version='0.1.0',
    license='MIT',
    project_urls={
        'Documentação':'https://wmoural.github.io/pavdedutor/inicio/',
        'Repositório': 'https://github.com/wmoural/pavdedutor'
        },
    author=['Wellington Moura', 'Francisco Macedo'],
    author_email='pro.wmoura@gmail.com',
    description='Cálculo otimizado de valores deduzíveis para análise de patologias em pavimentos rígidos',
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='dnit pavimento norma ábaco rígido flexível',
    packages=['pavdedutor'],
    install_requires=['pandas', 'numpy', 'tabulate'],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)