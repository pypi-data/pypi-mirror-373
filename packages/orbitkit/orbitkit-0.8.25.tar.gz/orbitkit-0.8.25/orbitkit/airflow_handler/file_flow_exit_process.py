import os
import logging
from datetime import datetime
import pytz
from pymongo import MongoClient
from orbitkit import id_srv
from orbitkit.constant.report_schema import SchemaKafkaIgnore

logger = logging.getLogger(__name__)


class FlowUpdater:

    def __init__(self, mongo_uri=None, database_name=None):
        self.mongo_url = mongo_uri or os.environ.get("MONGO_URL")
        if not self.mongo_url:
            raise EnvironmentError("MONGO_URL not set.")
        self.client = MongoClient(self.mongo_url)
        self.database = database_name or 'filing_reports'
        self.coon = self.client[self.database]
        self.step_tuple = ('convert', 'extract', 'embedding')
        self.kafka_ignore = SchemaKafkaIgnore()

    def _check_and_create_collection(self, data_source):
        collection_name = f'{data_source}_collection'
        if not hasattr(self, collection_name):
            setattr(self, collection_name, self.coon[data_source])
        return getattr(self, collection_name)

    def _handle_convert(self, status, attachments, db_store_path_set):
        if not attachments:
            raise ValueError("No attachments provided.")
        if not status:
            return {
                'x_status_list.status_convert.status': 'convert_failed',
                'x_status_list.status_convert.status_txt': 'convert_txt_init',
                'x_status_list.status_convert.status_meta': 'meta_init'
            }

        store_path_set = set()
        x_attachments_pdf = []
        for item in attachments:
            store_path = item['store_path']
            if store_path not in db_store_path_set:
                raise ValueError(f"store_path not found in db: {store_path}")
            if store_path in store_path_set:
                continue
            store_path_set.add(store_path)
            new_store_path = store_path if store_path.lower().endswith('.pdf') else store_path + '.pdf'
            x_attachments_pdf.append({
                "store_path": new_store_path,
                "store_path_txt": "",
                "store_path_pre": store_path,
                "file_name": item['file_name'],
                "raw_is_pdf": 'true' if store_path.lower().endswith('.pdf') else 'false',
                "file_hash": id_srv.get_fix_short_id(new_store_path).get("short_id")
            })
        return {
            'x_attachments_pdf': x_attachments_pdf,
            'x_status_list.status_convert.status': 'convert_done'
        }

    def _handle_extract(self, status):
        if not status:
            return {
                'x_status_list.status_convert.status_txt': 'convert_txt_failed'
            }
        return {
            'x_status_list.status_convert.status_txt': 'convert_txt_done',
            'x_status_list.status_convert.status_meta': 'meta_init'
        }

    def _handle_embedding(self, status):
        if not status:
            return {}
        return {'x_status_list.status_convert.status_txt': 'convert_txt_embedding'}

    def _step_handle(self, step_stage, status, attachments, db_store_path):
        method_name = f"_handle_{step_stage}"
        method = getattr(self, method_name, None)
        if method:
            return method(status, attachments=attachments,
                          db_store_path_set=db_store_path) if step_stage == 'convert' else method(status)
        else:
            raise ValueError(f"Unknown step_stage: {step_stage}")

    def update_mongo_data(self, report_id, data_source, update_params, kafka_ignore):
        if kafka_ignore:
            update_params.update({self.kafka_ignore.X_OTHERS_K_IGNORE_KEY: self.kafka_ignore.get_k_ignore_val()})
        update_params.update({"x_updated_date": datetime.now(tz=pytz.timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S%z")})
        collection = self._check_and_create_collection(data_source)
        result = collection.update_one({'_id': report_id}, {'$set': update_params})
        if result.matched_count == 0:
            raise LookupError(f"No document found with id {report_id} to update. {data_source}")
        logger.info(f"Document with id {report_id} update attempted. Modified: {result.modified_count}")

    def process_task(self, op_meta_record, kafka_ignore=False):
        report_id = op_meta_record['id']
        status = op_meta_record['status']
        start_stage = op_meta_record['start_stage']
        current_stage = op_meta_record['current_stage']
        target_stage = op_meta_record['target_stage']
        attachments = op_meta_record['x_attachments']
        data_source = op_meta_record['data_source']

        # 校验参数
        if not report_id or not status or not start_stage or not current_stage or not target_stage or (not attachments and start_stage == 'convert'):
            raise ValueError(f"Invalid op_meta_record: {op_meta_record}")
        if status == 'success' and target_stage != current_stage:
            raise ValueError(f"Invalid current_stage: {current_stage}-{report_id}")
        attachments = [i for i in attachments if i['category'] == 'x_attachments']

        # 确定结束阶段
        end_stage = target_stage if status == 'success' else current_stage if status == 'failed' else None
        if end_stage is None:
            logger.info(f"Invalid status: {status}.")
            return
        start_index = self.step_tuple.index(start_stage)
        end_index = self.step_tuple.index(end_stage)
        if start_index > end_index:
            raise ValueError(f"start_stage cannot be after end_stage: {start_stage} -> {end_stage}.")

        # 开始执行回更逻辑
        logger.info(
            f"😊 _id: {report_id}-{status}, start_step: {self.step_tuple[start_index]}, end_step: {self.step_tuple[end_index]}")

        # 查询这个报告是否存在于当前数据源
        db_doc = self._check_and_create_collection(data_source).find_one({'_id': report_id},
                                                                         {'_id': 1, 'x_attachments': 1,
                                                                          'x_status_list': 1})
        if not db_doc:
            logger.warning(f"No document found with id {report_id}.")
            return

        if db_doc['x_status_list']['status_crawl']['status'] != 'crawl_downloaded':
            logger.warning(f"{db_doc['_id']} statxus is not 'crawl_downloaded'")
            return

        # 构建数据库中存在store_path 防止出现数据库中x_attachments与x_attachments_pdf数据不一致问题
        db_store_path = {f"s3://{i['bucket']}/{i['store_path']}" for i in db_doc['x_attachments']}

        # 构建更新参数
        update_params = {}
        step_status = True
        for index, step in enumerate(self.step_tuple[start_index:end_index + 1], 1):
            if step == end_stage and status == 'failed':
                step_status = False
            logger.info(f' Processing step-{index} {step} - {"successfully" if step_status else "failed"}.')
            item = self._step_handle(step, step_status, attachments, db_store_path)
            update_params.update(item)

        # 执行更新
        if update_params:
            # logger.info(json.dumps(update_params, ensure_ascii=False, indent=2))
            self.update_mongo_data(report_id, data_source, update_params, kafka_ignore)
