# X2Case

> **X2Case** , `Xmind` 文件转 `jira` CSV 文件。 支持新版 xmind zen。

### 一、安装 Install

```
pip3 install x2case
```

### 二、使用方式 Usage

#### 1. to jira csv

```
import json
import logging

from x2case.func import XmindZenParser
from x2case.jira import xmind_to_jira_csv_file

logging.basicConfig(level=logging.INFO)

xmind_file = 'docs/jira_demo.xmind'
print('Start to convert XMind file: %s' % xmind_file)

# 1、testcases import file
# (1) jira
csv_file = xmind_to_jira_csv_file(xmind_file)
print(f'Convert XMind file to zentao csv file successfully: {xmind_file}')
```

#### 2. to testcases json file

```
parser = XmindZenParser(xmind_file)
# (1) testsuite
testsuite_json_file = parser.xmind_2_suite_json_file()
print('Convert XMind file to testsuite json file successfully: %s' % testsuite_json_file)
# (2) testcase
testcase_json_file = parser.xmind_2_case_json_file()
print('Convert XMind file to testcase json file successfully: %s' % testcase_json_file)
```

#### 3、test dict/json data

```
# (1) testsuite

test_suite = parser.get_xmind_testsuite_list()
print('Convert XMind to test suits dict data:\n%s' %
      json.dumps(test_suite, indent=2, separators=(',', ': '), ensure_ascii=False))
# (2) testcase
testcases = parser.get_xmind_testcase_list()
print('Convert Xmind to testcases dict data:\n%s' %
      json.dumps(testcases, indent=4, separators=(',', ': '), ensure_ascii=False))

print('Finished conversion, Congratulations!')

```

### 三、致谢

**X2Case** 工具的产生，受益于以下两个开源项目，并在此基础上扩展、优化，受益匪浅，感恩！

- 1、**[XMindParser](https://github.com/tobyqin/xmindparser)**：Parse xmind file to programmable data type (e.g. json,
  xml). Python 3.x required. Now it supports XmindZen file type as well.
- 2、**[Xmind2Testcase](https://github.com/zhuifengshen/xmind2testcase)**：XMind2TestCase 工具，提供了一个高效测试用例设计的解决方案！

（如果本项目对你有帮助的话，也欢迎 _**[star](https://github.com/Allenzzz/x2case)**_ ）

### LICENSE

```
MIT License
```