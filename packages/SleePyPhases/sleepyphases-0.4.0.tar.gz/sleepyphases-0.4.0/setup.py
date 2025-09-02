import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SleePyPhases",
    version="v0.4.0"[1:],
    author="Franz Ehrlich",
    author_email="fehrlichd@gmail.com",
    description="A framwork for creating deep learning pipelines for sleep data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/sleep-is-all-you-need/sleepyphases",
    packages=setuptools.find_packages(),
    package_data={"": ["*.yaml"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
      "SleepHarmonizer",
      "pyPhasesML",
      "phases"
    ],
    python_requires=">=3.5",
)
