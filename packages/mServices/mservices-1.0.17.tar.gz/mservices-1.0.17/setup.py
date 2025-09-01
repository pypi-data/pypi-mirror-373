from setuptools import setup, find_packages

setup(
    name='mServices',
    version='1.0.17',  # Update version as needed
    description='Manage your responses',
    packages=find_packages(),  # Automatically finds the package (testAppResponse)
    author='Manojan',          # Add author name
    author_email='manojan.mano@gmail.com',
    install_requires=[],       # Add dependencies if any
    classifiers=[              # Optional: Add classifiers
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',   # Specify Python version compatibility
)