# Third Party
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="squarelet_auth",  # Replace with your own username
    version="0.1.11",
    author="Mitchell Kotler",
    author_email="mitch@muckrock.com",
    description="Django authentication against the MuckRock user service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muckrock/squarelet-auth/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "celery",
        "django",
        "requests",
        "social-auth-core[openidconnect]",
    ],
    python_requires=">=3.6",
)
