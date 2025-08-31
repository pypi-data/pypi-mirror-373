import setuptools
from dunamai import Version

setuptools.setup(
    name="deepchecks-llm-client",
    version=Version.from_any_vcs().serialize(),
    include_package_data=True,
)
