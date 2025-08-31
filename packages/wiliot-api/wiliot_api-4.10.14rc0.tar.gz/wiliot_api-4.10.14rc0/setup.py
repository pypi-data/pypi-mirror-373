import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='wiliot_api',
                 use_scm_version={
                     'git_describe_command': "git describe --long --tags --match [0-9]*.[0-9]*.[0-9]*",
                     'write_to': "wiliot_api/version.py",
                     'write_to_template': '__version__ = "{version}"',
                     'root': ".",
                 },
                 setup_requires=['setuptools_scm'],
                 author='Wiliot',
                 author_email='support@wiliot.com',
                 description="A library for interacting with Wiliot's private Cloud API",
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
                     'requests==2.32.4; python_version >= "3.10" and python_version < "3.11"',
                     'setuptools_scm==8.1.0; python_version >= "3.10" and python_version < "3.11"',
                     'sgqlc==16.3; python_version >= "3.10" and python_version < "3.11"',
                     'pyjwt==2.10.1; python_version >= "3.10" and python_version < "3.11"',
                     # dynamic versions for all other python versions
                     'requests',
                     'setuptools_scm',
                     'sgqlc',
                     'cryptography==36.0.0; python_version >= "3.9" and python_version < "3.10"',
                     'pyjwt>2'
                 ],
                 zip_safe=False,
                 python_requires='>=3.6',
                 include_package_data=True,
                 )
