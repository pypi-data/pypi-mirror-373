from setuptools import setup, find_packages

setup(
    name="stepvision",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "matplotlib",
        "numpy"
    ],
    description="Explainable, step-by-step computer vision library",
    author="sumit kumar sharma",
    author_email="sharmasumitk877@gmail.com",
    url="https://github.com/sumit333/stepvision",
)
