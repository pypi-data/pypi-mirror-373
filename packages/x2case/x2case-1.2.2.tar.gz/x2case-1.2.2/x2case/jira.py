#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import csv
import logging
import os

from x2case import const
from x2case.func import XmindZenParser

"""
Convert XMind fie to jira testcase csv file
"""


def xmind_to_jira_csv_file(xmind_file):
    """Convert XMind file to a jira csv file"""
    parser = XmindZenParser(xmind_file)
    logging.info(f'Start converting XMind file{xmind_file} to jira file...')
    testcases = parser.get_xmind_testcase_list()

    jira_testcase_rows = [const.JIRA_HEAD]
    for testcase in testcases:
        row = gen_case_row(testcase)
        jira_testcase_rows.append(row)

    jira_file = xmind_file[:-6] + '.csv'
    if os.path.exists(jira_file):
        os.remove(jira_file)

    with open(jira_file, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerows(jira_testcase_rows)
        logging.info(f'Convert XMind file{xmind_file} to a jira csv file {jira_file} successfully!')

    return jira_file


def gen_case_row(testcase_dict):
    case_module = gen_case_module(testcase_dict['suite'])
    case_title = testcase_dict['name']
    case_precondition = testcase_dict['preconditions']
    case_step, case_expected_result = gen_case_step_and_expected_result(testcase_dict['steps'])
    # case_keyword = ''
    case_priority = gen_case_priority(testcase_dict['importance'])
    case_type = gen_case_type(testcase_dict['execution_type'])
    # case_apply_phase = 'SIT'  # default
    application = testcase_dict['product']

    row = [
        # ['Test Case Identifier*',
        #  'Issue Key (Update)',
        testcase_dict['case_id'], '',
        case_title, case_step,
        '',  # 'Data',
        case_expected_result,
        '',  # 'Description',
        case_type, application,
        #  'Issue Links - Tests',
        #  'Issue Links - Tests',
        '', '',
        case_priority,
        #  'Reporter',
        #  'Assignee',
        '', '',
        #  'Labels',
        case_module,
        #  'Component/s',
        #  'Affects Version/s',
        #  'Fix Version/s',
        #  'Environment',
        #  'Attachment',
        #  'Step Attachment',
        #  'Comment',
        '', '', '', '', '', '', '',  # 7 placeholder
        #  'Pre-Condition',
        case_precondition,
        #  'Test Set',
        #  'Test Repository',
        #  'Test Plan',
        #  'Test Run',
        '', '', '', '',  # 4 placeholder
        testcase_dict.get('epic_link', ''), #  'Epic Link',
        #  'Status',
        #  'Resolution'
        '', '',  # 2 placeholder
    ]

    return row


def gen_case_module(module_name):
    if module_name:
        module_name = module_name.replace('（', '(')
        module_name = module_name.replace('）', ')')
    else:
        module_name = '/'
    return module_name


def gen_case_step_and_expected_result(steps):
    case_step = ''
    case_expected_result = ''

    for step_dict in steps:
        actions = step_dict.get('actions', '').strip()
        if actions:
            case_step += str(step_dict['step_number']) + '. ' + actions.replace('\n', '') + '\n'
        else:
            case_step += ' \n'

        expected = step_dict.get('expected_results', '').strip()
        if expected:
            case_expected_result += str(step_dict['step_number']) + '. ' + expected.replace('\n', '') + '\n'
        else:
            case_expected_result += ' \n'

    return case_step, case_expected_result


def gen_case_priority(priority):
    mapping = {1: 'High', 2: 'Medium', 3: 'Low'}
    if priority in mapping.keys():
        return mapping[priority]
    else:
        return 'Medium'


def gen_case_type(case_type):
    mapping = {1: 'Manual', 2: 'Automation'}
    if case_type in mapping.keys():
        return mapping[case_type]
    else:
        return 'Manual'


if __name__ == '__main__':
    xmind_file = '../docs/jira_demo.xmind'
    jira_csv_file = xmind_to_jira_csv_file(xmind_file)
    print(f'Convert the xmind file to a jira csv file successfully{jira_csv_file}')
