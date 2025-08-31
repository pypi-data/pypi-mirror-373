from setuptools import setup
import sysconfig
from setuptools.command.install import install
import os

def get_site_packages_path():
    return sysconfig.get_path("purelib")


with open("README.md", encoding="utf-8") as f:
    readme = f.read()

class InstallWithPth(install):
    def run(self):
        super().run()
        site_packages = get_site_packages_path()
        pth_path = os.path.join(site_packages, "friendly_module_not_found_error.pth")
        with open(pth_path, "w", encoding="utf-8") as f:
            f.write("import friendly_module_not_found_error")

setup(
    name="friendly_module_not_found_error",
    version="0.2.2",
    author="Locked-chess-official",
    author_email="13140752715@163.com",
    description="change the message in ModuleNotFoundError",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Locked-chess-official/friendly_module_not_found_error",
    packages=["friendly_module_not_found_error"],
    include_package_data=True,
    python_requires=">=3.12",
    project_urls={
        "Bug Reports": "https://github.com/Locked-chess-official/friendly_module_not_found_error/issues",
        "Source": "https://github.com/Locked-chess-official/friendly_module_not_found_error"
    },
    package_data={
        "friendly_module_not_found_error": ["test/**"],
    },
    cmdclass={"install": InstallWithPth}
)
