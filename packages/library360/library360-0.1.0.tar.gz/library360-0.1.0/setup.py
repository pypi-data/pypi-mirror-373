from setuptools import setup, find_packages

setup(
    name="library360",                 # اسم پکیج در PyPI
    version="0.1.0",                   # نسخه پکیج
    author="Arash360",
    author_email="Arash360.ir@gmail.com",
    description="this module for manage library",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),           # تمام پوشه‌های پکیج رو پیدا می‌کنه
    python_requires=">=3.7",
    install_requires=[],                # وابستگی‌ها، اگر هست
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
