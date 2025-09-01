import logging
import shutil
import sys
import tempfile
from datetime import datetime, timedelta

from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry

from zapp.driver.strategies import browser_lifecycle
from zapp.features.core.settings import (
    STAND,
    RETRY_AFTER_FAIL,
    MAX_ATTEMPTS,
)
from zapp.driver import (
    REMOTE_EXECUTOR,
    SELENOID_VIDEO_ENABLED,
)
from zapp.features.core.tms.zephyr import ZEPHYR_USE
from zapp.features.core.tms.zephyr.zephyr import ZephyrSync
from zapp.features.core.utils import raise_if_not_valid_url, variables

from zapp.features.core.tms.test_culture.reporter import test_culture_reporter

log = logging.getLogger("environment")


def before_all(context):
    log.info(
        f"Версия Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    try:
        context.sync = ZEPHYR_USE
        if context.sync:
            ZephyrSync.before_all(context, None)
    except KeyError:
        context.sync = False
    finally:
        log.info(
            f'Синхронизация с Zephyr: {"включена" if context.sync is True else "отключена"}'
        )
        
    context.host = variables["context_host"] = raise_if_not_valid_url(STAND)
    context.tempdir = tempfile.mkdtemp()

    context.add_cleanup(lambda ctx: shutil.rmtree(ctx.tempdir), context)

    browser_lifecycle.before_all(context)


def before_feature(context, feature):
    browser_lifecycle.before_feature(context)

    if RETRY_AFTER_FAIL is True:
        for scenario in feature.scenarios:
            if scenario.effective_tags:
                patch_scenario_with_autoretry(scenario, max_attempts=MAX_ATTEMPTS)


def before_scenario(context, scenario):
    test_culture_reporter.before_scenario(context, scenario)

    log.info(f'Выполнение сценария "{scenario.name}" начато: {datetime.now()}')

    if context.sync:
        ZephyrSync.before_scenario(context, scenario)

    browser_lifecycle.before_scenario(context)


def before_step(context, step):
    context.current_step = dict(name=step.name, filename=step.filename, line=step.line)
    if context.sync:
        ZephyrSync.before_step(context, step)


def after_step(context, step):
    if context.sync:
        ZephyrSync.after_step(context, step)

    if step.exception:
        exception_type = type(step.exception).__name__
        log.debug(f"EXCEPTION_TYPE: {exception_type}")

        if REMOTE_EXECUTOR and SELENOID_VIDEO_ENABLED:
            log.warning(
                f"Примерное время ошибки на видео: {timedelta(seconds=round(context.feature.duration))}"
            )


def after_scenario(context, scenario):
    log.info(f'Выполнение сценария "{scenario.name}" закончено: {datetime.now()}')
    if context.sync:
        ZephyrSync.after_scenario(context, scenario)

    if scenario.status.has_failed():
        browser_lifecycle.on_fail(context)

    browser_lifecycle.after_scenario(context)


def after_feature(context, _):
    browser_lifecycle.after_feature(context)


def after_all(context):
    if context.sync:
        ZephyrSync.after_all(context)

    browser_lifecycle.after_all(context)
