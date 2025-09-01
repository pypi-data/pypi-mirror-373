'''
    @author  : xiaoyu.ma
    @date    : 2025/7/21
    @explain : 
    @version : 1.0
'''
import requests
from retry import retry
from orbitkit.util import s3_split_path
import logging

logger = logging.getLogger(__name__)


def get_ecm(sentence):
    return '业绩说明会' in sentence or '业绩会' in sentence or '集体接待日' in sentence or '年度' in sentence or '季度' in sentence

# investor_participants [{"name": "金桐羽","company": "太平洋证券"}]
# company_participants [{"name": "苗雷强","position": "证券事务代表"}]
@retry(tries=2, delay=4)
def send_request_to_api(s3_remote_url, endpoint, token):
    headers = {
        'Host': 'api.netmind.ai',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        "Authorization": f"Bearer {token}"
    }

    json_data = {
        'url': s3_remote_url,
    }

    response = requests.post(
        endpoint,
        headers=headers,
        json=json_data,
    )
    body = response.json()
    print(body)
    report_title = body['标题']
    report_list = body['投资者活动']
    meeting_location = body['会议地址']
    investor_participants = body['参会单位及人员']
    company_participants = body['公司接待人员']
    start_time = body['开始时间']  # 上海
    end_time = body['结束时间']  # 上海
    content = body['内容']
    table_report_type = body['报告类型']
    if table_report_type == '表格':
        report_list_str = " ".join(report_list)
        if get_ecm(report_list_str):
            report_type = 'ecm'
        else:
            report_type = 'brd'
    else:
        if len(content) > 0:
            if get_ecm(report_title):
                report_type = 'ecm'
            else:
                # 待定
                report_type = 'brd'
        else:
            report_type = 'unknown'
    json_file = {
        'report_title': report_title,
        'report_list': report_list,
        'report_type': report_type,
        'meeting_location': meeting_location,
        'investor_participants': investor_participants,
        'company_participants': company_participants,
        'start_time': start_time,
        'end_time': end_time,
        'content': content,
        'table_report_type': table_report_type,
        'source': 'netmind'
    }
    return json_file


def request_extractor_from_netmind(s3_client, s3_path, endpoint, token):
    s3_path_obj = s3_split_path(s3_path)
    # 开始尝试提取...
    presigned_url = s3_client.generate_presigned_url('get_object',
                                                     Params={
                                                         'Bucket': s3_path_obj["bucket"],
                                                         'Key': s3_path_obj["store_path"]
                                                     },
                                                     ExpiresIn=604800)
    logger.info("Get presigned_url successfully...")
    return send_request_to_api(presigned_url, endpoint, token)