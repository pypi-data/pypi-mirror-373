from setuptools import setup

setup(
    name='bhp_pro',  # Lowercase, unique on PyPI
    version='1.0.8',
    py_modules=['bhp_pro'],  # Matches your filename
    entry_points={
        'console_scripts': [
            'bhp_pro = bhp_pro:main',  # CLI command: maps to bhp_pro.py:main()
        ],
    },
    author='ssskingsss12',
    author_email='smalls3000i@gmail.com',
    description='Web Enumeration Tool',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.12',
)

