from typing import Optional
from behave.model import Table, Step, Scenario, ScenarioOutline, Background
from behave.runner import Context

from test_culture_client.models.test_case.data import (
    TestCaseDataRequest,
    TestCaseDataEntry,
    TestCaseDataValue,
    TestCaseDataId,
)
from test_culture_client.models.test_case.entry import (
    TestCaseCreateRequest,
    TestCaseUpdateRequest,
    TestCaseAttributes,
    TestCaseSteps,
    TestCaseStepItem,
    FormattedText,
)

from test_culture_client.models.test_case.formatted import (
    wrap_table_header,
    wrap_table_row,
    wrap_paragraph,
    wrap_table_cell,
    wrap_table,
    build_formatted_text,
)

from .utils import get_scenario, get_scenario_tag_attributes, get_column_widths


class StepContext:
    keyword: str
    name: str
    text: str
    table: Table

    def __init__(self, keyword: str, name: str, text: str = None, table: str = None):
        self.keyword = keyword
        self.name = name
        self.text = text
        self.table = table

    def __str__(self):
        return f"{self.keyword} {self.name}{self.text if self.text else ''}{str(self.table) if self.table else ''}"

    @property
    def formatted_content(self) -> list[dict]:
        content = [wrap_paragraph(f"{self.keyword} {self.name}")]
        if self.text:
            content.append(wrap_paragraph(self.text))
        if self.table:
            content.append(self._table_to_content(self.table))
        return content

    def _headings_to_row(self, headings) -> dict:
        cells = []
        for heading in headings:
            cells.append(wrap_table_header([wrap_paragraph(heading)]))
        return wrap_table_row(cells)

    def _values_to_row(self, values) -> dict:
        cells = []
        for value in values:
            cells.append(wrap_table_cell([wrap_paragraph(value)]))
        return wrap_table_row(cells)

    def _table_to_content(self, table: Table) -> dict:
        header_row = self._headings_to_row(table.headings)
        rows = [self._values_to_row(row.cells) for row in table.rows]
        return wrap_table(
            rows=[header_row] + rows, column_widths=get_column_widths(table)
        )

    @staticmethod
    def parse(step: Step) -> "StepContext":
        return StepContext(step.keyword, step.name, step.text, step.table)


class ComplexStepContext:
    action: list[StepContext]
    result: list[StepContext]

    def __init__(self, action: list[StepContext], result: list[StepContext]):
        self.action = action
        self.result = result

    def add_when(self, step: StepContext) -> None:
        self.action.append(step)

    def add_then(self, step: StepContext) -> None:
        self.result.append(step)

    @property
    def test_data(self) -> FormattedText:
        return FormattedText(plainText=None, formattedText=None)

    @property
    def test_description(self) -> FormattedText:
        return self._build_formatted_text(self.action)

    @property
    def test_result(self) -> FormattedText:
        return self._build_formatted_text(self.result)

    def _build_formatted_text(self, steps: list[StepContext]) -> str:
        formatted_content = []
        for step in steps:
            formatted_content.extend(step.formatted_content)
        plain_content = "\n".join([str(step) for step in steps])
        return FormattedText(
            plainText=plain_content,
            formattedText=build_formatted_text(formatted_content),
        )


class BackgroundContext:
    steps: list[StepContext]

    def __init__(self, steps: list):
        self.steps = steps

    def __str__(self):
        content = []
        for step in self.steps:
            content.extend(step.formatted_content)
        return build_formatted_text(content)

    @staticmethod
    def parse(background: Background) -> "BackgroundContext":
        return BackgroundContext([StepContext.parse(step) for step in background.steps])


class ScenarioContext:
    summary: str
    description: str
    attributes = dict[str, str]
    steps: list[StepContext]

    def __init__(
        self, summary: str, description: str, steps: list[StepContext], **kwargs
    ):
        self.summary = summary
        self.description = description
        self.steps = steps
        self.attributes = kwargs

    @property
    def formatted_description(self) -> str | None:
        if self.description:
            return build_formatted_text(wrap_paragraph(self.description))

    def to_complex_steps(self) -> list[ComplexStepContext]:
        complex_steps: list[ComplexStepContext] = []
        last_was_when = True
        for step in self.steps:
            if step.keyword in ("When", "Given"):
                if last_was_when and complex_steps:
                    complex_steps[-1].add_when(step)
                else:
                    complex_steps.append(ComplexStepContext(action=[step], result=[]))
                last_was_when = True
            elif step.keyword == "Then":
                if complex_steps:
                    complex_steps[-1].add_then(step)
                else:
                    complex_steps.append(ComplexStepContext(action=[], result=[step]))
                last_was_when = False
            elif step.keyword == "And":
                if last_was_when:
                    complex_steps[-1].add_when(step)
                else:
                    complex_steps[-1].add_then(step)
        return complex_steps

    @staticmethod
    def parse(scenario: Scenario | ScenarioOutline) -> "ScenarioContext":
        # Заполняем здесь атрибуты, которые могут быть получены из описания сценария
        return ScenarioContext(
            summary=scenario.name,
            description="\n".join(scenario.description),
            steps=[StepContext.parse(step) for step in scenario.steps],
            pmi="not",
            automated="yes",
            **get_scenario_tag_attributes(scenario.effective_tags),
        )


class TestDataRowContext:
    name: str
    values: list[str]

    def __init__(self, name: str, values: list[str]):
        self.name = name
        self.values = values


class TestDataContext:
    rows: list[TestDataRowContext]

    def __init__(self, rows: list[TestDataRowContext]):
        self.rows = rows

    def to_request(self) -> TestCaseDataRequest:
        return TestCaseDataRequest(
            data=[
                TestCaseDataEntry(
                    id=TestCaseDataId(parameterId=None),
                    order=order + 1,
                    name=item.name,
                    value=[
                        TestCaseDataValue(order=value_order + 1, value=value)
                        for value_order, value in enumerate(item.values)
                    ],
                )
                for order, item in enumerate(self.rows)
            ]
        )

    @staticmethod
    def parse(tables: list[Table]) -> "TestDataContext":
        test_data = {key: [] for key in tables[0].headings}

        for table in tables:
            for row in table.rows:
                for key, value in row.items():
                    test_data[key].append(value)

        rows_context = [
            TestDataRowContext(name, values) for name, values in test_data.items()
        ]
        return TestDataContext(rows_context)


class TestCaseContext:
    background: Optional[BackgroundContext]
    scenario: ScenarioContext
    test_data: Optional[TestDataContext]

    def __init__(
        self,
        background: BackgroundContext,
        scenario: ScenarioContext,
        test_data: TestDataContext,
    ):
        self.background = background
        self.scenario = scenario
        self.test_data = test_data

    def _get_test_steps(self) -> TestCaseSteps:
        return TestCaseSteps(
            testStepList=[
                TestCaseStepItem(
                    stepNumber=order + 1,
                    stepDescription=step.test_description,
                    stepData=step.test_data,
                    stepResult=step.test_result,
                    deleted=False,
                    stepFiles=[],
                )
                for order, step in enumerate(self.scenario.to_complex_steps())
            ]
        )

    def _get_attributes(self) -> TestCaseAttributes:
        return TestCaseAttributes(
            **self.scenario.attributes,
            folder="",
            precondition=str(self.background) if self.background else None,
            test_step=self._get_test_steps(),
        )

    def to_create_request(self) -> TestCaseCreateRequest:
        return TestCaseCreateRequest(
            summary=self.scenario.summary,
            space="",
            description=self.scenario.description,
            attributes=self._get_attributes(),
        )

    def to_update_request(self) -> TestCaseUpdateRequest:
        return TestCaseUpdateRequest(
            summary=self.scenario.summary,
            description=self.scenario.description,
            attributes=self._get_attributes(),
        )

    @staticmethod
    def parse(context: Context) -> "TestCaseContext":
        scenario = get_scenario(context)
        background_context = (
            BackgroundContext.parse(scenario.background)
            if scenario.background
            else None
        )
        scenario_context = ScenarioContext.parse(scenario)
        test_data_context = (
            TestDataContext.parse([example.table for example in scenario.examples])
            if isinstance(scenario, ScenarioOutline)
            else TestDataContext([])
        )

        return TestCaseContext(background_context, scenario_context, test_data_context)
