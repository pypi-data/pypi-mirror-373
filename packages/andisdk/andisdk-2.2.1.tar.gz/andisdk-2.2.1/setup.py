import setuptools
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename).replace("src/andisdk/", ""))
    return paths

dlls = package_files('src/andisdk/dlls')
setuptools.setup(
    name="andisdk",
    version="2.2.1",
    author="Technica Engineering",
    description="ANDi python package to interact with ANDi scripting features from stand alone python package",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    python_requires=">=3.0.0",
    install_requires=[
        "clr-loader>=0.2.5",
        "pythonnet>=3.0.1",
        "udsoncan>=1.14",
        "rich>=11.2",
        "lxml>=4.9.1",
        "canmatrix>=0.9.5",
        "ldfparser>=0.14.0",
        "python-can>=4.2.2"
    ],
    entry_points = {
        'can.interface': [
            'andisdk = andisdk.can:TechnicaBus'
        ]
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux"
    ],
    package_data={
        '': dlls + ['*.pyi', 'runtimeconfig.json', 'SmartBind-Server.WibuCmLif'],
    },
    py_modules=['andisdk'],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)
