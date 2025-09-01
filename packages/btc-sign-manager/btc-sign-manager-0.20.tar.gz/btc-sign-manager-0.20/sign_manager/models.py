import base64
import math
import os
from typing import Union, Type, Tuple

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.text import slugify
from django.utils.timezone import now as tz_now

from sign_manager.collections import SignedObjectType
from sign_manager.utils import format_date, get_class_from_settings, get_str_hash
from sign_manager.utils import parse_certificate


def get_sign_manager_abstract_model_class() -> Type['AbstractSignManager']:
    """
    Returns current sign manager abstract model class from the project settings or original "AbstractSignManager"
    """

    error_message = 'Не найден укаазанный в "settings" абстрактный класс модели менеджера подписей. ' \
                    'Используется стандартный - "AbstractSignManager"'
    return get_class_from_settings('SIGN_MANAGER_ABSTRACT_MODEL_CLASS', error_message, AbstractSignManager)


def get_signature_file_path(instance, filename):
    default_save_path = os.path.join(instance._meta.app_label, 'sig')
    signature_save_path = getattr(settings, 'SIGN_MANAGER_SIGNATURE_SAVE_FILE_PATH', None) or default_save_path
    return os.path.join(signature_save_path, filename)


class SignManagerSignature(models.Model):
    """
    Object signature information model
    Tags for string parsing "cert_subject_name", "cert_issuer_name":
    CN= ФИО, T= Должность, O= Организация, E= E-mail, S= Город, L= Область, C= Страна, INN= ИНН, OGRN= ОГРН,
    STREET= Улица, UnstructuredName= Другое наименование
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(verbose_name='Дата и время создания', default=tz_now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Автор', related_name='sign_manager_signatures',
                               on_delete=models.SET_NULL, null=True)
    is_detached = models.BooleanField(verbose_name='Подпись открепленная (оборачивающая)')
    object_serialized = models.TextField(verbose_name='Сериализованный объект')
    signature = models.FileField(verbose_name='Подпись', upload_to=get_signature_file_path)
    signed_object_type = models.CharField(verbose_name='Тип подписанного объекта', max_length=20,
                                          choices=SignedObjectType.CHOICES)
    cert_version = models.CharField(verbose_name='Версия сертификата', max_length=200, null=True)
    cert_key_algorithm = models.CharField(verbose_name='Алгоритм ключа сертификата', max_length=200, null=True)
    cert_key_algorithm_oid = models.CharField(
        verbose_name='Идентификатор алгоритма ключа сертификата', max_length=200, null=True
    )
    cert_serial_number = models.CharField(verbose_name='Серийный номер сертификата', max_length=200, null=True)
    cert_subject_name = models.TextField(verbose_name='Информация о сертификате', null=True)
    cert_issuer_name = models.TextField(verbose_name='Информация об издателе сертификата', null=True)
    cert_valid_from_date = models.DateTimeField(verbose_name='Сертификат действителен от', null=True)
    cert_valid_to_date = models.DateTimeField(verbose_name='Сертификат действителен до', null=True)

    class Meta:
        verbose_name = 'Подпись объекта'
        verbose_name_plural = 'Подписи объектов'
        ordering = ('-created',)

    def __str__(self):
        return f'{self.content_object}, {format_date(self.created, "d.m.Y H:i")}'

    def get_object_serialized_encoded(self) -> bytes:
        # encode data here, it needed, for example,

        encoded_data = ''
        if self.signed_object_type == SignedObjectType.XML:
            encoded_data = self.object_serialized.encode('utf-8')
        elif self.signed_object_type == SignedObjectType.SIMPLE_FILE:
            encoded_data = base64.b64decode(self.object_serialized)
        # ...
        return encoded_data

    @property
    def owner_fio(self) -> str:
        return parse_certificate(self.cert_subject_name, 'CN=')

    @property
    def owner_org(self) -> str:
        return parse_certificate(self.cert_subject_name, 'O=')

    @property
    def owner_org_inn(self) -> str:
        return parse_certificate(self.cert_subject_name, 'INN=')

    @property
    def publisher(self) -> str:
        return parse_certificate(self.cert_issuer_name, 'CN=')

    @property
    def validity(self) -> str:
        return f'{format_date(self.cert_valid_from_date)} - {format_date(self.cert_valid_to_date)}'


class AbstractSignManager(models.Model):
    """
    An abstract model for save signs of model objects
    """

    SIGNATURE_FILE_EXTENSION: str = '.sig'
    SIGNATURE_FILE_NAME: str = 'Подпись_%s'
    FIELD_FOR_SIGNED_OBJECT_STRING: str = None
    ALLOW_MULTIPLY_SIGNS: bool = True

    BIG_FILE_CHUNK_SIZE: int = 8388608  # 8 Mb

    signature = GenericRelation(SignManagerSignature, related_query_name='sign_objects')

    class Meta:
        abstract = True

    def create_sign(self, signed_data: dict, sign_cert_data: dict, validate: bool = False) -> tuple:
        object_old_state_serialized = signed_data.get('object_serialized')
        signed_data_is_valid = True
        if validate:
            signed_data_is_valid = self.check_data_integrity(object_old_state_serialized)
        sign_object = None
        # if all checks passed - create signature file, attached to the model
        if signed_data_is_valid:
            signature_string = signed_data.pop('signature_string')
            sign_object = SignManagerSignature(**signed_data, **sign_cert_data)
            sign_object.content_type = ContentType.objects.get_for_model(self)
            sign_object.object_id = self.id
            decoded_data = self.decode_signed_data(signed_data['signed_object_type'], signature_string)
            sign_file_name = self.get_detached_signature_file_name()
            sign_object.signature.save(sign_file_name, ContentFile(decoded_data), save=False)
            # If the signature is not detached
            # Assigning the string "signed_object_string" to the model file field
            if not sign_object.is_detached \
                    and self.FIELD_FOR_SIGNED_OBJECT_STRING \
                    and hasattr(self, self.FIELD_FOR_SIGNED_OBJECT_STRING):
                file_field = getattr(self, self.FIELD_FOR_SIGNED_OBJECT_STRING)
                if isinstance(file_field, FieldFile):
                    filename = self.get_attached_signature_file_name(file_field.name)
                    file_field.save(filename, ContentFile(decoded_data), save=False)
            sign_object.save()
        return signed_data_is_valid, sign_object

    def get_detached_signature_file_name(self) -> str:
        title = slugify(str(self), allow_unicode=True)
        return (self.SIGNATURE_FILE_NAME + self.SIGNATURE_FILE_EXTENSION) % title

    def get_attached_signature_file_name(self, base_file_name: str) -> str:
        return os.path.basename(base_file_name) + self.SIGNATURE_FILE_EXTENSION

    def decode_signed_data(self, sign_format: str, signed_object_string: str) -> Union[bytes, str]:
        decoded_data = signed_object_string
        if sign_format == SignedObjectType.SIMPLE_FILE:
            # decode if needed
            # decoded_data = base64.b64decode(signed_object_string)
            pass
        return decoded_data

    def check_data_integrity(self, object_old_state_serialized: str) -> bool:
        # check serialized object string before and after sign
        old_state = object_old_state_serialized
        current_state = self.serialize_for_sign()
        # remove xml header
        xml_header = '<?xml version="1.0" encoding="utf-8"?>'
        xml_header_len = len(xml_header)
        # check length is identical
        check_integrity = old_state[xml_header_len:].split() == current_state[xml_header_len:].split()
        # check for multiply signs
        check_restriction = not (not self.ALLOW_MULTIPLY_SIGNS and self.signature.exists())

        return check_integrity and check_restriction

    def get_hash(self) -> str:
        # get the hash value of the current object
        hash_data_string = f'{self.__class__.__name__}-{self.id}'
        return str(get_str_hash(hash_data_string, digest_size=5))

    def serialize_for_sign(self, stage: int = None, stages_num: int = None, algorithm=None) -> Union[bytes, str]:
        return serializers.serialize('xml', (self,))

    def get_stages_number(self) -> int:
        return 1

    def get_stages_number_for_big_file(self, file: FieldFile) -> int:
        return math.ceil(file.size / self.BIG_FILE_CHUNK_SIZE)

    def get_data_chunk(self, stage: int, stages_num: int, algorithm=None) -> Tuple[str, bool]:
        """
        Возвращает данные для подписи и флаг, надо ли высчитать хэш по этим данным на фронте
        """
        return self.serialize_for_sign(stage, stages_num, algorithm=algorithm), False

    def get_data_chunk_for_simple_string(self, stage: int, stages_num: int) -> str:
        serialized_data = self.serialize_for_sign(stage, stages_num)
        total_len = len(serialized_data)
        base_chunk_len = int(total_len / stages_num) + 10
        return serialized_data[base_chunk_len * (stage - 1):base_chunk_len * (stage + 1)]

    def get_base64_chunk_for_big_file(self, file: FieldFile, stage: int,
                                      chunk_size: int) -> Union[str, bytes,bytearray]:
        file.seek((stage - 1) * chunk_size)
        return base64.b64encode(file.read(chunk_size)).decode('utf-8')

    def serialize_for_cache(self) -> Union[bytes, str]:
        return serializers.serialize('json', (self,))
