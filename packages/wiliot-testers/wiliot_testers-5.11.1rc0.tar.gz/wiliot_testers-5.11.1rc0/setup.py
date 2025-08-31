import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='wiliot_testers',
                 use_scm_version={
                     'git_describe_command': "git describe --long --tags --match [0-9]*.[0-9]*.[0-9]*",
                     'write_to': "wiliot_testers/version.py",
                     'write_to_template': '__version__ = "{version}"',
                     'root': ".",
                 },
                 setup_requires=['setuptools_scm'],
                 author='Wiliot',
                 author_email='support@wiliot.com',
                 description="A library for interacting with Wiliot's Testers app",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url='',
                 project_urls={
                     "Bug Tracker": "https://WILIOT-ZENDESK-URL",
                 },
                 license='MIT',
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 packages=setuptools.find_packages(),
                 # add all support files to the installation
                 package_data={"": ["*.*"]},
                 install_requires=[
                     'setuptools_scm',
                     'pyqtgraph',
                     'PyQt5-sip==12.9.0; python_version < "3.11"',
                     'PyQt5-sip; python_version >= "3.11"',
                     'PyQt5==5.15.6; python_version < "3.11"',
                     'PyQt5; python_version >= "3.11"',
                     'dash<=2.18.2',
                     'dash-bootstrap-components',
                     'dash-daq',
                     'wiliot-api>=4.10.12',
                     'wiliot-core>=5.11.1',
                     'wiliot-tools>=4.11.1',
                     'wiliot-test-equipment>=1.0.1',
                 ],
                 zip_safe=False,
                 python_requires='>=3.6',
                 include_package_data=True,
                 )
