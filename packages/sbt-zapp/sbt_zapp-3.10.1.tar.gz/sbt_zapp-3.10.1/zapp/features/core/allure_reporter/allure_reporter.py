from allure import step, attach
from allure_commons.types import AttachmentType
import json


class AllureApiReporter:
    @staticmethod
    @step("Отправка API запроса")
    def log_request(request_method, url, params=None, headers=None):
        attach(
            name="Request Details",
            body=f"Method: {request_method}\nURL: {url}",
            attachment_type=AttachmentType.TEXT
        )
        if headers:
            attach(
                name="Request Headers",
                body=json.dumps(headers, indent=2),
                attachment_type=AttachmentType.JSON
            )
        if params:
            attach(
                name="Request Parameters",
                body=json.dumps(params, indent=2),
                attachment_type=AttachmentType.JSON
            )

    @staticmethod
    @step("Проверка ответа API")
    def log_response(response):
        attach(
            name="Response Status",
            body=f"Status Code: {response.status_code}",
            attachment_type=AttachmentType.TEXT
        )
        try:
            attach(
                name="Response Body",
                body=json.dumps(response.json(), indent=2),
                attachment_type=AttachmentType.JSON
            )
        except json.JSONDecodeError:
            attach(
                name="Response Body",
                body=response.text,
                attachment_type=AttachmentType.TEXT
            )

    @staticmethod
    @step("Валидация JSON схемы")
    def log_schema_validation(schema_file, is_success=True):
        status = "Успешно" if is_success else "Неудачно"
        attach(
            name="Schema Validation",
            body=f"Валидация по схеме {schema_file}: {status}",
            attachment_type=AttachmentType.TEXT
        )


