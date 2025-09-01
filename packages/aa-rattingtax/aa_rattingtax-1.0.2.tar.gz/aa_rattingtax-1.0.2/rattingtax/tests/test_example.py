"""
Example Test
"""

# Django
from django.test import TestCase


class TestExample(TestCase):
    """
    TestExample
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Test setup
        :return:
        :rtype:
        """

        super().setUpClass()

    def test_rattingtax(self):
        """
        Dummy test function
        :return:
        :rtype:
        """

        self.assertEqual(True, True)
