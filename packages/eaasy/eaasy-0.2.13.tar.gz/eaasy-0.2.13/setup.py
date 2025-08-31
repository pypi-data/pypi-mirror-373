from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

setup(
    name='eaasy',
    version='0.2.13',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    author='Giuliano Errico',
    author_email='errgioul2@gmail.com',
    description='Build your e-commerce ea(a)sily',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ciulene/eaasy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)