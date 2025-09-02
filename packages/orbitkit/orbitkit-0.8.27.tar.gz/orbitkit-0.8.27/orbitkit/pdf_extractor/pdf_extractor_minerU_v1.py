'''
    @author  : xiaoyu.ma
    @date    : 2025/8/6
    @explain : 
    @version : 1.0
'''
import os
import json
from orbitkit import id_srv

class MinerUExtract:
    # page 中必填项
    page_required = ['page_size', 'page_idx']
    # page 其他参数 【做适配】
    page_extractable_values = ['preproc_blocks', "para_blocks", 'discarded_blocks']
    # 化学公式分类相关暂时不处理
    page_chemical = ['layout_bboxes', '_layout_tree', 'images', 'tables', 'interline_equations', 'need_drop', 'drop_reason']

    page_default = []

    def __init__(self, output_folder, file_path):
        self.blocks = []
        self.pages = []
        self.page_default.extend(self.page_required)
        self.page_default.extend(self.page_extractable_values)
        self.page_default.extend(self.page_chemical)
        self.output_folder = output_folder
        with open(file_path, 'r', encoding='utf-8') as file:
            self.layout_data = json.load(file)

    def extract_process(self):
        # 打印读取的数据
        pdf_info = self.layout_data['pdf_info']
        for pdf_pages in pdf_info:
            self.extract_pages(pdf_pages)

        minerU_reg_file = os.path.join(self.output_folder, 'minerU_reg.txt')
        with open(minerU_reg_file, "w+", encoding='utf-8') as u_pages:
            u_pages.write(json.dumps({
                "_backend": self.layout_data.get('_backend', ''),
                "_version_name": self.layout_data.get('_version_name', '')
            }, ensure_ascii=False) + "\n")

        blocks_file = os.path.join(self.output_folder, 'blocks.txt')
        pages_file = os.path.join(self.output_folder, 'pages.txt')
        with open(pages_file, "w+", encoding='utf-8') as f_pages:
            for page in self.pages:
                f_pages.write(json.dumps(page, ensure_ascii=False) + "\n")

        with open(blocks_file, "w+", encoding='utf-8') as f_blocks:
            for block in self.blocks:
                f_blocks.write(json.dumps(block, ensure_ascii=False) + "\n")

    def check_page_params(self, pdf_pages):
        for pk in pdf_pages.keys():
            if pk not in self.page_default:
                raise Exception(f'参数配置异常，意外参数:{pk}')

    def extract_pages(self, pdf_pages):
        # 做验证 扩展
        self.check_page_params(pdf_pages)
        self.page_size = pdf_pages['page_size']
        self.page = pdf_pages['page_idx'] + 1
        pages_body = self.extract_blocks(pdf_pages)  # \n\n 拼接
        self.pages.append({
            'id': id_srv.get_random_short_id(),
            'page': self.page,
            'sentence': '\n\n'.join(pages_body) + '\n\n' if len(pages_body) > 0 else ''
        })

    def extract_blocks(self, pdf_pages):
        pages_body = []
        block_seq = 0
        for block_method in self.page_extractable_values:
            if block_method in self.page_chemical:
                continue
            handler = getattr(self, block_method, "default_blocks")
            pages_body = handler(pdf_pages, pages_body, block_seq)
        return pages_body

    def preproc_blocks(self, pdf_pages, pages_body, block_seq):
        return self.default_extractable(pdf_pages, 'preproc_blocks', pages_body, block_seq)

    def para_blocks(self, pdf_pages, pages_body, block_seq):
        return self.default_extractable(pdf_pages, 'para_blocks', pages_body, block_seq)

    def discarded_blocks(self, pdf_pages, pages_body, block_seq):
        return self.default_extractable(pdf_pages, 'discarded_blocks', pages_body, block_seq)

    def default_blocks(self, pdf_pages):
        print(pdf_pages.keys())
        raise Exception('提取block方法异常')

    def default_extractable(self, pdf_pages, block_key, pages_body, block_seq):
        '''
            默认提取方法
        :return:
        '''
        for pages_block in pdf_pages.get(block_key, []):
            print(pages_block['type'])
            handler_type_func = getattr(self, f'level_two_{pages_block["type"]}', "level_two_default_blocks")
            block_seq, pages_body = handler_type_func(block_seq, pages_block, pages_body)
        return pages_body

    def get_location(self, bbox):
        location = [bbox[0], self.page_size[1] - bbox[1], bbox[2], self.page_size[1] - bbox[3]]
        return {"location": [location]}

    def level_two_text(self, block_seq, pages_block, pages_body):
        block_type = 'sentence'
        return self.level_two_txt_com(block_seq, pages_block, pages_body, block_type)

    def level_two_discarded(self, block_seq, pages_block, pages_body):
        block_type = 'sentence'
        return self.level_two_txt_com(block_seq, pages_block, pages_body, block_type)

    def level_two_title(self, block_seq, pages_block, pages_body):
        block_type = 'title'
        return self.level_two_txt_com(block_seq, pages_block, pages_body, block_type)

    def level_two_table(self, block_seq, pages_block, pages_body):
        block_type = 'table'
        table_block = pages_block['blocks']
        for table in table_block:
            block_seq = block_seq + 1
            bbox = table['bbox']
            # 设置坐标
            text_location = self.get_location(bbox)
            pages_lines = table["lines"]
            _block_arr, _image_detail_arr = self.get_com_lines(pages_lines)
            if len(_block_arr) > 0 or len(_image_detail_arr) > 0:
                _block_str = '\n'.join(_block_arr)
                self.blocks.append({
                    "id": id_srv.get_random_short_id(),
                    "page": self.page,
                    "seq_no": block_seq,
                    "sentence": _block_str,
                    "type": block_type,
                    "image_detail": _image_detail_arr,
                    "text_location": text_location
                })
                pages_body.append(_block_str)
            else:
                if block_seq > 0:
                    block_seq = block_seq - 1
        return block_seq, pages_body

    def level_two_image(self, block_seq, pages_block, pages_body):
        block_type = 'image'
        pages_image_blocks = pages_block["blocks"]
        # 多一个层级
        for _pages_image_blocks in pages_image_blocks:
            # image_caption/image_body
            block_seq = block_seq + 1
            _pages_image_blocks_type = _pages_image_blocks['type']
            pages_image_blocks_line = _pages_image_blocks["lines"]
            bbox = pages_block['bbox']
            if _pages_image_blocks_type == 'image_body':
                block_type = 'image'
            elif _pages_image_blocks_type in ['image_caption', 'image_footnote']:
                block_type = 'sentence'
            else:
                raise Exception(f'Image 异常目标值 {_pages_image_blocks_type}:')
            # 设置坐标
            text_location = self.get_location(bbox)
            _block_arr, _image_detail_arr = self.get_com_lines(pages_image_blocks_line)
            if len(_block_arr) > 0 or len(_image_detail_arr) > 0:
                _block_arr_str = '\n'.join(_block_arr)
                self.blocks.append({
                    "id": id_srv.get_random_short_id(),
                    "page": self.page,
                    "seq_no": block_seq,
                    "sentence": _block_arr_str,
                    "type": block_type,
                    "image_detail": _image_detail_arr,
                    "text_location": text_location
                })
            else:
                if block_seq > 0:
                    block_seq = block_seq - 1
        return block_seq, pages_body

    def level_two_interline_equation(self, block_seq, pages_block, pages_body):
        block_type = 'equation'
        block_seq = block_seq + 1
        bbox = pages_block['bbox']
        # 设置坐标
        text_location = self.get_location(bbox)
        pages_lines = pages_block["lines"]
        _block_arr, _image_detail_arr = self.get_com_lines(pages_lines)
        if len(_block_arr) > 0 or len(_image_detail_arr) > 0:
            _block_str = '\n'.join(_block_arr)
            self.blocks.append({
                "id": id_srv.get_random_short_id(),
                "page": self.page,
                "seq_no": block_seq,
                "sentence": _block_str,
                "type": block_type,
                "image_detail": _image_detail_arr,
                "text_location": text_location
            })
            pages_body.append(_block_str)
        else:
            if block_seq > 0:
                block_seq = block_seq - 1
        return block_seq, pages_body

    def level_two_txt_com(self, block_seq, pages_block, pages_body, block_type):
        block_seq = block_seq + 1
        bbox = pages_block['bbox']
        # 设置坐标
        text_location = self.get_location(bbox)
        pages_lines = pages_block["lines"]
        _block_arr, _image_detail_arr = self.get_com_lines(pages_lines)
        if len(_block_arr) > 0 or len(_image_detail_arr) > 0:
            _block_str = '\n'.join(_block_arr)
            self.blocks.append({
                "id": id_srv.get_random_short_id(),
                "page": self.page,
                "seq_no": block_seq,
                "sentence": _block_str,
                "type": block_type,
                "image_detail": _image_detail_arr,
                "text_location": text_location
            })
            pages_body.append(_block_str)
        else:
            if block_seq > 0:
                block_seq = block_seq - 1
        return block_seq, pages_body

    def level_two_default_blocks(self, block_seq, pages_block, pages_body):
        print(pages_block.keys())
        raise Exception('提取block方法异常')

    def get_com_lines(self, pages_lines):
        _block_arr = []
        _c_s = []
        _img = []
        for _line in pages_lines:
            # image_body, 'image_caption', 'image_footnote'
            for _l in _line['spans']:
                if _l['type'] in ['text', 'title', 'inline_equation', 'interline_equation']:
                    _c_s.append(_l['content'])
                elif _l['type'] in ['table']:
                    _c_s.append(_l['html'])
                # elif _l['type'] in ['interline_equation']:
                #     _c_s.append(_l['content'])
                #     # _img.append(f'images/{_l["image_path"]}')
                elif _l['type'] in ['image']:
                    # _img.append(f'images/{_l["image_path"]}')
                    pass
                else:
                    raise Exception(f'类型匹配异常 意外值: {_l["type"]}')
                if _l.get('image_path', None):
                    _img.append(f'images/{_l["image_path"]}')
            if len(_c_s) > 0:
                _block_arr.append(' '.join(_c_s))
        return _block_arr, _img