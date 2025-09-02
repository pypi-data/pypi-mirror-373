import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="p-template-generator",
    version="0.2.43",
    author="pengjun",
    author_email="mr_lonely@foxmail.com",
    description="temple tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=[],
    install_requires=[
        'requests',
        'Image',
        'protobuf',
        'imagesize',
        'urlparser',
        'Pillow',
        'p-template-res',
    ],
    dependency_links=[],
    entry_points={
        'console_scripts':[
            'template = template_generator.main:main'
        ]
    },
    python_requires='>=3.7',
)