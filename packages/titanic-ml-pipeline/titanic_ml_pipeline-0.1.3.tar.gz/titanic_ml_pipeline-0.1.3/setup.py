from setuptools import setup, find_packages
from pathlib import Path
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")
# testingss2jsjs
setup(
    name="titanic-ml-pipeline",
    version="0.1.3",
    description="Pipeline Titanic con scikit-learn (SVD + LogisticRegression)",
    author="Diego Hernandez",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.5",
        "numpy>=1.23",
        "scikit-learn>=1.2",
        "seaborn>=0.13",
        "joblib>=1.3"
    ],
    entry_points={
        "console_scripts": [
            "titanic-train=titanic_ml_pipeline.main:main",
        ]
    },
    include_package_data=True,
)
