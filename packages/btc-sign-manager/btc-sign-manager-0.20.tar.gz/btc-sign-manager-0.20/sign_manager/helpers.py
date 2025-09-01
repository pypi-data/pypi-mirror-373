from typing import Type

from django.db.models import Model

from sign_manager.collections import SignedObjectType


class BaseSignatureObject:
    """
    Base signature object data class
    """

    def __init__(self,
                 object_for_sign: Type[Model],
                 signed_object_type: str,
                 object_hash: str = None,
                 object_serialized: str = 'empty',  # empty string for files
                 is_detached: bool = True):  # constant property

        self.object_for_sign = object_for_sign
        self.object_hash = object_hash or object_for_sign.get_hash()
        self.object_serialized = object_serialized
        self.signed_object_type = signed_object_type
        self.is_detached = is_detached

    def to_dict(self) -> dict:
        return self.__dict__


class XMLSignatureObject(BaseSignatureObject):
    """
    Signature class-wrapper for xml signing
    """

    def __init__(self, object_for_sign: Type[Model], object_hash: str = None):
        super().__init__(object_for_sign, SignedObjectType.XML, object_hash)


class SimpleFileSignatureObject(BaseSignatureObject):
    """
    Signature class-wrapper for simple file signing
    """

    def __init__(self, object_for_sign: Type[Model], object_hash: str = None):
        super().__init__(object_for_sign, SignedObjectType.SIMPLE_FILE, object_hash)


class RawSignatureObject(BaseSignatureObject):
    """
    Signature class-wrapper for raw signing
    """

    def __init__(self, object_for_sign: Type[Model], object_hash: str = None):
        super().__init__(object_for_sign, SignedObjectType.RAW, object_hash)


class BigFileSignatureObject(BaseSignatureObject):
    """
    Signature class-wrapper for big file signing
    """

    def __init__(self, object_for_sign: Type[Model], object_hash: str = None):
        super().__init__(object_for_sign, SignedObjectType.BIG_FILE, object_hash)
