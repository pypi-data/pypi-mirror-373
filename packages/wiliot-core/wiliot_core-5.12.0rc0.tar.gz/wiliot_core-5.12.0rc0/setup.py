import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='wiliot_core',
                 use_scm_version={
                     'git_describe_command': "git describe --long --tags --match [0-9]*.[0-9]*.[0-9]*",
                     'write_to': "wiliot_core/version.py",
                     'write_to_template': '__version__ = "{version}"',
                     'root': ".",
                 },
                 setup_requires=['setuptools_scm'],
                 author='Wiliot',
                 author_email='support@wiliot.com',
                 description="A library for interacting with Wiliot's private core functions",
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
                 package_data={"": ["*.*"]},  # add all support files to the installation
                 install_requires=[
                     # fixed version for python 3.10 for cloud
                     'setuptools_scm==8.1.0; python_version >= "3.10" and python_version < "3.11"',
                     'pyserial==3.5; python_version >= "3.10" and python_version < "3.11"',
                     'pc_ble_driver_py==0.11.4; sys_platform != "linux" and python_version >= "3.10" and python_version < "3.11"',
                     'nrfutil==5.2.0; sys_platform != "linux" and python_version >= "3.10" and python_version < "3.11"',
                     'pandas==1.5.3; python_version >= "3.10" and python_version < "3.11"',
                     'numpy==1.24.4; python_version >= "3.10" and python_version < "3.11"',
                     'appdirs==1.4.4; python_version >= "3.10" and python_version < "3.11"',
                     # dynamic versions for all other python versions
                     'setuptools_scm',
                     'pyserial',
                     'pc_ble_driver_py; sys_platform != "linux" and python_version < "3.11"',
                     'nrfutil; sys_platform != "linux" and python_version < "3.11"',
                     'pandas',
                     'numpy>=1.20.0,<2; python_version < "3.11"',
                     'numpy>2; python_version >= "3.11"',
                     'appdirs'
                 ],
                 zip_safe=False,
                 python_requires='>=3.6',
                 include_package_data=True,
                 )
