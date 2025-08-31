from setuptools import setup, find_packages

# Baca isi README.md untuk long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="minitorch",
    version="0.5.1",
    packages=find_packages(),
    description="Lightweight deep learning library with autograd, Linear, LeakyReLU, MSE, and SGD.",  # ≤512 karakter
    long_description=long_description,
    long_description_content_type="text/markdown",  # Format README.md
    author="iyaz",
    author_email="gantengiyaz6@gmail.com",
    url="https://github.com/yourusername/minitorch",  # no account 
    install_requires=["numpy"],  # Dependensi
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Sesuaikan lisensi
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
