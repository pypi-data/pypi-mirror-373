import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qinsilk-scm-openapi-sdk-py",
    version="1.1.3",
    author="Qinsilk",
    author_email="tech@qinsilk.com",
    description="Qinsilk SCM OpenAPI SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qinsilk/qinsilk-starter", # 实际的项目URL
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'python-dotenv',
    ],
) 