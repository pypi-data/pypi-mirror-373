import datetime
import os
import logging
from contextlib import contextmanager
from typing import List, Dict, Tuple, Any, Union, Optional
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, MetaData, Table, select, Column, Integer, insert, and_, text, delete, update

logger = logging.getLogger(__name__)


class FileFlowHandle:

    def __init__(self, not_allow_file_type_list=None, postgres_url=None, database_name=None):
        self.postgres_url = postgres_url or os.environ['PG_URI_AIRFLOW12_USER_NEWSFEEDSITE']
        if not self.postgres_url:
            raise ValueError("mongo_url cannot be None or empty. Please provide a valid mongo_url.")
        self.databases = database_name or "process_net"
        self.postgres_engine = create_engine(f"{self.postgres_url}/{self.databases}", connect_args={"sslmode": "require"})
        self.postgres_session = sessionmaker(bind=self.postgres_engine)
        self.Session = scoped_session(self.postgres_session)
        self.postgres_metadata = MetaData()

        self.table_op_attachment = Table(
            'op_attachment', self.postgres_metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            autoload_with=self.postgres_engine, schema='public'
        )
        self.table_op_meta = Table(
            'op_meta', self.postgres_metadata,
            autoload_with=self.postgres_engine, schema='public'
        )
        self.table_op_step = Table(
            'op_step', self.postgres_metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            autoload_with=self.postgres_engine, schema='public'
        )

        self.table_op_meta_backup = Table(
            'op_meta_backup', self.postgres_metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            autoload_with=self.postgres_engine, schema='public'
        )

        self.not_allow_file_type_list = not_allow_file_type_list or ['.xhtml']

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            self.Session.remove()

    def _validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        required_fields = ['start_stage', 'target_stage', 'tag_name']
        for field in required_fields:
            if not params.get(field):
                if field in ['start_stage', 'target_stage'] and params.get(field) not in ['convert', 'extract',
                                                                                          'embedding']:
                    return False, f"The value of '{field}' must be one of ['convert', 'extract', 'embedding']."
                return False, f"'{field}' cannot be empty."

        if int(params['priority']) > 10 and params['urgent'] is False:
            return False, f"The priority of '{params.get('priority')}' must be greater than 10."

        allowed_methods = {"netmind", "pdfplumber"}
        if params.get("extract_method") not in allowed_methods:
            return False, f"Invalid extract_method: {params.get('extract_method')}. Allowed: {allowed_methods}"

        return True, ""

    def _validate_record(self, record: Dict[str, Any]) -> Tuple[bool, str]:
        if not record.get('id'):
            return False, "Record 'id' is required."
        if not record.get('s3_path_info'):
            return False, "'s3_path_info' is required and cannot be empty."
        for i in record['s3_path_info']:
            if not i.get('store_path') or not i.get('file_name'):
                return False, "'store_path' or 'file_name' is required and cannot be empty."
            file_type = '.' + str(i['store_path']).split('.')[-1].lower()
            if self.not_allow_file_type_list and file_type in self.not_allow_file_type_list:
                return False, f"'file_type' {file_type} is invalid."
        return True, ""

    def _get_existing_ids(self, ids: List[str]) -> List[str]:
        if not ids:
            return []

        stmt = select(self.table_op_meta.c.id).where(self.table_op_meta.c.id.in_(ids))
        with self.session_scope() as session:
            result = session.execute(stmt)
            return [row[0] for row in result.fetchall()]

    def _check_records(self, records: List[Dict[str, Any]]) -> Tuple[bool, List[str], str]:
        ids = []
        record_count = 0
        for record in records:
            record_count += 1
            is_valid, msg = self._validate_record(record)
            if not is_valid:
                return False, [record.get("id", "unknown")], msg
            ids.append(record["id"])

        existing_ids = self._get_existing_ids(ids)
        if len(existing_ids) == record_count:
            return False, existing_ids, "No new data has been inserted."
        return True, existing_ids, f"Validation complete. total: {len(records)}. {len(existing_ids)} records already exist."

    def _build_insert_data(
            self, record: Dict[str, Any], params: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
        now = datetime.datetime.now(datetime.timezone.utc)
        attachments = []
        for item in record['s3_path_info']:
            file_type = '.' + str(item['store_path']).split('.')[-1].lower()
            attachments.append({
                'meta_id': record['id'],
                'store_path': item['store_path'],
                'file_name': item['file_name'],
                'file_type': file_type,
                'category': 'x_attachments' if params['start_stage'] == 'convert' else 'x_attachments_pdf',
                'created_at': now
            })
        tags = params.get('tags_extend') or []
        meta = {
            'id': record['id'],
            'propagation_id': record['id'],
            'priority': params['priority'],
            'status': 'init',
            'start_stage': params['start_stage'],
            'current_stage': params['current_stage'],
            'target_stage': params['target_stage'],
            'data_source': params['source_type'],
            'created_at': now,
            'updated_at': now,
            'tags': [params['tag_name'], params['extract_method']] + tags,
        }

        step = {
            'meta_id': record['id'],
            'stage': 'init',
            'status': 'init',
            'created_at': now
        }

        return attachments, meta, step

    def _insert_data_to_queue(self, insert_info: List[Dict[str, Any]]):
        with self.session_scope() as session:
            for item in insert_info:
                table = item['table']
                insert_data = item['data']
                stmt = insert(table)
                session.execute(stmt, insert_data)

    def _delete_and_backup_data_from_queue(self, postgres_coon, meta_data):
        meta_id = meta_data['id']
        meta_data['meta_id'] = meta_id
        meta_data.pop('id')
        utcnow = datetime.datetime.now(datetime.timezone.utc)

        # 备份数据
        stmt_insert_backup = insert(self.table_op_meta_backup)
        postgres_coon.execute(stmt_insert_backup, meta_data)

        # 添加履历
        op_step_data = {
            'stage': 'backup',
            'status': 'success',
            'meta_id': meta_id,
            'message': None,
            'created_at': utcnow,
        }
        stmt = insert(self.table_op_step)
        postgres_coon.execute(stmt, op_step_data)

        # 删除数据
        stmt_del_op_meta = delete(self.table_op_meta).where(self.table_op_meta.c.id == meta_id)
        stmt_del_op_x_attachments = delete(self.table_op_attachment).where(self.table_op_attachment.c.meta_id == meta_id)
        postgres_coon.execute(stmt_del_op_meta)
        postgres_coon.execute(stmt_del_op_x_attachments)

    def _update_failed_record_to_manual(self, postgres_coon, op_meta_id):
        op_meta_stmt = (
            update(self.table_op_meta)
            .where(text("id = :op_meta_id"))
            .values(
                status='manual',
                updated_at=datetime.datetime.now(datetime.timezone.utc)
            )
        )

        postgres_coon.execute(op_meta_stmt, {'op_meta_id': op_meta_id})

    def file_flow_entry_point(
            self,
            records: List[Dict[str, Any]],
            start_stage: str,
            target_stage: str,
            tag_name: str,
            extract_method: str = 'netmind',
            priority: str = '1',
            source_type: Optional[str] = None,
            tags_extend: Optional[List[str]] = None
    ) -> Tuple[bool, Any, str]:
        """
            普通任务接口

            :param records: 待处理的文件记录列表，每个记录是一个字典，必须包含唯一的 'id' 字段。
            :type records: List[Dict[str, Any]]
            :param start_stage: 文件处理流程的起始阶段。
            :type start_stage: str
            :param target_stage: 文件处理流程的目标阶段。
            :type target_stage: str
            :param tag_name: 标签名称，用于标识任务或处理流。
            :type tag_name: str
            :param extract_method: 提取方式，默认为 'netmind'，可根据具体业务自定义。
            :type extract_method: str, optional
            :param priority: 任务优先级，默认为 '1'，数值越小优先级越低。
            :type priority: str, optional
            :param source_type: 数据来源类型，默认为空字符串。
            :type source_type: str, optional 数据来源
            :tags_extend: List[str] tags中的扩展信息

            :return: 包含三个元素的元组：
                     - 第一个元素表示是否成功（True/False）；
                     - 第二个元素为已存在记录的 ID 列表（或空字符串）；
                     - 第三个元素为提示信息或错误信息。
            :rtype: Tuple[bool, Any, str]
        """
        return self._file_flow_entry_point_internal(
            records, start_stage, target_stage, tag_name,
            extract_method, priority, source_type, tags_extend,
            urgent=False
        )

    def file_flow_entry_point_urgent(
            self,
            records: List[Dict[str, Any]],
            start_stage: str,
            target_stage: str,
            tag_name: str,
            extract_method: str = 'netmind',
            priority: str = '1',
            source_type: Optional[str] = None,
            tags_extend: Optional[List[str]] = None
    ) -> Tuple[bool, Any, str]:
        """
            加急任务接口

            :param records: 待处理的文件记录列表，每个记录是一个字典，必须包含唯一的 'id' 字段。
            :type records: List[Dict[str, Any]]
            :param start_stage: 文件处理流程的起始阶段。
            :type start_stage: str
            :param target_stage: 文件处理流程的目标阶段。
            :type target_stage: str
            :param tag_name: 标签名称，用于标识任务或处理流。
            :type tag_name: str
            :param extract_method: 提取方式，默认为 'netmind'，可根据具体业务自定义。
            :type extract_method: str, optional
            :param priority: 任务优先级，默认为 '1'，数值越小优先级越低。
            :type priority: str, optional
            :param source_type: 数据来源类型，默认为空字符串。
            :type source_type: str, optional 数据来源
            :tags_extend: List[str] tags中的扩展信息

            :return: 包含三个元素的元组：
                     - 第一个元素表示是否成功（True/False）；
                     - 第二个元素为已存在记录的 ID 列表（或空字符串）；
                     - 第三个元素为提示信息或错误信息。
            :rtype: Tuple[bool, Any, str]
        """
        return self._file_flow_entry_point_internal(
            records, start_stage, target_stage, tag_name,
            extract_method, priority, source_type, tags_extend,
            urgent=True
        )

    def _file_flow_entry_point_internal(
            self,
            records: List[Dict[str, Any]],
            start_stage: str,
            target_stage: str,
            tag_name: str,
            extract_method: str,
            priority: str,
            source_type: Optional[str],
            tags_extend: Optional[List[str]],
            urgent: bool
    ) -> Tuple[bool, Any, str]:
        """核心处理逻辑"""
        params = {
            'start_stage': start_stage,
            'target_stage': target_stage,
            'tag_name': tag_name,
            'extract_method': extract_method,
            'priority': priority,
            'current_stage': start_stage,
            'source_type': source_type,
            'tags_extend': tags_extend,
            'urgent': urgent
        }

        is_valid, msg = self._validate_params(params)
        if not is_valid:
            return False, "", msg

        if isinstance(records, dict):
            records = [records]
        elif not isinstance(records, list):
            raise ValueError("records must be a dict or list of dicts.")

        is_valid, existing_ids, msg = self._check_records(records)
        if not is_valid:
            return False, existing_ids, msg
        logger.info(msg)

        batch_size = 1000
        attachments_batch, meta_batch, step_batch = [], [], []

        count = 0
        for record in records:
            if record['id'] in existing_ids:
                continue

            attachments, meta, step = self._build_insert_data(record, params)
            attachments_batch.extend(attachments)
            meta_batch.append(meta)
            step_batch.append(step)
            count += 1

            if len(meta_batch) >= batch_size:
                self._insert_data_to_queue([
                    {'table': self.table_op_attachment, 'data': attachments_batch},
                    {'table': self.table_op_meta, 'data': meta_batch},
                    {'table': self.table_op_step, 'data': step_batch}
                ])
                attachments_batch.clear()
                meta_batch.clear()
                step_batch.clear()

        if meta_batch:
            self._insert_data_to_queue([
                {'table': self.table_op_attachment, 'data': attachments_batch},
                {'table': self.table_op_meta, 'data': meta_batch},
                {'table': self.table_op_step, 'data': step_batch}
            ])

        return True, "", f"Data successfully queued. inserted_count: {count}"

    def file_flow_exit_point(
            self,
            tags: Union[str, List[str]],
            report_id: str = None,
            status: str = None,
            limit_size: int = 10000
    ) -> List[Dict[str, Any]]:
        """
        从 op_meta 表中读取数据。
        数据被读取默认删除op_meta,op_xattachments中信息,备份信息储存到op_backup表中。

        :param limit_size: 每次返回的数据条数
        :param tags: 查询过滤条件，'test_tag_name' | ['test_tag_name', 'xxxx']
        :param report_id: 查询过滤条件，'test_report_id'
        :param status: 查询过滤条件，'success'
        :return: 查询结果列表
        """
        op_meta = self.table_op_meta
        op_attachment = self.table_op_attachment

        conditions = []
        if status:
            conditions.append(op_meta.c.status == status)

        if tags and isinstance(tags, str):
            conditions.append(op_meta.c.tags.any(tags))
        if tags and isinstance(tags, list):
            conditions.append(op_meta.c.tags.contains(array(tags)))

        if report_id:
            conditions.append(op_meta.c.report_id == report_id)

        meta_subquery = (
            select(op_meta)
            .where(and_(*conditions)) if conditions else select(op_meta)
        )
        meta_subquery = meta_subquery.limit(limit_size).subquery()
        join_stmt = meta_subquery.outerjoin(op_attachment, meta_subquery.c.id == op_attachment.c.meta_id)
        stmt = select(meta_subquery, op_attachment).select_from(join_stmt)

        with self.session_scope() as session:
            result = session.execute(stmt).fetchall()

            meta_map = {}
            for row in result:
                row_dict = dict(row._mapping)
                meta_id = row_dict['id']

                meta_fields: Dict[str, Any] = {k: v for k, v in row_dict.items() if k in op_meta.c}
                attachment_fields: Dict[str, Any] = {k: v for k, v in row_dict.items() if k in op_attachment.c}

                meta_fields['created_at'] = meta_fields['created_at'].isoformat()
                meta_fields['updated_at'] = meta_fields['updated_at'].isoformat()
                attachment_fields['created_at'] = attachment_fields['created_at'].isoformat()
                attachment_fields['updated_at'] = attachment_fields['updated_at'].isoformat()
                if meta_id not in meta_map:
                    meta_fields['x_attachments'] = []
                    meta_map[meta_id] = meta_fields

                meta_map[meta_id]['x_attachments'].append(attachment_fields)

            result_data = list(meta_map.values())
            for item in result_data:
                yield item
                try:
                    status = item['status']
                    meta_id = item['id']
                    if status == 'success':
                        self._delete_and_backup_data_from_queue(session, item)
                    elif status == 'failed':
                        self._update_failed_record_to_manual(session, meta_id)
                    else:
                        logger.info(f"Data is still processing. Current status: {status}")
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
