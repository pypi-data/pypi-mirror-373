from typing import Type, Any

from django.core import serializers
from django.core.cache import cache
from django.db.models import Model

from sign_manager.utils import get_class_from_settings


def get_cache_manager_class() -> Type['CacheManager']:
    """
    Returns current cache manager class from the project settings or original "CacheManager"
    """

    error_message = 'Не найден указанный в "settings" класс менеджера кеширования объектов подписания. ' \
                    'Используется стандартный - "CacheManager"'
    return get_class_from_settings('SIGN_MANAGER_CACHE_MANAGER_CLASS', error_message, CacheManager)


def get_data_provider_class() -> Any:
    """
    Returns current data provider class from the project settings or original "DataProvider"
    """

    error_message = 'Не найден указанный в "settings" класс для проверки целостности данных. ' \
                    'Используется стандартный - "DataProvider"'
    return get_class_from_settings('SIGN_MANAGER_DATA_PROVIDER_CLASS', error_message, DataProvider)


class CacheManager:
    """
    A manager for data storing and recover, constructing queues
    """

    cache_key: str = 'for_sign'

    def __init__(self, request_key: str = None, cache_timeout: int = 300):
        self.request_key = request_key or self.cache_key
        self.cache_timeout = cache_timeout

    def cache_object(self, object_for_sign: Type[Model], object_hash: str = None) -> None:
        data = {
            object_hash or object_for_sign.get_hash(): object_for_sign.serialize_for_cache()
        }
        cache_data = self.get_data() or {}
        cache_data.update(data)
        cache.set(self.request_key, cache_data, timeout=self.cache_timeout)

    def get_queue(self) -> list:
        cached_data = self.get_data()

        queue = []
        for object_hash, entry in cached_data.items():
            queue += self.get_queue_stages_for_object(object_hash, entry)

        return queue

    def get_data(self) -> dict:
        return cache.get(self.request_key)

    @staticmethod
    def deserialize_object(entry_from_cache: str) -> tuple:
        deserialized_object, proxy_object = None, None
        for item in serializers.deserialize('json', entry_from_cache, ignorenonexistent=True):
            deserialized_object, proxy_object = item, item.object
            break
        return deserialized_object, proxy_object

    def get_queue_stages_for_object(self, hash_value: str, entry_from_cache: str) -> list:
        _, proxy_object = self.deserialize_object(entry_from_cache)
        stages_number = proxy_object.get_stages_number()
        stages = []
        try:
            name = str(proxy_object)
        except Exception:
            name = 'Подпись объекта'

        for stage_number in range(stages_number):
            stage_data = dict()
            stage_data['object_hash'] = hash_value
            stage_data['request_key'] = self.request_key
            stage_data['stage'] = stage_number + 1
            stage_data['stages_num'] = stages_number
            stage_data['name'] = name

            stages.append(stage_data)

        return stages

    def get_data_to_sign(self, object_hash: str, stage: int, stages_num: int, algorithm=None) -> dict:
        cached_data = self.get_data()
        entry_from_cache = cached_data.get(object_hash)
        _, proxy_object = self.deserialize_object(entry_from_cache)

        stage_data = dict()
        data_to_sign, need_hash = proxy_object.get_data_chunk(stage, stages_num, algorithm)
        stage_data['data_to_sign'] = data_to_sign
        stage_data['need_hash'] = need_hash

        stage_data['object_hash'] = object_hash
        stage_data['request_key'] = self.request_key
        stage_data['stage'] = stage
        stage_data['stages_num'] = stages_num

        try:
            stage_data['name'] = str(proxy_object)
        except Exception:
            stage_data['name'] = 'Подпись объекта'

        return stage_data


class DataProvider:
    """
    Provides necessary data for create signature object
    """

    @staticmethod
    def object_signed_data_provider(raw_signed_data: dict) -> dict:
        """
        Function for receiving signature data and ensuring its integrity
        """

        data = dict()
        data['object_serialized'] = raw_signed_data.get('object_serialized')
        data['signature_string'] = raw_signed_data.get('signature_string')
        data['signed_object_type'] = raw_signed_data.get('signed_object_type')
        data['is_detached'] = raw_signed_data.get('is_detached')
        return data

    @staticmethod
    def object_sign_cert_data_provider(raw_cert_data: dict) -> dict:
        """
        Function for obtaining certificate data and ensuring its integrity
        """

        data = dict()
        data['cert_serial_number'] = raw_cert_data.get('cert_serial_number')
        data['cert_version'] = raw_cert_data.get('cert_version')
        data['cert_key_algorithm'] = raw_cert_data.get('cert_key_algorithm')
        data['cert_key_algorithm_oid'] = raw_cert_data.get('cert_key_algorithm_oid')
        data['cert_subject_name'] = raw_cert_data.get('cert_subject_name')
        data['cert_issuer_name'] = raw_cert_data.get('cert_issuer_name')
        data['cert_valid_from_date'] = raw_cert_data.get('cert_valid_from_date')
        data['cert_valid_to_date'] = raw_cert_data.get('cert_valid_to_date')
        return data
