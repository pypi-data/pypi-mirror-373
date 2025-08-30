from enum import Enum
from allure import step, attach
from allure_commons.types import AttachmentType
import json
from jsonschema import ValidationError

class AllureTag(Enum):
    TMS = "allure.link.tms"
    ISSUE = "allure.issue"

    @staticmethod
    def get_value(tag):
        return tag.split(":")[-1]

def get_tms_key(tags) -> str:
    for tag in tags:
        if AllureTag.TMS.value in tag:
            return AllureTag.get_value(tag)

def get_issue_links(tags) -> list[str]:
    return [AllureTag.get_value(tag) for tag in tags if AllureTag.ISSUE.value in tag]