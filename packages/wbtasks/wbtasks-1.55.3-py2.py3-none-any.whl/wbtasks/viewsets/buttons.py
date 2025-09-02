from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class TaskButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {
            bt.WidgetButton(key="see_activity", label="Linked Activity", icon=WBIcon.CALENDAR.icon),
            bt.WidgetButton(key="widget", label="Linked Widget", icon=WBIcon.LINK.icon),
        }
