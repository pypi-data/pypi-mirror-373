from setuptools import setup, find_packages

setup(
    name='pymine-edu',
    version='0.1.0',
    author='Fash & Chubike',
    author_email='fashjr@icloud.com',  
    description='An interpretable, transparent, and educational data mining library built from scratch in pure Python.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fashjr/pymine',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.21',
        'pandas>=1.3',
    ],
    include_package_data=True,
    project_urls={
        'Documentation': 'https://github.com/fashjr/pymine/wiki',
        'Source': 'https://github.com/fashjr/pymine',
        'Bug Tracker': 'https://github.com/fashjr/pymine/issues',
    },
    keywords=[
        'data mining', 'machine learning', 'education', 'explainable ai',
        'classification', 'clustering', 'association rules', 'preprocessing',
        'python from scratch', 'interpretable ml', 'pure python'
    ]
)
