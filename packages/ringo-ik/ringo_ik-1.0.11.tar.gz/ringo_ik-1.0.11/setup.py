import platform
import glob
import ntpath
import os
from setuptools import setup

# OS specifics
CUR_OS = platform.system()
SHAREDOBJ_TEMPLATE = {
    'Windows': "ringo_base.cp{py_ver}-win_amd64.pyd",
    'Linux': "ringo_base.cpython-{py_ver}*-x86_64-linux-gnu.so",
}

# assert CUR_OS in ['Linux',
#                   'Windows'], "Only Linux and Windows platforms are supported"
assert CUR_OS == 'Linux', "Only Linux platform is currently supported 🤗"

# Python version specifics
python_version_tuple = platform.python_version_tuple()
py_ver = int(f"{python_version_tuple[0]}{python_version_tuple[1]}")

ringo_so_list = glob.glob(
    os.path.join('./ringo', SHAREDOBJ_TEMPLATE[CUR_OS].format(py_ver=py_ver)))
assert len(ringo_so_list) == 1
ringo_object_name = ntpath.basename(ringo_so_list[0])

for file in glob.glob('./ringo/*.pyd') + glob.glob('./ringo/*.so'):
    if ntpath.basename(file) != ringo_object_name:
        os.remove(file)

if CUR_OS == 'Windows':
    ADDITIONAL_FILES = ['*.dll']
elif CUR_OS == 'Linux':
    ADDITIONAL_FILES = []


def all_py(dir='.', exts=('.py', '.pyi')):
    result = []
    for root, _, files in os.walk(dir):
        for file in files:
            if any(file.endswith(ext) for ext in exts):
                result.append(
                    os.path.join(
                        *(os.path.join(root, file).split(os.sep)[1:])))
    return result


INSTALL_MCRLIB = True

packages = ['ringo']
package_data = {
    'ringo': [
        ringo_object_name,
        *all_py('ringo'),  # All python files
        *all_py('ringo', exts=('.xyz', )),  # Structures for built-in testing
        *all_py('ringo', exts=('.sdf', )),  # Structures for built-in testing
        *ADDITIONAL_FILES,
    ]
}
install_requires = [
    'numpy',
    'networkx',
    'pydantic',
]

if INSTALL_MCRLIB:
    packages.append('mcr')
    install_requires.append('PyYAML')
    package_data['mcr'] = all_py('mcr')

setup(
    name='ringo_ik',
    version='1.0.11',
    author='Nikolai Krivoshchapov',
    python_requires=f'=={python_version_tuple[0]}.{python_version_tuple[1]}.*',
    install_requires=install_requires,
    platforms=['Linux'],
    packages=packages,
    package_data=package_data,
)
