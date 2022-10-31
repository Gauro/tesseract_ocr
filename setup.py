# Author: Gaurav Ail (2022)
import setuptools

with open("README.md", "r") as f:
    lstr_long_description = f.read()

setuptools.setup(
    name='tesseract_ocr',
    version='1.0.0',
    description='Python Distribution Utilities',
    author='Gaurav Ail',
    author_email='ail.gaurav10@gmail.com',
    long_description=lstr_long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=['pandas==1.1.5', 'opencv-python==4.6.0.66', 'configparser==5.2.0', 'lxml==4.9.1',
                      'python-json-logger==2.0.4']
)
