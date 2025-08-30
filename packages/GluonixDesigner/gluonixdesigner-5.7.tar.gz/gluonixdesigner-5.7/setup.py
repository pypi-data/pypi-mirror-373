from setuptools import setup, find_packages

setup(
    name="GluonixDesigner",
    version="5.7",
    description="A GUI Designer with drag-and-drop features.",
    author="Nucleon Automation",
    author_email="jagroop@nucleonautomation.com",
    packages=find_packages(),
    install_requires=[
        "pillow>=6.0.0",
        "requests>=2.22.0"
    ],
    entry_points={
        "console_scripts": [
            "GluonixDesigner = GluonixDesigner.Designer:main",
            "Gluonix = GluonixDesigner.Designer:main"
        ]
    },
    include_package_data=True,
    package_data={
        "GluonixDesigner": ["Data/**/*"],
    },
)

'''
python -m build --sdist
twine upload dist/*
pip install dist/GluonixDesigner-2.5.tar.gz
GluonixDesigner
'''