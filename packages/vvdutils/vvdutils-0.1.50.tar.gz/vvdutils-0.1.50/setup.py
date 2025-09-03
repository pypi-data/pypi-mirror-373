from setuptools import find_packages, setup
import os

str_version = '0.1.50'

# 自动包含所有子包
packages = find_packages()

# 数据文件路径
assets_path = os.path.join('vvdutils', 'assets')
data_files = [
    (assets_path, [os.path.join(assets_path, f) for f in os.listdir(assets_path) 
     if f.endswith('.json') or f.endswith('.jpg')])
]

if __name__ == '__main__':

    setup(
        name='vvdutils',
        version=str_version,
        description='Commonly used function library by VVD',
        url='https://github.com/zywvvd/utils_vvd',
        author='zywvvd',
        author_email='zywvvd@mail.ustc.edu.cn',
        license='MIT',
        packages=packages,
        data_files=data_files,
        include_package_data=True,
        zip_safe=False,
        install_requires= ['numpy<2', 'opencv-python', 'numba', 'func_timeout', 'pypinyin','scikit-learn', 'pathlib2', 'tqdm', 'pytest', 'matplotlib', 'pandas', 'flask', 'shapely', 'pyproj', 'bson', 'scikit-image', 'rasterio', 'pyzmq', 'loguru', 'pygltflib'],
        python_requires='>=3.6')