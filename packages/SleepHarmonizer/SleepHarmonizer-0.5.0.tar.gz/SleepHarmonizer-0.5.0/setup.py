import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SleepHarmonizer",
    version="v0.5.0"[1:],
    author="Franz Ehrlich",
    author_email="fehrlichd@gmail.com",
    description="A Plugin and stand alone tool to harmonize sleep related data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/sleep-is-all-you-need/sleep-harmonizer",
    packages=setuptools.find_packages(),
    package_data={"": ["*.yaml"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pyPhases",
        "pyPhasesRecordloader",
        "pyPhasesRecordloaderPhysionet",
        "pyPhasesRecordloaderSHHS",
        "pyPhasesRecordLoaderMrOS",
        "pyPhasesRecordloaderMESA",
        "phases",
        "numpy",
        "tqdm",
        "pydicom",
        "pyedflib",
    ],
    python_requires=">=3.5",
)
