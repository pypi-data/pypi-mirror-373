from setuptools import setup, find_packages
# import versioneer
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
    name="SimCodes",
    use_scm_version=True,  # <--- this replaces versioneer
    setup_requires=["setuptools_scm"],  # ensures setuptools_scm is available during build
    packages=find_packages(),
    package_dir={"": "."},
    include_package_data=True,
    python_requires=">=3.10",
    author="James Jones",
    author_email="james.jones@stfc.ac.uk",
    description="Simulations codes for use with SimFrame",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/astec-stfc/simcodes",
    install_requires=requirements,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
