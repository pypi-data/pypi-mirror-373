from wbcore.metadata.configs.titles import TitleViewConfig


class RegisterTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Registers"

    def get_instance_title(self):
        return "Register: {{register_reference}}"

    def get_create_title(self):
        return "New Register"
