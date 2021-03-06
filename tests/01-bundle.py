#!/usr/bin/env python3

import amulet
import json
import os
import unittest
import yaml


class TestBundle(unittest.TestCase):
    bundle_file = os.path.join(os.path.dirname(__file__), '..', 'bundle.yaml')

    @classmethod
    def setUpClass(cls):
        cls.d = amulet.Deployment(series='trusty')
        with open(cls.bundle_file) as f:
            bun = f.read()
        bundle = yaml.safe_load(bun)
        cls.d.load(bundle)
        cls.d.setup(timeout=1800)
        cls.d.sentry.wait_for_messages({'pig': 'ready (mapreduce)'}, timeout=1800)
        cls.hdfs = cls.d.sentry['namenode'][0]
        cls.yarn = cls.d.sentry['resourcemanager'][0]
        cls.slave = cls.d.sentry['slave'][0]
        cls.pig = cls.d.sentry['pig'][0]

    def test_components(self):
        """
        Confirm that all of the required components are up and running.
        """
        hdfs, retcode = self.hdfs.run("pgrep -a java")
        yarn, retcode = self.yarn.run("pgrep -a java")
        slave, retcode = self.slave.run("pgrep -a java")
        pig, retcode = self.pig.run("pgrep -a java")

        # .NameNode needs the . to differentiate it from SecondaryNameNode
        assert '.NameNode' in hdfs, "NameNode not started"
        assert '.NameNode' not in yarn, "NameNode should not be running on yarn-master"
        assert '.NameNode' not in slave, "NameNode should not be running on compute-slave"
        assert '.NameNode' not in pig, "NameNode should not be running on pig"

        assert 'ResourceManager' in yarn, "ResourceManager not started"
        assert 'ResourceManager' not in hdfs, "ResourceManager should not be running on hdfs-master"
        assert 'ResourceManager' not in slave, "ResourceManager should not be running on compute-slave"
        assert 'ResourceManager' not in pig, "ResourceManager should not be running on pig"

        assert 'JobHistoryServer' in yarn, "JobHistoryServer not started"
        assert 'JobHistoryServer' not in hdfs, "JobHistoryServer should not be running on hdfs-master"
        assert 'JobHistoryServer' not in slave, "JobHistoryServer should not be running on compute-slave"
        assert 'JobHistoryServer' not in pig, "JobHistoryServer should not be running on pig"

        assert 'NodeManager' in slave, "NodeManager not started"
        assert 'NodeManager' not in yarn, "NodeManager should not be running on yarn-master"
        assert 'NodeManager' not in hdfs, "NodeManager should not be running on hdfs-master"
        assert 'NodeManager' not in pig, "NodeManager should not be running on pig"

        assert 'DataNode' in slave, "DataServer not started"
        assert 'DataNode' not in yarn, "DataNode should not be running on yarn-master"
        assert 'DataNode' not in hdfs, "DataNode should not be running on hdfs-master"
        assert 'DataNode' not in pig, "DataNode should not be running on pig"

    def test_hdfs_dir(self):
        """Smoke test validates mkdir, ls, chmod, and rm on the hdfs cluster."""
        uuid = self.d.action_do(self.hdfs['unit_name'], 'smoke-test')
        result = json.loads(self.d.action_fetch(uuid))
        if (result['status'] != "completed"):
            error = "HDFS smoke-test failed: %s" % result['output']
            amulet.raise_status(amulet.FAIL, msg=error)
        else:
            amulet.raise_status(amulet.PASS, msg="HDFS smoke-test successful")

    def test_yarn_mapreduce_exe(self):
        """Smoke test validates teragen/terasort."""
        uuid = self.d.action_do(self.yarn['unit_name'], 'smoke-test')
        result = json.loads(self.d.action_fetch(uuid))
        if (result['status'] != "completed"):
            error = "YARN smoke-test failed: %s" % result['output']
            amulet.raise_status(amulet.FAIL, msg=error)
        else:
            amulet.raise_status(amulet.PASS, msg="YARN smoke-test successful")

    def test_pig(self):
        """Smoke test validates Pig with a simple /etc/passwd script."""
        uuid = self.d.action_do(self.pig['unit_name'], 'smoke-test')
        result = json.loads(self.d.action_fetch(uuid))
        if (result['status'] != "completed"):
            error = "Pig smoke-test failed: %s" % result['output']
            amulet.raise_status(amulet.FAIL, msg=error)
        else:
            amulet.raise_status(amulet.PASS, msg="Pig smoke-test successful")


if __name__ == '__main__':
    unittest.main()
