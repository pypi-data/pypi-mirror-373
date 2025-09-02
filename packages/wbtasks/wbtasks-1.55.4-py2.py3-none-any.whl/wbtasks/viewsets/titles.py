from wbcore.metadata.configs.titles import TitleViewConfig


class TaskTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "{{title}}"

    def get_list_title(self):
        return "Tasks"

    def get_create_title(self):
        return "Create Task"
