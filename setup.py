from setuptools import setup, find_packages

setup(
    name="myfiglet",
    version="0.1.0.dev1",
    description="unhelpful wrappers for popular utilities",
    packages=["myfiglet"],
    python_requires=">=3.6",
    install_requires=["sh"],
    entry_points={
        "console_scripts": [
            "mytree = myfiglet.mytree:main",
            "myfiglet = myfiglet.myfiglet:main",
        ]
    },
)
