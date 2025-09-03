from setuptools import setup, find_packages

setup(
    name="zarrier-python",
    version="1.1.5",
    author="homo-zhou",
    author_email="408088242@qq.com",
    url="http://127.0.0.1",
    description="Mass tools for computer vision projects",
    packages=find_packages(),
    install_requires=["numpy", "opencv-python", "tqdm"],
    entry_points={"console_scripts": []},
)

