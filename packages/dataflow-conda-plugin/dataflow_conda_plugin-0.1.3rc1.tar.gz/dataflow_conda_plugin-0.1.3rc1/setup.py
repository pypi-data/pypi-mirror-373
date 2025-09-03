from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class PostInstall(install):
    """Post-installation script to set executable permissions for scripts."""
    def run(self):
        install.run(self)
        install_dir = os.path.join(self.install_lib, 'plugin', 'scripts')
        for filename in os.listdir(install_dir):
            if filename.endswith('.sh'):
                filepath = os.path.join(install_dir, filename)
                os.chmod(filepath, 0o755)

setup(
    name="dataflow-conda-plugin",
    version='0.1.3rc1',
    entry_points={"conda": ["dataflow-conda-plugin = plugin.plugin"]},
    packages=find_packages(include=["plugin"]),
    package_data={'plugin': ['scripts/*.sh']},
    cmdclass={
        'install': PostInstall,
    },
)