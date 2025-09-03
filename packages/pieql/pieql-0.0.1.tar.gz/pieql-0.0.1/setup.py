from setuptools import setup
from setuptools import find_packages


with open('requirements.txt', 'r') as f:
    requirements = f.read()


setup(
    name='pieql',
    version='0.0.1',
    python_requires=f'>=3.6',
    description='QL wrapper on top of existing FastAPI web service',
    url='https://github.com/PieDataLabs/pieql.git',
    author='George Kasparyants',
    author_email='gkasparyants@gmail.com',
    license="""
Copyright 2025 George Kasparyants
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """,
    packages=find_packages(include=['pieql', 'pieql.*']),
    install_requires=requirements,
    zip_safe=True,
    include_package_data=True,
    exclude_package_data={'': ['notebooks']},
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6"
    ],
)
