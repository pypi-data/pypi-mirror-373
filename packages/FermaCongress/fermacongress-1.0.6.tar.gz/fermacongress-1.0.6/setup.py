from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()
    
setup(
    name='FermaCongress',
    version='1.0.6',
    author='Ferma Congress Team',
    author_email='hema.murapaka@zoomrx.com',
    license='MIT',
    description='A ZoomRx - Ferma Congress package for internal usage',
    long_description=readme,
    url = 'https://www.zoomrx.com/ferma/',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.7'
)