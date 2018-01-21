from setuptools import find_packages, setup

setup(
	name='django-drflog',
	version='0.0.1',
	packages=find_packages(),
    install_requires=(
                      'Pygments>=2.2.0',
    )
)
