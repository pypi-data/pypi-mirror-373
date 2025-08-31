from setuptools import setup, find_packages

setup(
    name="pqcdualusb",
        version = "0.1.1",
    description="Enterprise-grade dual USB backup library with post-quantum cryptography protection for maximum security",
    author="Johnson Ajibi",
    author_email="johnsonajibi@example.com",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
