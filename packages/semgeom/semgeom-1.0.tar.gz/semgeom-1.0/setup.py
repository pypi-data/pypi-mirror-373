from setuptools import setup, find_packages

setup(
    name='semgeom',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
        "pandas",
    ],
    extras_require={
        "viz": ["plotly", "seaborn"],
        "models": ["sentence-transformers"],
        "spatial": ["alphashape", "shapely"]
    },
    author="Alina Topper",
    description="Semantic geometry tools — projection axes, fields and visualizations",
    license="MIT",
)
