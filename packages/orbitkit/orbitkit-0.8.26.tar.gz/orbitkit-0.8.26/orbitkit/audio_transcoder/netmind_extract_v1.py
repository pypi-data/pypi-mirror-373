'''
    @author  : xiaoyu.ma
    @date    : 2025/7/28
    @explain : netmind 视频api 解析
    @version : 1.0
'''
import os.path

import boto3
import requests
from retry import retry
import json
from openai import OpenAI
from orbitkit.util import s3_split_path
import openai
import json
import logging

logger = logging.getLogger(__name__)


class Translate:
    # gpt-4.1-nano-2025-04-14
    def __init__(self, model='gpt-4.1-mini'):
        self.model = model

    @retry(tries=2, delay=4)
    def send_msg(self, prompt):
        messages = [{"role": "system", "content": prompt}]
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"}
        )
        try:
            res = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            logger.error('GPT: "Invalid JSON format"')
            return None
        return res['text']

    def convert(self, q, to='English'):
        if not q:
            return None
        prompt = f"""
        You are a professional translator and financial research analyst.

        Your task is to:
        1. Automatically detect the input language.
           Always rely on the input text itself to detect the language — do not assume based on user expectations.
        2. Translate the content into {to}.
        3. Apply style transfer to ensure the translation is appropriate for a professional financial research report or analyst context.

        ⚠️ The input may be a sentence, phrase, title, abbreviation, or even resemble a file name — regardless of its form, always attempt to interpret and translate it based on context and professional judgment.

        ✅ Do not provide explanations, comments, or assumptions. Just return the translated result in the JSON format below.

        Return format:
        {{"text": "<translated_text>"}}

        --------------------
        Input to be translated:
        {q}
        --------------------
        """

        return self.send_msg(prompt)


#
# {"version": "1.0.1", "text": [
#     {"speaker": "SPEAKER_00", "text": " This is Peter.  This is Peter. This is Johnny. Kenny. And Josh.",
#      "start": 0.031, "end": 2.921},
#     {"speaker": "SPEAKER_01", "text": "We just wanted to take a minute to thank you.", "start": 3.507, "end": 4.962}],
#  "id": "0ca63ef01e224adca4865b3cec94c1a2", "model": "WhisperX"}
def text_processing(netmind_data, lang):
    import fasttext
    from urllib.request import urlretrieve
    model_path = "lid.176.bin"
    tran = Translate()
    # 如果模型不存在，则下载
    if not os.path.exists(model_path):
        logger.info("Downloading fasttext language detection model...")
        url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
        urlretrieve(url, model_path)
        logger.info("Download completed.")
    fasttext_model = fasttext.load_model(model_path)
    net_process = []
    for ele in netmind_data['text']:
        label, confidence = fasttext_model.predict(ele['text'])
        label_lang = label[0].replace("__label__", "")
        if lang != label_lang or (lang not in label_lang and confidence <= 0.95):
            # openai 翻译
            logger.info(f'置信度太低，正在翻译...， {label_lang}, {confidence}')
            ele['text'] = tran.convert(ele['text'], lang)
        net_process.append(ele)

    netmind_data['text'] = net_process
    return netmind_data


@retry(tries=2, delay=4)
def send_request_to_api(s3_remote_url, **kwargs):
    endpoint = kwargs['endpoint']
    token = kwargs['token']
    lang = kwargs.get('lang', 'en')
    headers = {
        'Authorization': token,
    }

    files = {
        'model': (None, 'WhisperX'),
        'url': (None, s3_remote_url),
        'language': (None, lang),
    }

    response = requests.post(endpoint, headers=headers, files=files)
    response.raise_for_status()
    netmind_data = response.json()
    return netmind_data


@retry(tries=2, delay=4)
def send_request_to_stream(file_steam, **kwargs):
    endpoint = kwargs['endpoint']
    token = kwargs['token']
    lang = kwargs.get('lang', 'en')
    headers = {
        'Authorization': token,
    }

    files = {
        'model': (None, 'WhisperX'),
        'files': (None, file_steam),
        'language': (None, lang),
    }

    response = requests.post(endpoint, headers=headers, files=files)
    response.raise_for_status()
    netmind_data = response.json()
    return netmind_data


def request_wav_from_netmind(s3_client, s3_path=None, file_steam=None, **kwargs):
    lang = kwargs.get('lang', 'en')
    folder = kwargs.get('folder', '')
    if s3_path:
        s3_path_obj = s3_split_path(s3_path)
        # 开始尝试提取...
        presigned_url = s3_client.generate_presigned_url('get_object',
                                                         Params={
                                                             'Bucket': s3_path_obj["bucket"],
                                                             'Key': s3_path_obj["store_path"]
                                                         },
                                                         ExpiresIn=604800)
        logger.info("Get presigned_url successfully...")
        data = send_request_to_api(presigned_url, **kwargs)
    elif file_steam:
        logger.info("Get Stream...")
        data = send_request_to_stream(file_steam, **kwargs)
    else:
        raise Exception('参数异常！')
    json_netmind_wav_path = os.path.join(folder, 'netmind_wav.json')
    with open(json_netmind_wav_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    net_process = text_processing(data, lang)

    # 翻译接口处理
    json_netmind_lang_wav_path = os.path.join(folder, 'netmind_lang_wav.json')
    with open(json_netmind_lang_wav_path, 'w', encoding='utf-8') as json_file:
        json.dump(net_process, json_file, ensure_ascii=False, indent=4)
    return json_netmind_wav_path, json_netmind_lang_wav_path
