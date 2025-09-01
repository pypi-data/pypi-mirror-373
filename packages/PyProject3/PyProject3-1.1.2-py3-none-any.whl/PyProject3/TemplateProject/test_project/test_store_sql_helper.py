import unittest
from PyProject3.TemplateProject.TemplateProject import settings
from PyProject3.TemplateProject.TemplateProject.widgets.QTreeWidget.MyQTreeWidget import test
from PyProject3.TemplateProject.TemplateProject.stores.test_sql_helper import test_helper


class TestMain(unittest.TestCase):
    def test_settings(self):
        print(settings.YAML_CONFIG)

    def testSpsToFbx(self):
        a = 0.00001
        b = 77
        c = True
        self.assertLess(a, 0.001, f'assert error: {a}>0.001')
        self.assertEqual(b, 77)
        self.assertTrue(c)

    def test_helper(self):
        test_helper()

    def test_qtree(self):
        test()
