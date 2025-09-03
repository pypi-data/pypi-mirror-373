from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="keymint",
    version="1.0.0",
    author="KeyMint",
    author_email="admin@keymint.dev",
    description="Official Python SDK for KeyMint license management with comprehensive API coverage.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keymint-dev/keymint-python",
    project_urls={
        "Bug Reports": "https://github.com/keymint-dev/keymint-python/issues",
        "Source": "https://github.com/keymint-dev/keymint-python",
        "Documentation": "https://docs.keymint.dev/sdks/python",
        "Homepage": "https://keymint.dev",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="keymint license licensing api sdk drm software-licensing",
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.25.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'flake8',
        ],
    },
)
