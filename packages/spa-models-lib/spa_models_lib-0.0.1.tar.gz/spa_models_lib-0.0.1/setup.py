from setuptools import setup, find_packages
from pathlib import Path

readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else ""

src_pkgs = find_packages(where="src")
prefixed = [f"spa_models_lib.src.{p}" for p in src_pkgs]

packages = ["spa_models_lib", "spa_models_lib.src"] + prefixed
setup(
    name='spa-models-lib',
    version='0.0.1',
    packages=packages,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires=">=3.11",
    package_dir={
        "spa_models_lib": ".",
        "spa_models_lib.src": "src",
    },
    include_package_data=True,
)
