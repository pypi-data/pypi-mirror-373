import os
import sys
import setuptools

repository = "https://git.w21.org/ni/jpylib/"
pkg_version = os.environ["PKG_VERSION"] or sys.exit("missing $PKG_VERSION env.")

with open("README.md", "r") as fh:
    # filter out the comment lines from the README
    description_lines = [
        l.replace("$__package_version$", pkg_version)
        for l in fh if not l.startswith("#")
    ]

setuptools.setup(
    name="jpylib-jyrgenn",
    version=pkg_version,
    author="Juergen Nickelsen",
    author_email="ni@w21.org",
    description=description_lines[0].strip(),
    long_description="".join(description_lines),
    long_description_content_type="text/markdown",
    url=repository,
    packages=setuptools.find_packages(),
    project_urls=dict(
        Documentation="{}/-/blob/v{}/doc/jpylib.md".format(repository, pkg_version),
        Source=repository,
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
