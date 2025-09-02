import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
    
with open('requirements.txt', 'r') as f:
    install_requires = f.readlines()

setuptools.setup(
    name='betpy',
    version='0.0.1',
    author='Bryan Brzycki',
    author_email='bryan@bryanbrzycki.com',
    description='Odds utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/predicting-stuff/betpy',
#     project_urls={
#         'Documentation': '',
#         'Source': ''
#     },
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
