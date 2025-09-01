from django.contrib import admin


class SignManagerSignatureModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'sign_owner_admin', 'cert_valid_from_date_admin', 'cert_valid_to_date_admin')
    exclude = ('signature', 'content_type', 'object_id', 'object_serialized', 'is_detached', 'signed_object_type',
               'author')
    readonly_fields = ('signed_object_type_admin', 'is_detached_admin', 'cert_key_algorithm', 'cert_key_algorithm_oid',
                       'cert_serial_number', 'cert_subject_name', 'cert_issuer_name', 'cert_valid_from_date',
                       'cert_valid_to_date')
    list_per_page = 10
    empty = 'Не указано'

    def signed_object_type_admin(self, obj):
        return obj.signed_object_type.upper()

    signed_object_type_admin.short_description = 'Формат'

    def sign_owner_admin(self, obj):
        info_parts = [part for part in (obj.owner_fio, obj.owner_org, obj.owner_org_inn) if part]
        return ', '.join(info_parts) or self.empty

    sign_owner_admin.short_description = 'Владелец'

    def is_detached_admin(self, obj):
        return 'Оборачивающая' if obj.is_detached else 'Вложенная'

    is_detached_admin.short_description = 'Тип подписи'

    def cert_valid_from_date_admin(self, obj):
        return obj.cert_valid_from_date or self.empty

    cert_valid_from_date_admin.short_description = 'Действителен от'

    def cert_valid_to_date_admin(self, obj):
        return obj.cert_valid_to_date or self.empty

    cert_valid_to_date_admin.short_description = 'Действителен до'

    def cert_serial_number_admin(self, obj):
        return obj.cert_serial_number or self.empty

    cert_serial_number_admin.short_description = 'Серийный номер сертификата'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
