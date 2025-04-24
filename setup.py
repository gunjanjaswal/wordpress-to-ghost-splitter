from setuptools import setup, find_packages

setup(
    name="wordpress-to-ghost-splitter",
    version="1.0.0",
    author="Gunjan Jaswal",
    author_email="hello@gunjanjaswal.me",
    description="Split WordPress XML exports into smaller chunks for Ghost import",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gunjanjaswal/wordpress-to-ghost-splitter",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.0.0",
        "Werkzeug>=2.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "wp-ghost-split=wp_xml_splitter:main",
        ],
    },
)
