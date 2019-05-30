import os
import tempfile
import unittest

from bakker.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp_config_dir = tempfile.TemporaryDirectory()
        class TestConfig(Config):
            CONFIG_FILE = os.path.join(self.tmp_config_dir.name, 'config.json')
        self.TestConfig = TestConfig

    def testSetItem(self):
        config = self.TestConfig()
        config['this.is.test'] = 'string'
        config['another.test'] = 'abc'
        with self.assertRaises(AssertionError):
            config['another.test'] = 123

    def testGetItem(self):
        self.testSetItem()
        config = self.TestConfig()
        self.assertEqual(config['this.is.test'], 'string')
        self.assertEqual(config['another.test'], 'abc')
        with self.assertRaises(KeyError):
            tmp = config['this.is.nokey']
        with self.assertRaises(KeyError):
            tmp = config['this.is']

    def testDelItem(self):
        config = self.TestConfig()
        config['path.to.value'] = 'value1'
        config['path.to.other_value'] = 'value2'
        config['path.2'] = 'value3'

        self.assertEqual(config['path.to.value'], 'value1')
        del config['path.to.value']
        with self.assertRaises(KeyError):
            tmp = config['path.to.value']

        self.assertEqual(config['path.to.other_value'], 'value2')
        del config['path.to.other_value']
        with self.assertRaises(KeyError):
            tmp = config['path.to.other_value']

        self.assertEqual(config['path.2'], 'value3')
        del config['path.2']
        with self.assertRaises(KeyError):
            tmp = config['path.2']

    def tearDown(self):
        self.tmp_config_dir.cleanup()
