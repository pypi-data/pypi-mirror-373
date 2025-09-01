import os
from collections import Counter
from datetime import datetime
from typing import Literal
import logging
import pymongo
import pytz
from orbitkit.airflow_handler.file_handler_v2 import FileFlowHandleV2
from orbitkit.airflow_handler.data_preprocessing import DocumentProcessor

logger = logging.getLogger(__name__)


class FilingOfficialProcessor:

    def __init__(self, mongo_uri=None, postgres_uri=None):
        mongo_uri = os.environ.get('MONGO_URI_MAIN_USER_APP') if not mongo_uri else mongo_uri
        if not mongo_uri:
            raise KeyError('mongo_uri not set.')

        self.mongo_client = pymongo.MongoClient(mongo_uri)
        self.data_xbrl_convert_collection = self.mongo_client['filing_reports']['data_xbrl_convert']
        self.filing_data_collection = self.mongo_client['filing_reports']['filing_data']
        self.official_data_collection = self.mongo_client['filing_reports']['official_data_relocation']
        self.annotation_reports_view_rows_collection = self.mongo_client['filing_reports'][
            'annotation_reports_view_rows']
        self.source_map = {
            'filing_data': (self.filing_data_collection, 'filing_data'),
            'official_data': (self.official_data_collection, 'official_data_relocation'),
            'reports_view': [
                (self.filing_data_collection, 'filing_data'),
                (self.official_data_collection, 'official_data_relocation')
            ]
        }
        self.only_low_important_set = {'internal_seekingalpha'}
        postgres_uri = os.environ.get('PG_URI_AIRFLOW12_USER_NEWSFEEDSITE') if not postgres_uri else postgres_uri
        if not postgres_uri:
            raise KeyError('postgres_uri not set.')
        self.file_handler = FileFlowHandleV2(postgres_uri=postgres_uri)
        self.data_processor = DocumentProcessor()
        self.max_batch_size = 10000
        self.all_stat_count = {'all': 0, 'skip': 0, 'step_error': 0, 'xbrl': 0, 'file_flow': 0}

    def create_spider_name_source_type_map(self, collections):

        def find_duplicates(keys):
            return [k for k, v in Counter(keys).items() if v > 1]

        map_dict = {}
        pipeline = [{'$group': {'_id': "$x_spider_name"}}]

        for collection, label in collections:
            for document in collection.aggregate(pipeline):
                map_dict[document['_id']] = label

        all_keys = list(map_dict.keys())
        duplicates = find_duplicates(all_keys)
        if duplicates:
            raise KeyError(f"Duplicate x_spider_name found: {duplicates}")

        return map_dict

    def send_xbrl_data_to_mongo(self, xbrl_data_list):
        if not xbrl_data_list:
            return
        report_id_list = list(set([i['_id'] for i in xbrl_data_list]))
        result = self.data_xbrl_convert_collection.find({'_id': {'$in': report_id_list}}, {'_id': 1}).batch_size(self.max_batch_size)
        exists_id_list = [i['_id'] for i in result]
        new_xbrl_data_list = [i for i in xbrl_data_list if i['_id'] not in exists_id_list]
        if not new_xbrl_data_list:
            return
        self.data_xbrl_convert_collection.insert_many(new_xbrl_data_list)
        logger.info(f'{len(new_xbrl_data_list)}-xbrl data inserted.')

    def update_doc_status_to_convert(self, collection, report_id_list):
        if len(report_id_list) == 0:
            return
        collection.update_many({
            '_id': {'$in': report_id_list}
        }, {'$set': {
            "x_status_list.status_convert.status": "convert_init",
            "x_status_list.status_convert.status_txt": "convert_txt_init",
            "x_status_list.status_convert.status_meta": "meta_init",
            "x_updated_date": datetime.now(tz=pytz.timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S%z"),
        }})
        logger.info(f'The document file type cannot be converted.')

    def send_task(self, file_flow_info, tags, is_important, priority, spider_name_source_type):
        for step_str, records in file_flow_info.items():
            steps = step_str.split('@__@')
            start_stage = steps[0]
            target_stage = steps[1]
            x_spider_name = steps[2]

            if start_stage == 'success' or target_stage == 'success':
                self.all_stat_count['skip'] += len(records)
                logger.info(
                    f"{len(records)}--{start_stage}-{target_stage}-{x_spider_name} status: False, message: 'File has already completed the embedding stage.' ")
                continue

            if is_important and x_spider_name not in self.only_low_important_set:
                logger.info(f"is_important: {is_important} - {x_spider_name}")
                status, ids, message = self.file_handler.entry_point_urgent(records=records, start_stage=start_stage,
                                                                            target_stage=target_stage,
                                                                            tags=tags,
                                                                            tag=x_spider_name,
                                                                            priority=priority,
                                                                            source_type=spider_name_source_type[
                                                                                x_spider_name])
            else:
                status, ids, message = self.file_handler.entry_point(records=records, start_stage=start_stage,
                                                                     target_stage=target_stage, tags=tags,tag=x_spider_name,
                                                                     priority=priority,
                                                                     source_type=spider_name_source_type[x_spider_name])
            self.all_stat_count['file_flow'] += len(records)
            logger.info(f"{len(records)}--{start_stage}-{target_stage}-{x_spider_name} status: {status}, message: {message}")


    def process_task_entry(self, source: Literal["filing_data", "official_data", "reports_view"],
                           query: dict, tags: list[str], priority: str,
                           is_important: bool = False):

        if source == 'reports_view':
            collections = self.source_map[source]
        else:
            collections = [self.source_map[source]]

        spider_name_source_type = self.create_spider_name_source_type_map(collections)

        process_data = []
        for collection, label in collections:
            logger.info(f"load {label} data.")
            docs = collection.find(query).batch_size(1000)

            for doc in docs:
                self.all_stat_count['all'] += 1
                process_data.append(self.data_processor.process(doc))
                if len(process_data) >= self.max_batch_size:
                    file_flow_info, xbrl_data, except_id_list, doc_error_list = self.data_processor.split_data_by_spider_name_and_step(
                        process_data)
                    self.all_stat_count['skip'] += len(doc_error_list)
                    self.all_stat_count['step_error'] += len(except_id_list)
                    self.all_stat_count['xbrl'] += len(xbrl_data)
                    self.send_task(file_flow_info, tags, is_important, priority, spider_name_source_type)
                    self.send_xbrl_data_to_mongo(xbrl_data)
                    self.update_doc_status_to_convert(collection, except_id_list)
                    process_data.clear()

            if process_data:
                file_flow_info, xbrl_data, except_id_list, doc_error_list = self.data_processor.split_data_by_spider_name_and_step(
                    process_data)
                self.all_stat_count['skip'] += len(doc_error_list)
                self.all_stat_count['step_error'] += len(except_id_list)
                self.all_stat_count['xbrl'] += len(xbrl_data)
                self.send_task(file_flow_info, tags, is_important, priority, spider_name_source_type)
                self.send_xbrl_data_to_mongo(xbrl_data)
                self.update_doc_status_to_convert(collection, except_id_list)
                process_data.clear()

        logger.info(f"finish processing {self.all_stat_count}.")
