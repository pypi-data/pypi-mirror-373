from datetime import datetime
from enum import Enum

'''Report status list
Below are all report status switch using
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''


class StatusCrawl(Enum):
    '''
        crawl_init: 爬虫爬取完索引
        crawl_downloaded: 爬虫下载附件成功
        crawl_failed: 爬虫下载附件失败
        crawl_bad: 这是一条无效记录（一般人工判定）
    '''

    CRAWL_INIT = 'crawl_init'
    CRAWL_DOWNLOADED = 'crawl_downloaded'
    CRAWL_FAILED = 'crawl_failed'
    CRAWL_BAD = 'crawl_bad'


class StatusExtract(Enum):
    '''
        extract_init: 文本提取初始化状态
        extract_done: 文本提取成功
        extract_failed: 文本提取失败
        extract_bad: 这是一条无效记录（一般人工判定）
    '''

    EXTRACT_INIT = 'extract_init'
    EXTRACT_DONE = 'extract_done'
    EXTRACT_FAILED = 'extract_failed'
    EXTRACT_BAD = 'extract_bad'


class StatusPerm(Enum):
    '''
        perm_init: permid 匹配初始化状态
        perm_match: permid 根据特征值完全匹配
        perm_match_part: permid 根据特征值部分匹配
        perm_match_no: permid 根据特征值完全不匹配
    '''

    PERM_INIT = 'perm_init'
    PERM_MATCH = 'perm_match'
    PERM_MATCH_PART = 'perm_match_part'
    PERM_MATCH_NO = 'perm_match_no'


class StatusConvert(Enum):
    '''
        convert_init: 文本提取块初始化状态
        convert_done: 文本提取块初始化成功
        convert_failed: 文本提取块初始化失败
        convert_bad: 这是一条无效记录（一般人工判定）
    '''

    CONVERT_INIT = 'convert_init'
    CONVERT_DONE = 'convert_done'
    CONVERT_FAILED = 'convert_failed'
    CONVERT_BAD = 'convert_bad'


class StatusConvertTxt(Enum):
    '''
        convert_init: 文本提取块初始化状态
        convert_done: 文本提取成功
        convert_txt_embedding: 文本提取成功和 embedding 成功
        convert_failed: 文本提取块初始化失败
        convert_bad: 这是一条无效记录（一般人工判定）
    '''

    CONVERT_TXT_INIT = 'convert_txt_init'
    CONVERT_TXT_DONE = 'convert_txt_done'
    CONVERT_TXT_EMBEDDING = 'convert_txt_embedding'
    CONVERT_TXT_FAILED = 'convert_txt_failed'
    CONVERT_TXT_BAD = 'convert_txt_bad'


class StatusConvertMeta(Enum):
    '''
        convert_init: 报告 meta 信息初始化状态
        convert_done: 报告 meta 信息提取成功
        convert_failed: 报告 meta 信息提取化失败
        convert_bad: 这是一条无效记录（一般人工判定）
    '''

    CONVERT_META_INIT = 'meta_init'
    CONVERT_META_DONE = 'meta_done'
    CONVERT_META_FAILED = 'meta_failed'
    CONVERT_META_BAD = 'meta_bad'


class SchemaKafkaIgnore:
    """Usage for
    "x_others.k_ignore": int(datetime.now().timestamp() * 1000)
    """
    X_OTHERS_K_IGNORE_KEY = "x_others.k_ignore"

    @staticmethod
    def get_k_ignore_val():
        return int(datetime.now().timestamp() * 1000)
