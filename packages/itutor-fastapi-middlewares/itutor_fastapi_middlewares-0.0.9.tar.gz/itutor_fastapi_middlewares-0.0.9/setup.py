from setuptools import setup, find_packages

VERSION = '0.0.9' 
DESCRIPTION = 'Package for google sso login in FastAPI'
LONG_DESCRIPTION = 'Package for google sso login in FastAPI'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="itutor_fastapi_middlewares", 
        version=VERSION,
        author="Nicolas Acosta",
        author_email="nicolas.acosta@itutor.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        package_dir={'fastapi_middlewares': 'fastapi_middlewares'},
        include_package_data = True,
        package_data={'fastapi_middlewares': ['statics/*', 'itutor_google_sso/templates/*']},
        install_requires=[
            "Authlib>=1.3.1",
            "httpx>=0.23.0",
            "itsdangerous>=2.1.2",
            "jinja2>=3.1.6",
            "fastapi>=0.75.2",
        ],
        url="https://github.com/bcpitutor/fastapi_middlewares",
        keywords=['google-sso', 'fastapi'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
        ]
)