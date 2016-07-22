import unittest2 as unittest
import os
import datetime


class HouseKeeping(unittest.TestCase):

    def test_license_year(self):
        self.assertTrue(os.path.exists('LICENSE.txt'))
        now = datetime.datetime.now()
        current_year = datetime.datetime.strftime(now, '%Y')
        license_text = open('LICENSE.txt').read()
        expected_text = 'Copyright %s Danny Lawrence <dannyla@linux.com>' \
                        % current_year
        self.assertIn(expected_text, license_text)

    def test_pip_install(self):
        x = os.popen("pip uninstall graphitesend -y")
        print(x.read())
        y = os.popen("pip install -e .")
        print(y.read())
        pip_freeze_stdout = os.popen("pip freeze").read()
        self.assertIn("graphitesend", pip_freeze_stdout)
