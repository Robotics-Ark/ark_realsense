from setuptools import setup, find_packages

setup(
    name="ark-realsense",
    version="0.1.0",
    description="Intel RealSense sensor integration for the Ark robotics stack",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyrealsense2",
        "numpy",
    ],
)
