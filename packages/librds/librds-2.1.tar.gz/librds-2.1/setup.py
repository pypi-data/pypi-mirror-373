from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
	readme = f.read()

setup(
		name="librds",
		version="2.01",
		author="KubaPro010",
		description='RDS Group Generator',
		long_description=readme,
		long_description_content_type='text/markdown',
		packages=find_packages(),
		url="https://github.com/KubaPro010/librds",
		install_requires=[],
		project_urls={
			'Source': 'https://github.com/KubaPro010/librds'
		},
		keywords=['radiodatasystem','rds','broadcast_fm'],
		classifiers=[
			"Intended Audience :: Education",
			"Intended Audience :: Telecommunications Industry",
			"Programming Language :: Python :: 3 :: Only",
			"Programming Language :: Python :: 3.10",
			"Development Status :: 5 - Production/Stable",
			"License :: OSI Approved :: GNU General Public License (GPL)",
		]
)