import json
import os.path
import requests
import logging
from enum import Enum
from typing import Dict, Literal, List
from orbitkit import id_srv
from dataclasses import dataclass

try:
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import Image, Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics, ttfonts
except ImportError:
    raise ImportError(
        "reportlab is not installed. Please install it with `pip install reportlab`."
    )


logger = logging.getLogger(__name__)


def init_asset():
    """
    初始化生成 pdf 所需的静态资源
    """

    arial_font_url = 'https://orbit-common-resources.s3.us-west-2.amazonaws.com/asset/font/Arial.ttf'
    nsimsun_font_url = 'https://orbit-common-resources.s3.us-west-2.amazonaws.com/asset/font/Nsimsun.TTF'
    logo_png_url = 'https://orbit-common-resources.s3.us-west-2.amazonaws.com/asset/img/logo.png'
    icon_s_png = 'https://orbit-common-resources.s3.us-west-2.amazonaws.com/asset/img/icon_s.png'
    icon_qa_png = 'https://orbit-common-resources.s3.us-west-2.amazonaws.com/asset/img/icon_qa.png'

    resource_dir_name = 'asset'
    if not os.path.exists(resource_dir_name):
        os.mkdir(resource_dir_name)

    font_dir_name = os.path.join(resource_dir_name, 'font')
    if not os.path.exists(font_dir_name):
        os.mkdir(font_dir_name)

    img_dir_name = os.path.join(resource_dir_name, 'img')
    if not os.path.exists(img_dir_name):
        os.mkdir(img_dir_name)

    arial_font_file_name = os.path.join(font_dir_name, 'Arial.ttf')
    nsimsun_font_file_name = os.path.join(font_dir_name, 'Nsimsun.TTF')
    logo_png_file_name = os.path.join(img_dir_name, 'logo.png')
    icon_s_png_file_name = os.path.join(img_dir_name, 'icon_s.png')
    icon_qa_png_file_name = os.path.join(img_dir_name, 'icon_qa.png')

    def download_file(url, file_name):
        if not os.path.exists(file_name):
            r = requests.get(url, allow_redirects=True)
            open(file_name, 'wb').write(r.content)
            logger.warning(f"Download file: {file_name} from {url}")

    if not os.path.exists(arial_font_file_name):
        download_file(arial_font_url, arial_font_file_name)
    if not os.path.exists(nsimsun_font_file_name):
        download_file(nsimsun_font_url, nsimsun_font_file_name)
    if not os.path.exists(logo_png_file_name):
        download_file(logo_png_url, logo_png_file_name)
    if not os.path.exists(icon_s_png_file_name):
        download_file(icon_s_png, icon_s_png_file_name)
    if not os.path.exists(icon_qa_png_file_name):
        download_file(icon_qa_png, icon_qa_png_file_name)

    return True


def get_str(item, key):
    if key not in item:
        return "N/A"
    if item[key] is None:
        return "N/A"
    if item[key] == "":
        return "N/A"
    return item[key]


class _PdfColorEm(Enum):
    FOOTER_SPLIT_LINE = "#4884E9"
    FOOTER_WORDING = "#666666"
    TITLE_BG = "#4c82df"
    META_BG = "#F5F5F5"
    TITLE_COLOR = "#4C82DF"


@dataclass
class PdfContent:
    title: str
    sub_title: str
    statements: List[str]
    qa_dict: Dict[str, str]


class PdfWriter:
    def __init__(self, lang: Literal['zh', 'en'], content: PdfContent, export_path: str, pdf_file_name: str):
        """
        :param lang: 语言，中文报告请选择 zh，非中文报告选择 en
        :param content: pdf 文件内容
        :param export_path: 生成 pdf 文件的路径
        :param pdf_file_name: 生成 pdf 文件名
        """

        result = init_asset()
        if not result:
            raise Exception("初始化资源失败！")

        pdfmetrics.registerFont(ttfonts.TTFont("Nsimsun", "asset/font/Nsimsun.TTF"))
        pdfmetrics.registerFont(ttfonts.TTFont("Arial", "asset/font/Arial.ttf"))

        self.font_face = "Helvetica"  # Default font-face for reportlab
        self.page_width, self.page_height = A4  # 595.27 # 841.89
        self.margin_top = self.margin_bottom = 20
        self.margin_left = self.margin_right = 30
        self.page_eff_width = self.page_width - (self.margin_left + self.margin_right)

        self._generate_buffer_enum()
        # Mark page info
        self.current_page = 1
        self.top_offset_height = self.margin_top
        self.top_offset_height_max = self.page_height - self.margin_bottom - self.buffer_room["bf_40"] - \
                                     self.buffer_room["bf_10"]
        logger.debug(f"page_height: {self.page_height}, {self.top_offset_height_max}")  # 841.89, 771.89

        # Get write_json by lang
        self.content = content
        # Setup wordwrap
        self.word_wrap = None
        self._setup_word_wrap(lang=lang)
        self._setup_font_face(lang=lang)

        # Output files
        self.block_txt = []
        self.page_txt = []
        self.block_txt_seq = 1
        self.pdf_file = os.path.join(export_path, pdf_file_name)
        self.page_txt_file = os.path.join(export_path, "page.txt")
        self.block_txt_file = os.path.join(export_path, "block.txt")
        self.c = Canvas(self.pdf_file, pagesize=A4)

    def _reset_remaining_top_offset_height(self):
        self.top_offset_height = self.margin_top  # From top to bottom, the effective write area.

    def write(self, with_block_and_page=False, statements_with_img=True, question_with_img=True):
        """
        生成 pdf
        """
        # Write INFO into the 1st page,
        # I assume there will be enough space to hold the information.
        self._write_footer()
        self._write_title()

        self._move_down_space(bf_x="bf_10")

        for statement in self.content.statements:
            self._write_s(statement, statements_with_img)

        self._write_q('', with_icon=False)

        # Start to write content
        for question, answer in self.content.qa_dict.items():
            if question:
                self._write_q(question, with_icon=question_with_img)
            answer_list = answer.split("\n")
            for answer_item in answer_list:
                answer_item = answer_item.strip()
                if answer_item:
                    self._write_a(answer_item)

        # If QA[] is empty, then signoff current page
        # If invoke _goto_next_page method, then signoff the final result
        # If NOT invoke _goto_next_page method, then signoff the final result
        self._goto_next_page(last=True)

        self.c.save()

        if with_block_and_page:
            with open(self.block_txt_file, "w+", encoding="utf-8") as f:
                for item in self.block_txt:
                    f.write(json.dumps(item, ensure_ascii=False))
                    f.write("\n")
            with open(self.page_txt_file, "w+", encoding="utf-8") as f:
                for item in self.page_txt:
                    f.write(json.dumps(item, ensure_ascii=False))
                    f.write("\n")

    def _setup_word_wrap(self, lang):
        if lang == "zh":
            self.word_wrap = "CJK"
            return
        if lang == "en":
            self.word_wrap = None
            return
        raise Exception("Lang err!")

    def _setup_font_face(self, lang):
        if lang == "zh":
            self.font_face = "Nsimsun"
            return
        if lang == "en":
            self.font_face = "Arial"
            return
        raise Exception("Lang err!")

    def _goto_next_page(self, last=False):
        self._dump_block_2_page()
        self.c.showPage()

        if last is False:
            self.current_page += 1
            self.block_txt_seq = 1
            self._reset_remaining_top_offset_height()
            self._write_footer()
            logger.info(f"[GOTO NEXT PAGE] Top offset: {self.top_offset_height}, Page: {self.current_page}")

    def _move_down_space(self, bf_x):
        self.top_offset_height = self.top_offset_height + self.buffer_room[bf_x]

        if self.top_offset_height > self.top_offset_height_max:
            self._goto_next_page()
        logger.debug(f"Top offset: {self.top_offset_height}, Page: {self.current_page}")

    def _get_location(self, x, y, height):
        return [x, y + height, x + self.page_eff_width, y]

    def _dump_block_2_page(self):
        page_txt = ""
        for item in self.block_txt:
            if item["page"] == self.current_page:
                page_txt = page_txt + item["sentence"] + "\n"

        self.page_txt.append({
            "id": f"p_{id_srv.get_random_short_id()}",
            "page": self.current_page,
            "sentence": page_txt,
        })

    def _collect_block_text(self, sentence, location, text_type="text"):
        text_block_obj = {
            "id": f"l_{id_srv.get_random_short_id()}",
            'page': self.current_page,
            'seq_no': self.block_txt_seq,
            'sentence': sentence,
            'type': text_type,
            'text_location': {"location": location},
        }
        self.block_txt.append(text_block_obj)
        self.block_txt_seq += 1

    def _generate_buffer_enum(self):
        self.buffer_room = {}
        for i in range(1, 900):
            self.buffer_room["bf_" + str(i)] = i

    def _write_footer(self):
        """
        Total footer height should be:
        footer_height(40) + margin_bottom(20) = 60
        """
        footer_height = 40
        # Draw line
        self.c.setStrokeColor(colors.HexColor(_PdfColorEm.FOOTER_SPLIT_LINE.value))
        self.c.line(30, self.margin_bottom + footer_height, self.page_width - 30, self.margin_bottom + footer_height)
        # Draw wording
        self.c.setFillColor(colors.HexColor(_PdfColorEm.FOOTER_WORDING.value))
        self.c.setFont(self.font_face, 10)
        self.c.drawString(30, self.margin_bottom + 20, "ORBIT FINANCIAL TECHNOLOGY LIMITED")
        self.c.drawString(30, self.margin_bottom + 3, "https://www.orbitfin.ai/")
        # Draw log
        image = Image("asset/img/logo.png", width=90, height=30)  # 替换为您的图片路径和尺寸
        image.drawOn(self.c, self.page_width - 120, 20)

    def _write_title(self):
        title_block_style = ParagraphStyle(name="titleStyle",
                                           fontName=self.font_face,
                                           fontSize=16,
                                           leading=20,
                                           textColor=colors.white,
                                           wordWrap=self.word_wrap)

        paragraph = Paragraph(self.content.title, title_block_style)
        info_real_width, info_real_height = paragraph.wrap(self.page_eff_width, self.page_height)
        info_position_x = self.margin_left
        info_position_y = self.page_height - info_real_height - self.buffer_room["bf_10"]

        # Draw blue area ------
        rect_height = (info_real_height + self.buffer_room["bf_10"]) + self.buffer_room["bf_30"]
        rect_position_y = self.page_height - (info_real_height + self.buffer_room["bf_10"]) - self.buffer_room["bf_30"]
        self.c.setFillColor(colors.HexColor(_PdfColorEm.TITLE_BG.value))
        self.c.rect(0, rect_position_y, self.page_width, rect_height, fill=True, stroke=False)
        # Draw blue area ------

        paragraph.drawOn(self.c, info_position_x, info_position_y)

        # Write subtitle
        self.c.setFillColor(colors.white)  # 将文本颜色设置为白色
        self.c.setFont(self.font_face, 12)
        self.c.drawString(self.margin_left, self.page_height - info_real_height - self.buffer_room["bf_30"],
                          self.content.sub_title)

        # remaining_height & top_offset_height
        self.top_offset_height = self.page_height - rect_position_y

        # >>>>>>>>> Write txt block <<<<<<<<<
        sentence = self.content.title + "\n"
        if self.content.sub_title:
            sentence += self.content.sub_title
        self._collect_block_text(sentence,
                                 [self._get_location(x=self.margin_left, y=rect_position_y, height=rect_height)])
        # >>>>>>>>> Write txt block <<<<<<<<<

        logger.debug(f"Top offset: {self.top_offset_height}, Page: {self.current_page}")

    def _draw_rect(self, color, start_x, start_y, width, height):
        self.c.setFillColor(colors.HexColor(color))
        self.c.rect(start_x, start_y, width, height, fill=True, stroke=False)

    def _dump_paragraph_lines(self, p):
        text_lines = []
        lines = p.blPara.lines
        for ind, line in enumerate(lines):
            line = lines[ind]
            if hasattr(line, 'words'):
                words = line.words
            else:
                words = line[1]

            words_new = [getattr(word, 'text', word) for word in words]
            text_lines.append(" ".join(words_new))
        return text_lines

    def _write_meta_block(self, meta_key, meta_value, meta_paragraph):
        # Write title...
        if self.top_offset_height + self.buffer_room["bf_30"] > self.top_offset_height_max:
            self._goto_next_page()

        collect_point_start = collect_point_end = self.top_offset_height
        collect_point_str = ""

        self._draw_rect(_PdfColorEm.META_BG.value,
                        self.margin_left - 10,
                        self.page_height - self.top_offset_height - self.buffer_room["bf_10"],
                        self.page_eff_width + 20,
                        self.buffer_room["bf_10"])
        self._move_down_space(bf_x="bf_10")

        paragraph_style_title = ParagraphStyle(name="titleStyle",
                                               fontName=self.font_face,
                                               leading=20,
                                               fontSize=12,
                                               textColor=_PdfColorEm.TITLE_COLOR.value,
                                               wordWrap=self.word_wrap)
        paragraph_title = Paragraph(meta_key, paragraph_style_title)
        info_real_width, info_real_height = paragraph_title.wrap(self.page_eff_width, self.page_height)
        self._draw_rect(_PdfColorEm.META_BG.value,
                        self.margin_left - 10,
                        self.page_height - self.top_offset_height - self.buffer_room["bf_20"],
                        self.page_eff_width + 20,
                        self.buffer_room["bf_20"])
        paragraph_title.drawOn(self.c, self.margin_left,
                               self.page_height - self.top_offset_height - self.buffer_room["bf_20"])

        collect_point_str = collect_point_str + meta_key + "\n"

        self.top_offset_height += self.buffer_room["bf_20"]

        # Write content...
        paragraph = Paragraph(meta_value, meta_paragraph)
        info_real_width, info_real_height = paragraph.wrap(self.page_eff_width, self.page_height)

        if self.top_offset_height + info_real_height > self.top_offset_height_max:  # 流写
            all_para_lines = self._dump_paragraph_lines(paragraph)
            for para_line in all_para_lines:
                if self.top_offset_height + 15 > self.top_offset_height_max:
                    # 收集一下 & goto next page
                    collect_point_end = self.top_offset_height
                    self._collect_block_text(collect_point_str, [
                        self._get_location(x=self.margin_left, y=self.page_height - self.top_offset_height,
                                           height=collect_point_end - collect_point_start)
                    ])

                    self._goto_next_page()

                    collect_point_start = collect_point_end = self.top_offset_height
                    collect_point_str = ""

                paragraph_line = Paragraph(para_line, meta_paragraph)
                paragraph_line.wrap(self.page_eff_width, self.page_height)
                self._draw_rect(_PdfColorEm.META_BG.value,
                                self.margin_left - 10,
                                self.page_height - self.top_offset_height - 15,
                                self.page_eff_width + 20,
                                15)
                paragraph_line.drawOn(self.c, self.margin_left, self.page_height - self.top_offset_height - 15)
                self.top_offset_height += 15

                # 收集一下
                collect_point_str = collect_point_str + para_line + "\n"
                collect_point_end = self.top_offset_height
                logger.debug(f"Top offset: {self.top_offset_height}, Page: {self.current_page}")

            self._collect_block_text(collect_point_str, [
                self._get_location(x=self.margin_left, y=self.page_height - self.top_offset_height,
                                   height=collect_point_end - collect_point_start)
            ])
        else:  # 整写
            position_x = self.margin_left
            position_y = self.page_height - self.top_offset_height - info_real_height
            self._draw_rect(_PdfColorEm.META_BG.value,
                            self.margin_left - 10,
                            position_y,
                            self.page_eff_width + 20,
                            info_real_height)
            paragraph.drawOn(self.c, position_x, position_y)
            self.top_offset_height += info_real_height

            # 收集一下
            collect_point_str = collect_point_str + meta_value + "\n"
            collect_point_end = self.top_offset_height
            self._collect_block_text(collect_point_str, [
                self._get_location(x=self.margin_left, y=self.page_height - self.top_offset_height,
                                   height=collect_point_end - collect_point_start)
            ])

            logger.debug(f"Top offset: {self.top_offset_height}, Page: {self.current_page}")

    def _write_content_block(self, content, text_color="", font_size=12, with_icon=True, icon_path=""):
        self._move_down_space(bf_x="bf_10")

        if with_icon:
            # Draw icon
            icon_dim = 15
            if self.top_offset_height + icon_dim > self.top_offset_height_max:  # Judge if we have enough room for icon pic.
                self._goto_next_page()

            image = Image(icon_path, width=icon_dim, height=icon_dim)
            image.drawOn(self.c, self.margin_left - self.buffer_room["bf_10"],
                         self.page_height - self.top_offset_height - icon_dim)

        collect_point_start = collect_point_end = self.top_offset_height
        collect_point_str = ""

        # Draw content
        paragraph_style = ParagraphStyle(name="titleStyle",
                                         leading=15,
                                         fontName=self.font_face,
                                         textColor=text_color,
                                         fontSize=font_size,
                                         wordWrap=self.word_wrap)
        paragraph = Paragraph(content, paragraph_style)
        info_real_width, info_real_height = paragraph.wrap(self.page_eff_width - self.buffer_room["bf_10"],
                                                           self.page_height)

        if self.top_offset_height + info_real_height > self.top_offset_height_max:  # 流写
            all_para_lines = self._dump_paragraph_lines(paragraph)
            for para_line in all_para_lines:
                if self.top_offset_height + 15 > self.top_offset_height_max:
                    # 收集一下 & goto next page
                    collect_point_end = self.top_offset_height
                    self._collect_block_text(collect_point_str,
                                             [self._get_location(x=self.margin_left + self.buffer_room["bf_10"],
                                                                 y=self.page_height - self.top_offset_height,
                                                                 height=collect_point_end - collect_point_start)])

                    self._goto_next_page()

                    collect_point_start = collect_point_end = self.top_offset_height
                    collect_point_str = ""

                paragraph_line = Paragraph(para_line, paragraph_style)
                paragraph_line.wrap(self.page_eff_width - self.buffer_room["bf_10"], self.page_height)
                paragraph_line.drawOn(self.c, self.margin_left + self.buffer_room["bf_10"],
                                      self.page_height - self.top_offset_height - 15)
                self.top_offset_height += 15

                # 收集一下
                collect_point_str = collect_point_str + para_line + "\n"
                collect_point_end = self.top_offset_height
                logger.debug(f"Top offset: {self.top_offset_height}, Page: {self.current_page}")

            self._collect_block_text(collect_point_str,
                                     [self._get_location(x=self.margin_left + self.buffer_room["bf_10"],
                                                         y=self.page_height - self.top_offset_height,
                                                         height=collect_point_end - collect_point_start)])
        else:  # 整写
            position_x = self.margin_left + self.buffer_room["bf_10"]
            position_y = self.page_height - self.top_offset_height - info_real_height
            paragraph.drawOn(self.c, position_x, position_y)
            self.top_offset_height += info_real_height

            # 收集一下
            collect_point_str = collect_point_str + content + "\n"
            collect_point_end = self.top_offset_height
            self._collect_block_text(collect_point_str,
                                     [self._get_location(x=self.margin_left + self.buffer_room["bf_10"],
                                                         y=self.page_height - self.top_offset_height,
                                                         height=collect_point_end - collect_point_start)])

        logger.debug(f"Top offset: {self.top_offset_height}, Page: {self.current_page}")

    def _write_s(self, content, with_icon: bool):
        self._write_content_block(content,
                                  with_icon=with_icon,
                                  font_size=12,
                                  text_color=colors.black,
                                  icon_path="asset/img/icon_s.png")

    def _write_q(self, content, with_icon: bool):
        """
        ⓠ
        """
        self._write_content_block(content,
                                  with_icon=with_icon,
                                  font_size=14,
                                  text_color=_PdfColorEm.TITLE_COLOR.value,
                                  icon_path="asset/img/icon_qa.png")

    def _write_a(self, content):
        """
        ⓐ
        """
        self._write_content_block(content,
                                  with_icon=False,
                                  font_size=12,
                                  text_color=colors.black,
                                  icon_path="")

