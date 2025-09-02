#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import logging
import os

from x2case.parser import xmind2suite
from xmindparser import get_xmind_zen_builtin_json


class XmindZenParser:
    """Xmind file Parser for Zen"""

    def __init__(self, xmind_file):
        self.xmind_file = xmind_file

    def get_suite_json(self):
        """Load the XMind file and parse to `x2case.metadata.TestSuite` list"""

        content_json = get_xmind_zen_builtin_json(self.xmind_file)

        logging.debug(f"loading XMind file:{self.xmind_file} dict data: {content_json}")

        if content_json:
            test_suites = xmind2suite(content_json)
            return test_suites
        else:
            logging.error(f'Invalid XMind file {self.xmind_file}: it is empty!')
            return []

    def get_xmind_testsuite_list(self):
        """Load the XMind file and get all testsuite in it
        :return: a list of testsuite data
        """

        logging.info(f'Start converting XMind file{self.xmind_file} to testsuite data list...')
        testsuite_list = self.get_suite_json()
        suite_data_list = []

        for testsuite in testsuite_list:
            product_statistics = {
                'case_num': 0,
                'non_execution': 0,
                'pass': 0,
                'failed': 0,
                'blocked': 0,
                'skipped': 0
            }
            for sub_suite in testsuite.sub_suites:
                suite_statistics = {
                    'case_num': len(sub_suite.testcase_list),
                    'non_execution': 0,
                    'pass': 0,
                    'failed': 0,
                    'blocked': 0,
                    'skipped': 0
                }
                for case in sub_suite.testcase_list:
                    if case.result == 0:
                        suite_statistics['non_execution'] += 1
                    elif case.result == 1:
                        suite_statistics['pass'] += 1
                    elif case.result == 2:
                        suite_statistics['failed'] += 1
                    elif case.result == 3:
                        suite_statistics['blocked'] += 1
                    elif case.result == 4:
                        suite_statistics['skipped'] += 1
                    else:
                        logging.warning(
                            f'This testcase result is abnormal: {case.result}, please check it: {case.to_dict()}')
                sub_suite.statistics = suite_statistics
                for item in product_statistics:
                    product_statistics[item] += suite_statistics[item]

            testsuite.statistics = product_statistics
            suite_data = testsuite.to_dict()
            suite_data_list.append(suite_data)

        logging.info(f'Convert XMind file{self.xmind_file} to testsuite data list successfully!')
        return suite_data_list

    def get_xmind_testcase_list(self):
        """Load the XMind file and get all testcase in it
        :return: a list of testcase data
        """

        logging.info(f'Start converting XMind file{self.xmind_file} to testcases dict data...')
        test_suites = self.get_suite_json()
        testcases = []

        for testsuite in test_suites:
            product = testsuite.name
            epic_link = testsuite.epic_link
            for suite in testsuite.sub_suites:
                for case in suite.testcase_list:
                    case_data = case.to_dict()
                    case_data['product'] = product
                    case_data['suite'] = suite.name
                    case_data['epic_link'] = epic_link
                    testcases.append(case_data)

        logging.info(f'Convert XMind file{self.xmind_file} to testcases dict data successfully!')
        return testcases

    def xmind_2_suite_json_file(self):
        """Convert XMind file to a testsuite json file"""

        logging.info(f'Start converting XMind file{self.xmind_file} to test_suites json file...')
        test_suites = self.get_xmind_testsuite_list()
        testsuite_json_file = self.xmind_file[:-6] + '_testsuite.json'

        if os.path.exists(testsuite_json_file):
            os.remove(testsuite_json_file)

        with open(testsuite_json_file, 'w', encoding='utf8') as f:
            f.write(json.dumps(test_suites, indent=4, separators=(',', ': '), ensure_ascii=False))
            logging.info(
                f'Convert XMind file {self.xmind_file} to a testsuite json file {testsuite_json_file} successfully!')

        return testsuite_json_file

    def xmind_2_case_json_file(self):
        """Convert XMind file to a testcase json file"""

        logging.info(f'Start converting XMind file {self.xmind_file} to testcases json file...')
        testcases = self.get_xmind_testcase_list()
        testcase_json_file = self.xmind_file[:-6] + '.json'

        if os.path.exists(testcase_json_file):
            os.remove(testcase_json_file)

        with open(testcase_json_file, 'w', encoding='utf8') as f:
            f.write(json.dumps(testcases, indent=4, separators=(',', ': '), ensure_ascii=False))
            logging.info(
                f'Convert XMind file {self.xmind_file} to a testcase json file{testcase_json_file} successfully!')

        return testcase_json_file


def get_absolute_path(path):
    """
        Return the absolute path of a file

        If path contains a start point (eg Unix '/') then use the specified start point
        instead of the current working directory. The starting point of the file path is
        allowed to begin with a tilde "~", which will be replaced with the user's home directory.
    """
    fp, fn = os.path.split(path)
    if not fp:
        fp = os.getcwd()
    fp = os.path.abspath(os.path.expanduser(fp))
    return os.path.join(fp, fn)
