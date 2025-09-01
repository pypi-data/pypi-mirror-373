from setuptools import setup, find_packages
import versioneer
# from glob import glob

# base_data_files=glob('MasterLattice/*/*', recursive=True)
# data_files = []
# for df in base_data_files:
#     if os.path.isfile(df):
        # df = df.replace('\\','/')
        # print((os.path.dirname(df), df))
        # data_files.append((os.path.dirname(df), df))
# print(data_files)
# exit()
with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = []

setup(
    name="MasterLattice",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="James Jones",
    author_email="james.jones@stfc.ac.uk",
    description="Files defining the CLARA lattice",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.stfc.ac.uk/jkj62/masterlattice",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
	include_package_data=True,
)
