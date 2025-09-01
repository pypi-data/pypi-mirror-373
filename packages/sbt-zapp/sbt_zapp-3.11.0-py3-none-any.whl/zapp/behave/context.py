import six
import logging
from allure import step as allure_step
from behave.runner import Context

log = logging.getLogger(__name__)


class ZappContext(Context):
    def __init__(self, runner):
        super().__init__(runner)

    def execute_steps(self, steps_text):
        assert isinstance(steps_text, six.text_type), "Steps must be unicode."
        if not self.feature:
            raise ValueError("execute_steps() called outside of feature")

        # -- PREPARE: Save original context data for current step.
        # Needed if step definition that called this method uses .table/.text
        original_table = getattr(self, "table", None)
        original_text = getattr(self, "text", None)

        self.feature.parser.variant = "steps"
        steps = self.feature.parser.parse_steps(steps_text)
        with self._use_with_behave_mode():
            for step in steps:
                step_line = "%s %s" % (step.keyword, step.name)
                with allure_step(step_line):
                    passed = step.run(self._runner, quiet=True, capture=False)
                    if not passed:
                        log.exception(step.exception)
                        raise step.exception

            # -- FINALLY: Restore original context data for current step.
            self.table = original_table
            self.text = original_text
        return True

def override_context_execute_steps_method():
    Context.execute_steps = ZappContext.execute_steps