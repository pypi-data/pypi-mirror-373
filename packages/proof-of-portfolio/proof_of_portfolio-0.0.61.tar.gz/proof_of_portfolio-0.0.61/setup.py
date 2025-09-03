from setuptools import setup
from setuptools.command.install import install
import os


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        if not (os.environ.get("CI") or os.environ.get("POP_SKIP_INSTALL")):
            try:
                from .proof_of_portfolio import main

                main()
            except Exception as e:
                print(f"Post-install setup failed: {e}")


setup(
    cmdclass={"install": PostInstallCommand},
)
