from setuptools import setup, find_packages
import byzh_core
setup(
    name='byzh_core',
    version=byzh_core.__version__,
    author="byzh_rc",
    description="byzh_core是byzh系列的核心库，包含了一些常用的工具函数和类。",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'wcwidth',
    ],
    entry_points={
        "console_scripts": [
            "b_zip=byzh_core.__main__:b_zip" # b_zip 路径
        ]
    },
)
