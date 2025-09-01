from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wintop",
    version="1.0.1",
    author="Jingfeng Xia",
    author_email="xiajingfeng@gmail.com",
    description="Windows System Monitor like top command in Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jfxia/wintop",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.13",
    install_requires=[
        "psutil>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "wintop=wintop.wintop:main",
        ],
    },
    keywords="windows monitor system performance",
)