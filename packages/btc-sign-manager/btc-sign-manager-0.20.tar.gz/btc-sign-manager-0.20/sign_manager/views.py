import logging
import uuid
from typing import List, Type, Collection, Optional

from django.contrib import messages
from django.forms import BaseForm
from django.http import JsonResponse
from django.views import View

from sign_manager.forms import MultipleObjectsSignFormSet, MultipleObjectsSignCertificateForm
from sign_manager.helpers import BaseSignatureObject
from sign_manager.service import get_cache_manager_class, get_data_provider_class
from sign_manager.signet import SignetCreator

logger = logging.getLogger(__name__)


SIGN_STORE_SESSION_KEY = 'sign_store'


class SignManagerMixin:
    """
    Mixin for transform views to sign views
    """

    _serialization_flag: str = 'serialize_for_sign'
    _sign_complete_flag: str = 'sign_complete'
    _check_methods: list = ['POST']
    __objects_to_serialization: dict = {}

    is_ajax: bool = False
    sign_success_message: str = 'Данные успешно подписаны'
    sign_error_message: str = 'Подписание было прервано. Произошла ошибка сохранения'

    sign_success_url: str = None
    sign_error_url: str = None
    sign_formset_class = MultipleObjectsSignFormSet
    sign_certificate_form_class = MultipleObjectsSignCertificateForm

    __request_key: str = None
    data_is_valid: bool = True
    restore_from_cache: bool = False

    called_object: Optional[str] = None
    called_object_type: Optional[str] = None

    @property
    def request_key(self) -> str:
        # cached property for request_key
        if not self.__request_key:
            self.__request_key = uuid.uuid4().hex
        return self.__request_key

    def dispatch(self, request, *args, **kwargs):
        if any(self._serialization_flag in getattr(request, method, {}) for method in self._check_methods):
            self.prepare_objects()
            return JsonResponse(data=dict(request_key=self.request_key, queue=self._get_queue(),
                                          signet_queue=self.get_queue_for_signet()))
        elif self._sign_complete_flag in request.POST:
            # if "_sign_complete_flag" flag in request data - call "after_sign" method to finish signing
            self.data_is_valid = self._validate_and_save_signed_data()

        # throw the normal view response
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.data_is_valid:
            self.process_view()
            response_data = self.get_data_to_success_response()
        else:
            response_data = self.get_data_to_error_response()
        return JsonResponse(data={**response_data, **self.get_data_to_response()})

    def get_data_to_response(self) -> dict:
        return dict(called_object=self.get_called_object(), called_object_type=self.get_called_object_type())

    def get_called_object(self):
        return self.called_object

    def get_called_object_type(self):
        return self.called_object_type

    def get_data_to_success_response(self):
        return dict(redirect_url=self.get_sign_success_url(), message=self.sign_success_message)

    def get_data_to_error_response(self):
        return dict(redirect_url=self.get_sign_error_url(), message=self.sign_error_message)

    def process_view(self) -> None:
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self._get_sign_context_data())
        return context

    def _get_sign_context_data(self, **kwargs) -> dict:
        sign_formset_initial_data = [sign_object.to_dict() for sign_object in self.set_sign_initial_data()]
        context = dict(
            sign_formset=self.sign_formset_class(initial=sign_formset_initial_data),
            sign_certificate_form=self.sign_certificate_form_class(),
            sign_success_url=self.get_sign_success_url(),
            **kwargs
        )
        return context

    def get_sign_success_url(self) -> str:
        return self.sign_success_url

    def get_sign_error_url(self) -> str:
        return self.sign_error_url

    def set_sign_initial_data(self) -> List[BaseSignatureObject]:
        return []

    def _validate_and_save_signed_data(self) -> bool:
        signed_formset_data_is_valid, signed_data = self.get_signed_data()
        sign_cert_data_is_valid, sign_cert_data = self.get_sing_cert_data()
        is_valid = signed_formset_data_is_valid and sign_cert_data_is_valid
        if is_valid:
            if self.restore_from_cache:
                self.restore_objects_from_cache()
            is_valid &= self.after_sign(signed_data, sign_cert_data) or True
        if not self.is_ajax:
            if is_valid:
                messages.success(self.request, self.sign_success_message)
            else:
                messages.error(self.request, self.sign_error_message)
        return is_valid

    def get_signed_data(self) -> tuple:
        data_provider_class = get_data_provider_class()
        signed_data = dict()
        sign_formset = self.sign_formset_class(data=self.request.POST)
        is_valid = sign_formset.is_valid()
        if is_valid:
            for form in sign_formset:
                form_cleaned_data = form.cleaned_data.copy()
                object_hash = form_cleaned_data.pop(form.OBJECT_HASH_FIELD_NAME)
                signed_data[object_hash] = data_provider_class.object_signed_data_provider(form_cleaned_data)
        else:
            logger.debug(sign_formset.errors)
        return is_valid, signed_data

    def get_sing_cert_data(self) -> tuple:
        sign_cert_data = dict()
        sign_cert_form = self.sign_certificate_form_class(data=self.request.POST)
        is_valid = sign_cert_form.is_valid()
        if is_valid:
            data_provider_class = get_data_provider_class()
            sign_cert_data = data_provider_class.object_sign_cert_data_provider(sign_cert_form.cleaned_data)
        else:
            logger.debug(sign_cert_form.errors)
        return is_valid, sign_cert_data

    def _cache_objects(self) -> None:
        # put objects to cache for sign-serialization in future
        cache_manager_class = get_cache_manager_class()
        cache_manager = cache_manager_class(request_key=self.request_key)
        for object_hash, obj in self.__objects_to_serialization.items():
            cache_manager.cache_object(obj, object_hash)

    def _get_queue(self) -> list:
        cache_manager_class = get_cache_manager_class()
        cache_manager = cache_manager_class(request_key=self.request_key)
        return cache_manager.get_queue()

    def _get_objects_for_sign(self) -> dict:
        return {sign_object.object_hash: sign_object.object_for_sign for sign_object in self.set_sign_initial_data()}

    def prepare_objects(self) -> None:
        self.__objects_to_serialization = self._get_objects_for_sign()
        self._cache_objects()

    def after_sign(self, signed_data: dict, sign_cert_data: dict) -> bool:
        # auto save signs for all objects marked for sign (which in initial sign data)
        data_is_valid = True
        for obj_hash, obj in self._get_objects_for_sign().items():
            obj_sign_data = signed_data.get(obj_hash)
            is_valid, sign_object = obj.create_sign(obj_sign_data, sign_cert_data)
            data_is_valid &= is_valid
        return data_is_valid

    def restore_objects_from_cache(self) -> None:
        pass

    def get_queue_for_signet(self) -> list:
        # returns list of dicts: file id and file_type: {'stage': 1, id: '1', 'file_type': 'pdf'}
        return []


class SignManagerQueueView(View):
    """
    A view for sending the queue data to js script
    """

    def post(self, request, *args, **kwargs):
        request_key = request.POST.get('request_key')
        object_hash = request.POST.get('object_hash')
        stage = request.POST.get('stage')
        stages_num = request.POST.get('stages_num')
        algorithm = request.POST.get('algorithm')

        cache_manager_class = get_cache_manager_class()
        cache_manager = cache_manager_class(request_key=request_key)
        data_to_sign = cache_manager.get_data_to_sign(object_hash, int(stage), int(stages_num), algorithm)

        return JsonResponse(data=data_to_sign)


class AddSignetToFiles(View):
    """
    View for file signet adding
    """

    certificate_form_class: Type[BaseForm] = MultipleObjectsSignCertificateForm
    success_response_data: dict = {'result': 'success'}
    error_response_data: dict = {'result': 'error'}

    def post(self, request, *args, **kwargs):
        certificate_form = self.certificate_form_class(data=self.request.POST)
        is_valid = certificate_form.is_valid()
        if is_valid:
            self.add_signet(certificate_form)
            response = self.status_response(self.success_response_data)
        else:
            response = self.status_response(self.error_response_data)
        return response

    def add_signet(self, certificate_form: Type[BaseForm]) -> None:
        data_provider_class = get_data_provider_class()
        sign_cert_data = data_provider_class.object_sign_cert_data_provider(certificate_form.cleaned_data)
        for file in self.get_files():
            if self.request.POST.get('file_type') == 'pdf':
                SignetCreator.attach_signet_to_pdf(file.file, sign_cert_data)

    def status_response(self, data: dict):
        return JsonResponse(data=data)

    def get_files(self) -> Collection:
        return []
