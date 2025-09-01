from setuptools import setup, find_packages

setup(
    name="hwpwings",
    version="0.4.5",
    author="한파엑셀",
    author_email="hpxl0518@gmail.com",
    description="파이썬으로 한글 문서를 제어할 수 있는 두번째 라이브러리입니다.",
    url="https://www.youtube.com/@한파엑셀",
    packages=find_packages(include=["hwpwings", "hwpwings.*"]),
    python_requires=">=3.6",
    install_requires=[
        "pywin32>=302",
        "pandas>=1.0.0",
        "lxml>=4.0.0",
    ],
)
