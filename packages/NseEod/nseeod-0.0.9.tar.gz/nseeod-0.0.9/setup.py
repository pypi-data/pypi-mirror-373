from setuptools import setup, find_packages

setup(
    name="NseEod",
    version="0.0.9",
    author="Prasad",
    description="A NSEEOD library to fetch NSE EOD data",
    packages=find_packages(),
    install_requires=["pandas", "requests", "numpy", "feedparser", "urllib3", "gspread", "oauth2client", "google-auth", "schedule", "pytz", "beautifulsoup4" , "xlrd", "openpyxl", "pyxlsb",],
    python_requires=">=3.8",
)