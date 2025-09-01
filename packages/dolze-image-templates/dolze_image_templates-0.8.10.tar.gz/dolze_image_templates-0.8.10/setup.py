from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dolze-image-templates",
    version="0.1.2",
    author="Dolze Team",
    author_email="support@dolze.com",
    description="A package for generating Dolze templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dolze-templates",
    packages=find_packages(),
    package_data={
        "dolze_image_templates": ["templates/*", "fonts/*"],
    },
    install_requires=[
        "Pillow>=9.0.0",
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
