from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Operator
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbtasks.models import Task


class TaskDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="in_charge", label="In Charge"),
                dp.Field(key="due_date", label="Due at"),
                dp.Field(key="description", label="Description"),
                dp.Field(key="tags", label="Tags"),
            ],
            formatting=[
                dp.Formatting(
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=Task.Status.UNSCHEDULED),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=Task.Status.STARTED),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=Task.Status.COMPLETED),
                        ),
                    ],
                    column="status",
                )
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            label=Task.Status.UNSCHEDULED.label,
                            icon=WBColor.BLUE_LIGHT.value,
                            value=Task.Status.UNSCHEDULED.value,
                        ),
                        dp.LegendItem(
                            label=Task.Status.STARTED.label,
                            icon=WBColor.YELLOW.value,
                            value=Task.Status.STARTED.value,
                        ),
                        dp.LegendItem(
                            label=Task.Status.COMPLETED.label,
                            icon=WBColor.GREEN_LIGHT.value,
                            value=Task.Status.COMPLETED.value,
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["status", "status", "status"],
                ["title", "title", "title"],
                ["creation_date", "due_date", "."],
                ["starting_date", "completion_date", "."],
                ["requester", "in_charge", "tags"],
                ["description", "description", "description"],
                ["comment", "comment", "comment"],
            ]
        )
