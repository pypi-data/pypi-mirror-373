from setuptools import setup, find_packages
import os

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'textom', 'version.py')
    with open(version_file) as f:
        # This will read the version from the version.py file
        exec(f.read())
    return locals()['__version__']

setup(
    name="TexTOM",          
    version=get_version(),       
    author="Moritz Frewein, Marc Allain, Tilman Gruenewald",
    author_email="textom@fresnel.fr",
    description="A program for texture simulations.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.fresnel.fr/textom/textom.git", 
    packages=find_packages(), 
    include_package_data=True,
    package_data={
        "textom": [
        "ressources/symmetrizedHSH/output/*",
        "ressources/*.txt",
        "input/*.py",
        "documentation/functions/*.tex",
        "documentation/introduction.tex",
        "documentation/textom_documentation.tex",
        "documentation/textom_documentation.pdf",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9, <=3.13',
    install_requires=["mumott >= 2.0, <=2.2", 
                      "pyfai >=2023, <=2025.1", 
                      "orix >= 0.13.0, <=0.13.3", 
                      "psutil==7.0",
                      "ase==3.25.0",
                      "ipython", 
    ],
    entry_points={
        "console_scripts": [
            "textom=textom.entries:main",
            "textom_config=textom.entries:config",
            "textom_documentation=textom.entries:documentation",
        ]
    },
)