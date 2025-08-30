from setuptools import setup, find_packages

setup(
    name="PPTE",
    version="0.5.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "biopython",
        "pysam"
    ],
    entry_points={
        "console_scripts": [
            "ppte=ppte.__main__:main"
        ]
    },
    description="PPTEs: A Pangenome Polymorphic Transposable Elements simulation toolkit",
    long_description="PPTEs is a toolkit to simulate and analyze polymorphic transposable elements across genomes, supporting TE pool building, real TE processing, pTE simulation, and VCF comparison.",
    long_description_content_type="text/markdown",
    author="JIAN MIAO",
    author_email="miaojian6363@gmail.com",
    url="https://github.com/yourusername/ppte",  
    classifiers=[               
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
