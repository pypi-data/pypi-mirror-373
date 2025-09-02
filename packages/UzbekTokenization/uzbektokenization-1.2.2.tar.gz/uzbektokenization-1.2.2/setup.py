from setuptools import setup, find_packages

setup(
    name='UzbekTokenization',
    version='1.2.2',
    author='dasturbek',
    author_email='sobirovogabek0409@gmail.com',
    description='O‘zbek tilida matnni belgilarga, bo‘g‘inlarga, affikslarga, so‘zlarga, '
                'gaplarga va tinish belgilariga ajratish uchun mo‘ljallangan dastur.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ddasturbek/UzbekTokenization',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
