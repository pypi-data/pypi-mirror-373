"""
Setup configuration for Cyber Wolf Hunter package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cyber-wolf-hunter",
    version="1.0.1",
    author="S.Tamilselvan",
    author_email="tamilselvanreacher@gmail.com",
    description="Comprehensive website vulnerability scanner with multi-threading and HTML reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tamilselvan-S-Cyber-Security/cyber-wolf-hunter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "jinja2>=3.0.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    include_package_data=True,
    package_data={
        "wolf_hunter": ["templates/*.html"],
    },

    keywords="cybersecurity, vulnerability scanner, web security, penetration testing, security assessment",
    project_urls={
        "Bug Reports": "https://github.com/Tamilselvan-S-Cyber-Security/cyberwolf-hunter/issues",
        "Source": "https://github.com/Tamilselvan-S-Cyber-Security/cyber-wolf-hunter",
        "Documentation": "https://github.com/Tamilselvan-S-Cyber-Security/cyber-wolf-hunter/wiki",
        "Portfolio": "https://tamilselvan-portfolio-s.web.app/",
    },
)
