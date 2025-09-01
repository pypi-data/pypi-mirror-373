from setuptools import setup, find_packages
import os

# Ler o README.md do diretório pai
readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Ler requirements.txt do mesmo diretório
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(requirements_path, "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="django-vite-ssr",
    version="0.2.0",
    author="Lucas de Oliveira Neitzke",
    author_email="lucas.neitzke@ssys.com.br",
    description="Django integration for Vite Server-Side Rendering (SSR)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucas-neitzke-ssys/django-vite-ssr",
    packages=find_packages(where='..'),  # Procurar pacotes no diretório pai
    package_dir={'': '..'},  # O diretório raiz para encontrar pacotes é o pai
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)