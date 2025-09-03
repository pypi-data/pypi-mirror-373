from kitconcept.core import __version__
from kitconcept.core.utils import packages as pkg_utils

import pytest


class TestUtilsPackages:
    @pytest.mark.parametrize(
        "package_name,expected",
        [
            ("kitconcept.core", __version__),
            ("kitconcept.core.testing", __version__),
            ("", "-"),
        ],
    )
    def test_package_version(self, package_name: str, expected: str):
        result = pkg_utils.package_version(package_name)
        assert result == expected
