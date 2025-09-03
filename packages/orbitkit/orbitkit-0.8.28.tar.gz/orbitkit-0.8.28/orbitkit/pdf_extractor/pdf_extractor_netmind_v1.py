import json
import os
import tempfile
import datetime
import time
import pytz
import logging
import requests
from orbitkit import id_srv
from orbitkit.util import s3_split_path, S3Util, get_from_dict_or_env, ExtenCons, s3_path_join, \
    get_content_type_4_filename
from typing import Optional
import urllib3

logger = logging.getLogger(__name__)

"""默认的目录生成规则
文件名称/
- pages.txt
- pages.txt.vector
- blocks.txt
- blocks.txt.vector
- raw-netmind-backup.txt（如果使用 netmind 解析的话，则存储一份原生备份）

文件格式：
- {'id': 'l_9Kk4iDUL', 'page': 125, 'seq_no': 31, 'sentence': 'xxx', 'type': 'sentence', 'text_location': {'location': [[752.7609, 423.47514, 774.3009, 416.99514]]}, 'others': 'xxx'}
- {'id': 'p_9Kk4iDUL', 'page': 1, 'sentence': 'xxx', 'others': 'xxx'}

raw:
    type: 'title/table/sentence | image'
    sentence: ""
    image_detail: [{'path','desc': '',}]
"""


class PdfExtractorNetmind:
    def __init__(self,
                 s3_path: str,
                 version: str = 'ov3',
                 stop_page: int = 0,
                 parse_timeout: int = 10 * 60 + 3,
                 txt_vector: str = 'txt-vector',
                 temp_folder: Optional[str] = None,
                 *args, **kwargs):

        self.version = version
        self.s3_path = s3_path
        self.stop_page = stop_page
        self.parse_timeout = parse_timeout
        self.txt_vector = txt_vector
        self.temp_folder = temp_folder

        # Try to get key aws pair
        aws_access_key_id = get_from_dict_or_env(
            kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
        )

        aws_secret_access_key = get_from_dict_or_env(
            kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
        )

        netmind_token = get_from_dict_or_env(
            kwargs, "netmind_token", "NETMIND_TOKEN",
        )

        netmind_endpoint = get_from_dict_or_env(
            kwargs, "netmind_endpoint", "NETMIND_ENDPOINT",
        )

        self.netmind_token = netmind_token
        self.netmind_endpoint = netmind_endpoint

        self.s3_util = S3Util(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self._s3_resource = self.s3_util.get_s3_resource()
        self._s3_client = self.s3_util.get_s3_client()

    def extract(self):
        if self.temp_folder:
            if not os.path.exists(self.temp_folder):
                raise Exception('The temp folder given not exists...')
            self.extract_detail(self.temp_folder)
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                input_folder = os.path.join(tmp_dir, 'input')
                if not os.path.exists(input_folder):
                    os.makedirs(input_folder)

                self.extract_detail(input_folder)

    def extract_detail(self, input_folder):
        s3_path_obj = s3_split_path(self.s3_path)

        # 禁用 InsecureRequestWarning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # # 下载文件到 input folder
        # file_local_path_in = os.path.join(input_folder, 'tmp_filename.pdf')
        # self._s3_resource.Bucket(s3_path_obj['bucket']).download_file(s3_path_obj['store_path'], file_local_path_in)
        # logger.info("Download file successfully...")
        #
        # # >>>>>>>>>>>>>>>>>> 开始使用 netmind 进行文件的提取操作
        # start = time.time()
        # with open(file_local_path_in, "rb") as f:
        #     files = {"file": f}
        #     header = {
        #         "Authorization": f"Bearer {self.netmind_token}",
        #     }
        #     response = requests.post(self.netmind_endpoint, files=files, timeout=10 * 60, headers=header)
        #     if response.status_code != 200:
        #         print(response.content)
        #         raise Exception("Failed to extract file with NETMIND.")
        #     logger.info(f"Extract text by using Netmind successfully: {time.time() - start}")

        # 开始尝试提取...
        presigned_url = self._s3_client.generate_presigned_url('get_object',
                                                               Params={
                                                                   'Bucket': s3_path_obj["bucket"],
                                                                   'Key': s3_path_obj["store_path"]
                                                               },
                                                               ExpiresIn=604800)
        logger.info("Get presigned_url successfully...")

        # >>>>>>>>>>>>>>>>>> 开始使用 netmind 进行文件的提取操作
        start = time.time()
        files = {"url": (None, presigned_url)}
        header = {"Authorization": f"Bearer {self.netmind_token}"}
        response = requests.post(
            self.netmind_endpoint, files=files, timeout=self.parse_timeout, headers=header,
        )
        if response.status_code == 400:
            raise Exception("[400] Not a standard pdf format!")
        if response.status_code == 504:
            raise Exception("[504] Parsing pdf timed out!")
        if response.status_code != 200:
            raise Exception(f"[{str(response.status_code)}] {response.text}")

        logger.info(f"Extract text by using Netmind successfully: {time.time() - start}")

        # >>>>>>>>>>>>>>>>>> Start to generate pages/blocks/raw
        netmind_reg_file = os.path.join(input_folder, 'netmind_reg.txt')
        blocks_file = os.path.join(input_folder, 'blocks.txt')
        pages_file = os.path.join(input_folder, 'pages.txt')

        with open(netmind_reg_file, "w+", encoding='utf-8') as f_reg, \
                open(blocks_file, "w+", encoding='utf-8') as f_blocks, \
                open(pages_file, "w+", encoding='utf-8') as f_pages:

            current_page_num = 0
            current_page_txt = ""
            all_local_image_path = []
            for ind, block in enumerate(response.json(), start=1):
                # 如果是图片类型，则进行图片的转换
                if block["type"] in ["image"]:
                    for item_img in block["image_detail"]:
                        # res_img = requests.get(item_img["path"], verify=False)
                        # if res_img.status_code != 200:
                        #     raise Exception(f"Download image failed: {res_img.status_code}")

                        # Build image local path for using
                        image_extension = str(item_img["path"]).split(".")[-1]
                        image_local_relitive_path = f"{id_srv.get_random_short_id_v2()}.{image_extension}"
                        # image_local_abs_path = os.path.join(input_folder, image_local_relitive_path)
                        # with open(image_local_abs_path, mode="wb") as img_tmp:
                        #     img_tmp.write(res_img.content)
                        # all_local_image_path.append(image_local_relitive_path)
                        all_local_image_path.append({
                            "path_raw": item_img["path"],
                            "path_s3": f"images/{image_local_relitive_path}",
                        })
                        # 直接修改其 image path 为自己的
                        item_img["path"] = f"images/{image_local_relitive_path}"

                # For raw
                f_reg.write(json.dumps(block, ensure_ascii=False) + "\n")

                # For blocks
                f_blocks.write(json.dumps(self.convert_2_block(block), ensure_ascii=False) + "\n")

                # For page: image Not in combine list
                if block["type"] in ["image"]:
                    continue
                if "sentence" not in block:
                    continue
                if block["page"] != current_page_num:
                    if current_page_num != 0:
                        # 开辟新的页并且将之前的页写入到文件中
                        f_pages.write(json.dumps({
                            "id": id_srv.get_random_short_id(),
                            "page": current_page_num,
                            "sentence": current_page_txt,
                        }, ensure_ascii=False) + "\n")

                    # 重置为下一页做准备
                    current_page_num = block["page"]
                    current_page_txt = block["sentence"] + "\n\n"
                else:
                    # 说明在同一页
                    current_page_txt += block["sentence"] + "\n\n"

                # 最后一页的话，最后加入
                if ind == len(response.json()):
                    f_pages.write(json.dumps({
                        "id": id_srv.get_random_short_id(),
                        "page": current_page_num,
                        "sentence": current_page_txt,
                    }, ensure_ascii=False) + "\n")

        logger.info("Write [blocks.txt] and [pages.txt] successfully...")

        # 上传各种文件到 s3 ---------------------------------------------------------------------------------------
        # Update images to s3
        for item_img in all_local_image_path:
            with requests.get(item_img["path_raw"], stream=True) as response:
                response.raise_for_status()  # 检查是否成功
                self._s3_client.upload_fileobj(
                    response.raw,
                    s3_path_obj['bucket'],
                    s3_path_join(self.txt_vector, s3_path_obj['store_path'], item_img["path_s3"]),
                    ExtraArgs={'ContentType': get_content_type_4_filename(item_img["path_raw"])},
                )

            # for item_img in all_local_image_path:
            #     self._s3_client.upload_file(
            #         os.path.join(input_folder, item_img),
            #         s3_path_obj['bucket'], s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'images', item_img),
            #         ExtraArgs={'ContentType': get_content_type_4_filename(item_img)}
            #     )
        logger.info("[image] Store images result successfully...")

        # Upload raw files to s3
        self._s3_client.upload_file(
            netmind_reg_file,
            s3_path_obj['bucket'], s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'netmind_reg.txt'),
            ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value}
        )
        logger.info("[raw] Store raw result successfully...")

        # Upload pages files to s3
        pages_txt_key = s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'pages.txt')
        self._s3_client.upload_file(os.path.join(input_folder, 'pages.txt'), s3_path_obj['bucket'], pages_txt_key,
                                    ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value})
        if self.s3_util.check_file_exist(s3_path_obj["bucket"], pages_txt_key) is False:
            raise Exception("[page] Store page result failed...")
        logger.info("[page] Store page result successfully...")

        # Upload blocks files to s3
        blocks_txt_key = s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'blocks.txt')
        self._s3_client.upload_file(os.path.join(input_folder, 'blocks.txt'), s3_path_obj['bucket'], blocks_txt_key,
                                    ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value})
        if self.s3_util.check_file_exist(s3_path_obj["bucket"], blocks_txt_key) is False:
            raise Exception("[block] Store block result failed...")
        logger.info("[block] Store block result successfully...")

        # FIXME: Metadata uploaded but there is no use of it.
        extract_meta = {
            "extraction": {
                "version": "netmind",
                "sub_version": "v1",
                "finished_time": datetime.datetime.now(tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
            },
            "metadata": {},
            "others": {}
        }

        object_put = self._s3_resource.Object(s3_path_obj['bucket'],
                                              s3_path_join(self.txt_vector, s3_path_obj['store_path'],
                                                           'metadata.txt'))
        object_put.put(Body=json.dumps(extract_meta, ensure_ascii=False),
                       ContentType=ExtenCons.EXTEN_TEXT_TXT_UTF8.value)
        logger.info("[meta] Store extract meta info successfully...")

    def convert_2_block(self, block_raw):
        f_block = {
            "id": block_raw["id"],
            "page": block_raw["page"],
            "seq_no": block_raw["seq_no"],
            "sentence": "",
            "type": block_raw["type"],
            "image_detail": [],
            "text_location": {"location": block_raw["text_location"]["location"]},
        }
        if "sentence" in block_raw:
            f_block["sentence"] = block_raw["sentence"]

        if block_raw["type"] == "image":
            f_block["image_detail"] = block_raw["image_detail"]
        return f_block
