#!/usr/bin/env python
# _*_ coding:utf-8 _*_


TAG_XML = 'xml'

TAG_TESTSUITE = 'testsuite'
TAG_DETAILS = 'details'

TAG_TESTCASE = 'testcase'
TAG_VERSION = 'version'
TAG_SUMMARY = 'summary'
TAG_PRECONDITIONS = 'preconditions'
TAG_IMPORTANCE = 'importance'
TAG_ESTIMATED_EXEC_DURATION = 'estimated_exec_duration'
TAG_STATUS = 'status'
TAG_IS_OPEN = 'is_open'
TAG_ACTIVE = 'active'
TAG_STEPS = 'steps'
TAG_STEP = 'step'
TAG_STEP_NUMBER = 'step_number'
TAG_ACTIONS = 'actions'
TAG_EXPECTEDRESULTS = 'expectedresults'
TAG_EXECUTION_TYPE = 'execution_type'

ATTR_NMAE = 'name'
ATTR_ID = 'id'
ATTR_INTERNALID = 'internalid'

JIRA_HEAD = ['Test Case Identifier*',
             'Issue Key (Update)',
             'Summary*',
             'Action*',
             'Data',
             'Expected Result',
             'Description',
             'Test Type',
             'Applications',
             'Issue Links - Tests',
             'Issue Links - Tests',
             'Priority',
             'Reporter',
             'Assignee',
             'Labels',
             'Component/s',
             'Affects Version/s',
             'Fix Version/s',
             'Environment',
             'Attachment',
             'Step Attachment',
             'Comment',
             'Pre-Condition',
             'Test Set',
             'Test Repository',
             'Test Plan',
             'Test Run',
             'Epic Link',
             'Status',
             'Resolution'
             ]
