from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class PostInstall(install):
    """Post-installation script to set executable permissions for scripts."""
    def run(self):
        install.run(self)
        install_dir = os.path.join(self.install_lib, 'dataflow', 'scripts')
        for filename in os.listdir(install_dir):
            if filename.endswith('.sh'):
                filepath = os.path.join(install_dir, filename)
                os.chmod(filepath, 0o755)

setup(
    name="dataflow-core",
    version="2.1.10",
    packages=find_packages(include=["dataflow", "dataflow.*", "authenticator", "authenticator.*"]),
    include_package_data=True,
    package_data={
        "dataflow": ["scripts/*.sh"],
    },
    install_requires=[
        'sqlalchemy',
        'boto3',
        'psycopg2-binary',
        'pymysql',
        'requests',
        'azure-identity',
        'azure-keyvault-secrets'
    ],
    author="Dataflow",
    author_email="",
    description="Dataflow core package",
    entry_points={
        'jupyterhub.authenticators': [
            'dataflow_authenticator = authenticator.dataflowhubauthenticator:DataflowHubAuthenticator',
        ],
    },
    cmdclass={
        'install': PostInstall,
    },
)
