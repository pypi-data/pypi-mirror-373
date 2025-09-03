from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_adp_decidium',
    version='1.0.0',
    description='ADP Decidium wrapper from BrynQ',
    long_description='ADP Decidium wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'pandas>=2.2.0,<3.0.0',
        'pydantic>=2.5.0,<3.0.0',
        'pandera>=0.16.0,<1.0.0',
        'requests>=2.25.1,<3.0.0',
        'brynq-sdk-functions>=2.0.5'
    ],
    zip_safe=False,
)
