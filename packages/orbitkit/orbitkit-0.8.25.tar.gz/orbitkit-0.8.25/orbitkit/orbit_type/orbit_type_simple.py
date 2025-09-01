import abc
import json
import logging
import re
from typing import List, Literal
from botocore.exceptions import ClientError
import boto3

logger = logging.getLogger(__name__)

"""
https://ot-cdn.s3.us-west-2.amazonaws.com/orbit-typing/typing-prod/0.3.4.json
"lv3_list":[
    {
      "type": "lv3_list",
      "level_2_id": "1001",
      "lv3_id": "10000",
      "lv3_name": "Copy of Newspaper Publication",
      "rule_list": [
        {
          "order": 1,
          "is_stop": false,
          "selected": true,
          "type": "rule_keyword",
          "value": [
            {
              "name": "copy of Newspaper Publication",
              "is_sensitive": false,
              "id": 3843
            }
          ]
        },
        {
          "order": 2,
          "is_stop": false,
          "selected": true,
          "type": "rule_ex",
          "value": [
            {
              "name": "copy&newspaper&publica",
              "is_sensitive": false
            }
          ]
        },
        {
          "order": 3,
          "is_stop": false,
          "selected": false,
          "type": "rule_re",
          "value": [
            {
              "name": null,
              "is_sensitive": false
            }
          ]
        }
      ]
    },
    ...
]
"""


class L3Rule(metaclass=abc.ABCMeta):
    l3_obj: dict = None
    rule_each: dict = None

    @abc.abstractmethod
    def run_match(self, target_str: str) -> bool:
        raise NotImplementedError("No implement exception!")


class L3RuleKeyword(L3Rule):
    """E.G. 4 self.rule_each
    {
      "order": 1,
      "is_stop": false,
      "selected": true,
      "type": "rule_keyword",
      "value": [
        { "name": "Press Release", "is_sensitive": false },
        { "name": "pressrelease", "is_sensitive": false },
        { "name": "news release", "is_sensitive": false },
        { "name": "newsrelease", "is_sensitive": false },
        { "name": "conformity", "is_sensitive": false }
      ]
    },
    """

    def __init__(self, rule_each, l3_obj):
        self.rule_each = rule_each
        self.l3_obj = l3_obj

    def run_match(self, target_str: str) -> bool:
        is_matched = False
        value_list = self.rule_each["value"]
        for keyword_obj in value_list:
            if keyword_obj["is_sensitive"]:
                is_matched = target_str.__contains__(keyword_obj["name"])
            else:
                is_matched = target_str.lower().__contains__(str(keyword_obj["name"]).lower())
            if is_matched:
                break
        return is_matched


class L3RuleEx(L3Rule):
    """E.G. 4 self.rule_each
    {
      "order": 2,
      "is_stop": false,
      "selected": false,
      "type": "rule_ex",
      "value": [{ "name": "", "is_sensitive": false }]
    },
    """

    def __init__(self, rule_each, l3_obj):
        self.rule_each = rule_each
        self.l3_obj = l3_obj
        self.is_sensitive = self.rule_each["value"][0]["is_sensitive"]
        self.python_code = self.compile_rule()

    def compile_rule(self):

        expr: str = self.rule_each["value"][0]["name"]

        if not self.is_sensitive:
            expr = expr.lower()

        # --------- 操作符转义 ---------
        escape_chrs = {
            '_(_': '$FrPt$',
            '_)_': '$ClPt$',
            '_|_': '$OrOp$',
            '_&_': '$AndOp$',
            '_!_': '$NotOp$',
        }

        for k, v in escape_chrs.items():
            expr = expr.replace(k, v)
        # --------- 操作符转义 ---------

        symbol_dict = {
            '(': '("',
            ')': '" in s)',
            '&': '" in s and "',
            '|': '" in s or "',
        }

        python_code = ''
        for char in expr:
            if char in symbol_dict:
                python_code += symbol_dict[char]
            else:
                python_code += char

        python_code = python_code.replace('"(', "(").replace(')" in s', ")")
        if not python_code.endswith(')'):
            python_code += '" in s'
        if not python_code.startswith('('):
            python_code = '"' + python_code

        # --------- 反转义 ---------
        for k, v in escape_chrs.items():
            pure_chr = k[1:-1]
            python_code = python_code.replace(v, pure_chr)
        # --------- 反转义 ---------

        python_code = f"""
global match_flag
match_flag = {python_code}
        """

        # --------- 转换 not 运算符 ---------
        not_word = re.findall(r'("!.+?" in s)', python_code)
        for each in not_word:
            this_pure_word = each.replace('"!', '', 1).replace('" in s', '', 1)
            replaced_word = f'"{this_pure_word}" not in s'
            python_code = python_code.replace(each, replaced_word, 1)
        # --------- 转换 not 运算符 ---------

        return python_code

    def run_match(self, target_str: str) -> bool:

        if not self.is_sensitive:
            target_str = target_str.lower()

        s = target_str

        namespace = {'match_flag': False, 's': s}
        try:
            exec(self.python_code, namespace)
        except Exception as e:
            # print(e)
            return False

        return namespace['match_flag']


class L3RuleRe(L3Rule):
    """E.G. 4 self.rule_each
    {
      "order": 3,
      "is_stop": false,
      "selected": false,
      "type": "rule_re",
      "value": [{ "name": "", "is_sensitive": false }]
    }
    """

    def __init__(self, rule_each, l3_obj):
        self.rule_each = rule_each
        self.l3_obj = l3_obj
        re_pattern = self.rule_each["value"][0]["name"]
        if self.rule_each["value"][0]["is_sensitive"]:
            self.re_obj = re.compile(r"" + re_pattern + "")
        else:
            self.re_obj = re.compile(r"" + re_pattern + "", re.I)

    def run_match(self, target_str: str) -> bool:
        return self.re_obj.search(target_str) is not None


# RuleMatcher ---------------------------
class L3RuleMatcher:

    def __init__(self, l3_obj: dict):
        self.rule_list: List[L3Rule] = []
        self.l3_obj = l3_obj
        self._gen_all_rule()

        # Re-order the rule
        self.rule_list = sorted(self.rule_list, key=lambda r: r.rule_each["order"])

    def _gen_all_rule(self):
        rule_list = self.l3_obj["rule_list"]

        for rule_item in rule_list:
            # Only need selected rule
            if rule_item["selected"] is False:
                continue

            if rule_item["type"] == "rule_keyword":
                self.rule_list.append(L3RuleKeyword(rule_item, self.l3_obj))
            if rule_item["type"] == "rule_ex":
                self.rule_list.append(L3RuleEx(rule_item, self.l3_obj))
            if rule_item["type"] == "rule_re":
                self.rule_list.append(L3RuleRe(rule_item, self.l3_obj))

    def start_match(self, target_str: str):
        match_result = {"is_matched": False, "lv3_id": "", "lv3_name": "", "matched_list": []}
        for rule_item in self.rule_list:
            if rule_item.run_match(target_str=target_str):
                match_result["is_matched"] = True
                match_result["lv3_id"] = self.l3_obj["lv3_id"]
                match_result["lv3_name"] = self.l3_obj["lv3_name"]
                match_result["matched_list"].append(rule_item.rule_each['type'])
            # 如果当前的规则上有停止标志，并且已经有匹配项，则停止
            if rule_item.rule_each["is_stop"] and len(match_result["matched_list"]) > 0:
                break

        return match_result


# RuleMatcherList ---------------------------
class L3RuleListMatcher:

    def __init__(self, rule_schema: dict):
        self.l3_rule_matcher_list: List[L3RuleMatcher] = []
        self.rule_schema = rule_schema
        lv3_list = rule_schema["lv3_list"]
        for lv3_obj in lv3_list:
            self.l3_rule_matcher_list.append(L3RuleMatcher(l3_obj=lv3_obj))

    def start_match_all(self, target_str: str):
        matched_id_list = []
        for l3_rule_matcher in self.l3_rule_matcher_list:
            res = l3_rule_matcher.start_match(target_str)
            if res["is_matched"]:
                matched_id_list.append({
                    'lv3_id': str(res["lv3_id"]),
                    'lv3_name': res["lv3_name"]
                })
        return matched_id_list


class OrbitTypeMatcher:

    def __init__(self, s3_client=None, file_bucket: str = None, key_prefix: str = None, version: str = None):

        if not s3_client:
            s3_client = boto3.client('s3')
        if not file_bucket:
            file_bucket = 'ot-cdn'
        if not key_prefix:
            key_prefix = 'orbit-typing/typing-prod'

        self.s3_client = s3_client
        self.file_bucket = file_bucket
        self.key_prefix = key_prefix

        if not version:
            version = self.get_newest_version()
        source_key = f'{key_prefix}/{version}.json'
        json_file = self.read_s3_file(
            bucket_name=file_bucket,
            file_name=source_key
        )
        if not json_file:
            raise Exception(f'该 S3 文件不存在: {source_key}')
        self.json_file = json_file
        self.matcher = L3RuleListMatcher(json_file)
        self.version = version

    def read_s3_file(self, bucket_name: str, file_name: str):
        """
        工具函数：读取 s3 中的 json 文件
        """
        try:
            file_obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_name)
            lines = file_obj['Body'].read().decode('utf-8')
            json_data = json.loads(lines)
            return json_data
        except ClientError as e:
            return None

    def get_newest_version(self):
        """
        获取最新的类型版本号
        """
        response = self.s3_client.list_objects_v2(Bucket=self.file_bucket, Prefix=self.key_prefix)

        # 遍历存储桶中的对象，获取文件名
        file_names = []
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.endswith('/'):  # 排除文件夹本身
                continue
            file_names.append(key.split('/')[-1])  # 获取文件名部分

        result = []
        for key in file_names:
            if 'tmp.json' in key:
                continue
            if '.json' not in key:
                continue
            result.append(key.replace('.json', ''))

        def sort_vision_json_file(filename):
            parts = filename.replace('.json', '').split('.')
            return tuple(int(part) for part in parts)

        sorted_versions = sorted(result, key=sort_vision_json_file, reverse=True)
        return sorted_versions[0]

    def get_full_type_list(self):
        """
        获取完整包含 1、2、3 级类型的列表
        """

        lv1_list = self.json_file['lv1_list']
        lv1_dict = {}
        for row in lv1_list:
            lv1_id = row['lv1_id']
            name = row['lv1_name']
            lv1_dict[lv1_id] = name

        lv2_list = self.json_file['lv2_list']
        lv2_dict = {}
        for row in lv2_list:
            lv1_id = row['lv1_id']
            lv2_id = row['lv2_id']
            name = row['lv2_name']
            lv2_dict[lv2_id] = {
                'lv2_id': lv2_id,
                'lv2_name': name,
                'lv1_id': lv1_id,
                'lv1_name': lv1_dict[lv1_id]
            }

        lv3_list = self.json_file['lv3_list']
        lv3_data = []
        for row in lv3_list:
            lv2_id = row['level_2_id']
            this_dict = {
                'lv3_id': row['lv3_id'],
                'lv3_name': row['lv3_name']
            }
            this_dict.update(lv2_dict[lv2_id])
            lv3_data.append(this_dict)

        sorted_list = sorted(
            lv3_data,
            key=lambda x: (int(x['lv3_id']), int(x['lv2_id']), int(x['lv1_id']))
        )
        return sorted_list

    def match_type(self, match_flag: Literal['in_order', 'match_all'] = 'in_order', **match_kwargs):
        """
        用于匹配的函数，可以传入n个匹配参数。
        in_order: 按顺序依次匹配，匹配到结果就停止
        match_all: 匹配全部的项，并将结果合并
        """
        if match_flag not in ['in_order', 'match_all']:
            raise ValueError('match_flag 参数必须是 "in_order" 或 "match_all"')
        if not match_kwargs:
            raise ValueError('必须传入匹配关键词！')

        default_result = [{'lv3_id': '19999', 'lv3_name': 'Miscellaneous'}]

        def match_url(url: str):
            split_url = url.replace('http://', '').replace('https://', '').split('/')
            split_url = [x.strip().replace('%20', ' ') for x in split_url if len(x.strip()) > 4]
            for part in reversed(split_url):
                match_result = self.matcher.start_match_all(part)
                if match_result:
                    match_key = f'url#{part}'
                    return match_key, match_result
            return None, None

        if match_flag == 'in_order':
            for key, value in match_kwargs.items():
                if key == 'url':
                    url_key, match_result = match_url(value)
                    if match_result:
                        return url_key, match_result
                else:
                    match_result = self.matcher.start_match_all(value)
                    if match_result:
                        return key, match_result
            return None, default_result

        elif match_flag == 'match_all':
            overall_results = []
            match_detail = {}
            for key, value in match_kwargs.items():
                if key == 'url':
                    url_key, match_result = match_url(value)
                    if match_result:
                        overall_results += match_result
                        match_detail[url_key] = match_result
                else:
                    match_result = self.matcher.start_match_all(value)
                    if match_result:
                        overall_results += match_result
                        match_detail[key] = match_result

            if not overall_results:
                overall_results = default_result

            unique_dict = {d['lv3_id']: d for d in overall_results}
            sorted_results = sorted(unique_dict.values(), key=lambda x: int(x['lv3_id']))

            return {
                'results': sorted_results,
                'match_detail': match_detail
            }


if __name__ == '__main__':
    matcher = OrbitTypeMatcher(version='0.2.1')
    matcher.match_type(title='asdf')
