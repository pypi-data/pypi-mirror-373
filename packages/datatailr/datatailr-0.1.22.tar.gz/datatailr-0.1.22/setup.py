from datatailr import __version__  # type: ignore
from setuptools import find_packages, setup

setup(
    name="datatailr",
    version=__version__,
    packages=find_packages(where="src", exclude=["test_module", "test_module.*"]),
    package_dir={"": "src"},
    data_files=[
        (
            "/datatailr/sbin",
            [
                "src/sbin/datatailr_run.py",
                "src/sbin/datatailr_run_batch.py",
                "src/sbin/datatailr_run_app.py",
                "src/sbin/datatailr_run_excel.py",
                "src/sbin/datatailr_run_service.py",
            ],
        )
    ],
)
