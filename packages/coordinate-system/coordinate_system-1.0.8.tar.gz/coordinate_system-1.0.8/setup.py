from setuptools import setup, find_packages

setup(
    name='coordinate_system',  # 包名
    version='1.0.8',  # 版本号
    packages=find_packages(),  # 自动找到包
    include_package_data=True,  # 包含非Python文件
    description='A package for coordinate systems',  # 简短描述
    long_description=open('README.md').read(),  # 详细描述
    long_description_content_type='text/markdown',
    author='romeosoft',
    author_email='18858146@qq.com', 
    url='https://github.com/panguojun/Coordinate-System',
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='==3.8.*',
    install_requires=[],
    package_data={
        'coordinate_system': ['coordinate_system.pyd'],
    },
    platforms=['Windows'],
)