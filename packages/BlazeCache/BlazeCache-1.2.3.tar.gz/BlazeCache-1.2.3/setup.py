from setuptools import setup, find_packages
print("Found packages:", find_packages(where="src"))
setup(
    name="BlazeCache",
    version='1.2.3',
    packages=find_packages(where="src"),
    long_description=open('README.md').read(),  
    py_modules=["blazecache"],  # 包含 src/blazecache.py
    long_description_content_type='text/markdown',  
    package_dir={"": "src"},
    install_requires=[
        "semver",  
    ],
    classifiers=[
        'Programming Language :: Python :: 3',  # 支持 Python 3
        'License :: OSI Approved :: MIT License',  # MIT 许可证
        'Operating System :: OS Independent',  # 支持跨平台

    ]
)
