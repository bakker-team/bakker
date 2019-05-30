import os
import tempfile
import unittest

from bakker.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp_config_dir = tempfile.TemporaryDirectory()
        self.tmp_config_path = self.tmp_config_dir.name
        class TestConfig(Config):
            def __init__(self, file_path):
                self.CONFIG_FILE = file_path
                super().__init__()
        self.TestConfig = TestConfig

    def testSetItem(self):
        config_path = os.path.join(self.tmp_config_path, 'test_set_item_config.json')
        config = self.TestConfig(config_path)
        config['this.is.test'] = 'string'
        config['another.test'] = 'abc'
        with self.assertRaises(AssertionError):
            config['another.test'] = 123

    def testGetItem(self):
        config_path = os.path.join(self.tmp_config_path, 'test_get_item_config.json')
        config = self.TestConfig(config_path)
        config['this.is.test'] = 'string'
        config['another.test'] = 'abc'

        self.assertEqual(config['this.is.test'], 'string')
        self.assertEqual(config['another.test'], 'abc')
        with self.assertRaises(KeyError):
            tmp = config['this.is.nokey']
        with self.assertRaises(KeyError):
            tmp = config['this.is']

    def testDelItem(self):
        config_path = os.path.join(self.tmp_config_path, 'test_del_item_config.json')
        config = self.TestConfig(config_path)
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

    def testItems(self):
        config_path = os.path.join(self.tmp_config_path, 'test_items_config.json')
        config = self.TestConfig(config_path)
        config['first.path1'] = 'value1'
        config['first.path2'] = 'value2'
        config['second.123.value1'] = 'value3'
        config['second.123.value2'] = 'value4'
        config['third'] = 'value5'

        comparision_items = [
            ('first.path1', 'value1'),
            ('first.path2', 'value2'),
            ('second.123.value1', 'value3'),
            ('second.123.value2', 'value4'),
            ('third', 'value5'),
        ]
        items = list(config.items())
        self.assertCountEqual(comparision_items, items)

    def tearDown(self):
        self.tmp_config_dir.cleanup()
