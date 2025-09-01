import os
import textwrap
from collections import OrderedDict
from tempfile import NamedTemporaryFile
from typing import Collection, Tuple

import fitz
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.db.models.fields.files import FieldFile
from django.utils.timezone import now as tz_now
from typing import BinaryIO

from sign_manager.utils import format_date, parse_certificate, set_file_name_suffix_in_path, replace_file_from_path


class TextLine:
    """
    Text string class for drawings
    """

    def __init__(self,
                 draw_object: ImageDraw.ImageDraw,
                 text, necessary_width: int,
                 font: ImageFont.ImageFont,
                 font_color_rgb: tuple = (0, 0, 0),
                 sub_lines_vertical_indent: int = 2,
                 line_vertical_indent: int = 0):

        self.draw_object = draw_object
        self.font = font
        self.text = text
        self.font_color_rgb = font_color_rgb
        self.necessary_width = necessary_width
        self.sub_lines_vertical_indent = sub_lines_vertical_indent
        self.line_indent = line_vertical_indent

        left, top, right, bottom = draw_object.textbbox((0, 0), text=self.text, font=self.font)
        self.text_width, self.text_height = right - left, bottom - top
        self.full_text_height = self.text_height + self.line_indent
        self.symbol_width = self.text_width / len(self.text)
        self.lines = textwrap.wrap(self.text, width=int(self.necessary_width // self.symbol_width))
        self.line = self.lines[:1][0]
        self.sub_lines = self.lines[1:]

    def draw(self, cursor_y_pos: int, cursor_x_pos: int, inner_vertical_indent: int) -> int:
        """
        Метод для рисования текста
        :param cursor_y_pos: int, начальная y-координата курсора-рисования
        :param cursor_x_pos: int, x-координата курсора-рисования
        :param inner_vertical_indent: int, рассчитанный отступ для строк текста
        :return: int, отступ для следующей строки 'TextLine'
        """
        indent = 0
        self.draw_object.text((cursor_x_pos, cursor_y_pos), self.line, fill=self.font_color_rgb, font=self.font)
        indent += self.full_text_height
        if self.sub_lines:
            indent += self.sub_lines_vertical_indent
        for sub_line in self.sub_lines:
            self.draw_object.text((cursor_x_pos, indent + cursor_y_pos), sub_line, fill=self.font_color_rgb,
                                  font=self.font)
            indent += self.sub_lines_vertical_indent + self.full_text_height
        indent += inner_vertical_indent
        return indent


class SignetCreator:
    """

    """

    @classmethod
    def draw_text_block(cls,
                        draw_object: ImageDraw.ImageDraw,
                        title: str,
                        data_dict: dict,
                        block_height: int,
                        block_width: int,
                        y_coord: int = 10, x_coord: int = 15, font_size: int = 20,
                        font_path: str = '/assets/fonts/TimesNewRoman/TimesNewRomanBold.ttf',
                        font_color_rgb: tuple = (0, 0, 0)) -> None:
        """
        Функция для генерации временного файла изображения с данными 'data_dict'
        :param draw_object: Pillow-объект изображения
        :param block_height: доступная высота исходного изображения
        :param block_width: доступная ширина исходного изображения
        :param data_dict: словарь со строками для вывода
        :param title: заголовок блока
        :param y_coord: y-координата для текста
        :param x_coord: x-координата для текста
        :param font_size: размер шрифта
        :param font_path: путь к файлу шрифта
        :param font_color_rgb: цвет шрифта в формате 'rgb'
        :return: None
        """

        info_dict = OrderedDict(data_dict)
        text_lines = []
        text_lines_full_height = 0
        font = ImageFont.truetype(font_path, font_size)

        text_lines.append(TextLine(draw_object, title, block_width, font, font_color_rgb, line_vertical_indent=5))
        for info_string in info_dict.values():
            text_line = TextLine(draw_object, info_string, block_width, font, font_color_rgb)
            text_lines_full_height += text_line.full_text_height
            text_lines.append(text_line)

        text_lines_len = len(text_lines)
        lines_inner_vertical_indent = int((block_height - text_lines_full_height) / text_lines_len)

        # Подпись изображения данными
        cursor_pos = y_coord
        for line_object in text_lines:
            cursor_pos += line_object.draw(cursor_pos, x_coord, lines_inner_vertical_indent)

    @classmethod
    def add_signet_to_pdf(cls,
                          pdf_filepath: str,
                          result_pdf_path: str,
                          sign_cert_data: dict,
                          pages_numbers: Collection = None) -> BinaryIO:
        """
        Функция для добавления изображения с данными сертификата в pdf-файл
        :param pdf_filepath: путь до pdf-файла
        :param result_pdf_path: путь сохранения pdf-файла с изображением
        :param sign_cert_data: данные сертификата
        :param pages_numbers: перечисление страниц для вставки изображения
        :return: BinaryIO
        """
        doc = fitz.open(pdf_filepath)
        if doc.is_pdf:
            pages = [doc[page_number] for page_number in pages_numbers] if pages_numbers else doc
            for page in pages:
                pixmap = cls.make_signet_pixmap(page, sign_cert_data)
                rect = cls.make_rect(page, pixmap)
                page.insert_image(rect, pixmap=pixmap, overlay=True)
            doc.save(result_pdf_path)
        return doc

    @classmethod
    def draw_pdf_signet(cls,
                        sign_cert_data: dict,
                        image_height: int,
                        image_width: int,
                        border_width: int) -> NamedTemporaryFile:
        """
        Функция для рисования данных в документе
        :param sign_cert_data: данные сертификата
        :param image_height: высота изображения
        :param image_width: ширина изображения
        :param border_width: размер границы
        :return: NamedTemporaryFile
        """
        owner_fio = parse_certificate(sign_cert_data.get('cert_subject_name'), 'CN=')
        owner_org = parse_certificate(sign_cert_data.get('cert_subject_name'), 'O=')
        owner_org_inn = parse_certificate(sign_cert_data.get('cert_subject_name'), 'INN=')
        cert_serial_number = sign_cert_data.get('cert_serial_number')
        cert_valid_from_date = sign_cert_data.get('cert_valid_from_date')
        cert_valid_to_date = sign_cert_data.get('cert_valid_to_date')

        data = OrderedDict()
        data['cert_info_first_block'] = dict(
            cert_owner_fio=f'Владелец: {owner_fio}',
            cert_owner_org=f'Организация: {owner_org} {owner_org_inn}',
            created=f'Подписано: {format_date(tz_now().date())}',
        )
        data['cert_info_second_block'] = dict(
            cert_serial_number=f'Серийный номер: {cert_serial_number}',
            cert_validity=f'Срок действия: {format_date(cert_valid_from_date)} - {format_date(cert_valid_to_date)}',
        )

        # Ограничение максимальной и минимальной высоты изображения (110 <= image_height <= 190).
        image_height = max(110, min(image_height, 190))

        # Расчет размера шрифта:
        font_size = int((image_height - 10) / 10)

        # Ограничение максимальной и минимальной высоты изображения: (350 <= image_width <= 700).
        image_width = max(350, min(image_width, 700))

        font_path = os.path.join(settings.ROOT_DIR, 'assets/fonts/TimesNewRoman/TimesNewRomanBold.ttf')
        image = Image.new('RGB', (image_width, image_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle(((0, 0), (image_width, image_height)), fill='white', outline=(0, 0, 0), width=border_width)

        cls.draw_text_block(draw,
                            'Данные электронной подписи',
                            data['cert_info_first_block'],
                            block_height=int(image_height * 40 / 100),  # 40% от высоты изображения
                            block_width=image_width,
                            y_coord=int(image_height * 2.5 / 100),  # 2.5% от высоты изображения
                            x_coord=int(image_width * 1.5 / 100),  # 1.5% от длины изображения
                            font_size=font_size,
                            font_path=font_path)

        cls.draw_text_block(draw,
                            'Данные сертификата',
                            data['cert_info_second_block'],
                            block_height=int(image_height * 20 / 100),  # 20% от высоты изображения
                            block_width=image_width,
                            y_coord=int(image_height * 62.5 / 100),  # 62.5% от высоты изображения
                            x_coord=int(image_width * 1.5 / 100),  # 1.5% от длины изображения
                            font_size=font_size,
                            font_path=font_path)

        temp_image_file = image._dump()
        return temp_image_file

    @classmethod
    def attach_signet_to_pdf(cls, file_field: FieldFile, sign_cert_data: dict) -> str:
        """
        Метод для вставки изображения с данными сертификата в pdf - документ
        :param file_field: FileField, объект поля модели
        :param sign_cert_data: dict, словарь с данными сертификата
        :return: str, путь к файлу со вставленным изображением
        """
        file_path, new_file_path = set_file_name_suffix_in_path(file_field.name, '_signed')
        cls.add_signet_to_pdf(file_path, new_file_path, sign_cert_data)
        replace_file_from_path(file_field, new_file_path)
        return new_file_path

    @classmethod
    def get_image_params(cls, page: fitz.Page) -> Tuple[int, int]:
        """
        Возвращает параметры изображения: ширину и высоту.
        Ширина - 55% от ширины страницы. Высота - 12% от высоты страницы.
        :param page: Page, страница документа
        :return: tuple, ширина и высота
        """
        return int(page.mediabox_size.x * 55 / 100), int(page.mediabox_size.y * 12 / 100)

    @classmethod
    def make_signet_pixmap(cls, page: fitz.Page, sign_cert_data) -> fitz.Pixmap:
        """
        Создает и возвращает прямоугольник с изображением c данными сертификата.
        :param page: Page, страница документа
        :param sign_cert_data: dict, словарь с данными сертификата
        :return: Pixmap, прямоугольник с изображением печатки
        """
        image_width, image_height = cls.get_image_params(page)

        temp_image_file = cls.draw_pdf_signet(
            sign_cert_data,
            image_height=image_height,
            image_width=image_width,
            border_width=2,
        )
        return fitz.Pixmap(temp_image_file)

    @classmethod
    def make_rect(cls, page: fitz.Page, pixmap: fitz.Pixmap) -> fitz.Rect:
        """
        Создает и возвращает прямоугольник по координатам, где будет располагаться изобрадение. (Правый нижний угол)
        Координаты рассчитываются от правой нижней точки страницы.
        :param page: Page, страница документа
        :param pixmap: Pixmap, прямоугольник с изображением печатки
        :return: Rect, прямоугольник, где будет располагаться изобрадение
        """
        image_coords = (
            page.mediabox_size.x - (pixmap.w + 3),
            page.mediabox_size.y - (pixmap.h + 3),
            page.mediabox_size.x - 3,
            page.mediabox_size.y - 3,
        )  # (x0, y0, x1, y1)
        return fitz.Rect(image_coords)
