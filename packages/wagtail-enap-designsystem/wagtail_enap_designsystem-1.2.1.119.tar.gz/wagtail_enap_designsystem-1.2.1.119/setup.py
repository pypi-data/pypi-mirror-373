from setuptools import setup, find_packages

setup(
    name='wagtail-enap-designsystem',
    version='1.2.1.119',
    description='Módulo de componentes utilizado nos portais ENAP, desenvolvido com Wagtail + CodeRedCMS',
    author='Renan Campos',
    author_email='renan.oliveira@enap.gov.br',
    long_description=open("README-use.md", encoding="utf-8").read(),
	long_description_content_type="text/markdown",
    packages=find_packages(include=["enap_designsystem", "enap_designsystem.*"]),
    package_dir={"": "."},
    package_data={
		"enap_designsystem": [
			"templates/**/*.html",
			"static/**/*.*",
		]
	},
    include_package_data=True,
    install_requires=[
        'django>=3.2',
        'wagtail==6.4',
        'coderedcms==4.1'
    ],
    s=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Wagtail',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
