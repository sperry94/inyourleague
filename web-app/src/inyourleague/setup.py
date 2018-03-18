from setuptools import setup

setup(
    name="inyourleague",
    packages=["inyourleague"],
    include_package_data=True,
    install_requires=[
        'flask',
        'requests'
    ]
)