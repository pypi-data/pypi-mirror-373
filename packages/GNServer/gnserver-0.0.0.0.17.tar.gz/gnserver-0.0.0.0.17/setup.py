from setuptools import setup

name = 'GNServer'
filesName = 'GNServer'

setup(
    name=name,
    version='0.0.0.0.17',
    author="KeyisB",
    author_email="keyisb.pip@gmail.com",
    description=name,
    long_description = 'GW and MMB Project libraries',
    long_description_content_type= 'text/plain',
    url=f"https://github.com/KeyisB/libs/tree/main/{name}",
    include_package_data=True,
    package_data = {}, # type: ignore
    package_dir={'': f'{filesName}'.replace('-','_')},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
    license="MMB License v1.0",
    install_requires = ['aioquic', 'anyio', 'KeyisBClient', 'aiofiles', 'uvloop'],
)
