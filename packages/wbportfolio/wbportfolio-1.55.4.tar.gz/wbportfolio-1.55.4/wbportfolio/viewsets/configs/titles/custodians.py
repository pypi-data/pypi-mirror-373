from wbcore.metadata.configs.titles import TitleViewConfig


class CustodianTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Custodians"

    def get_instance_title(self):
        return "Custodian"

    def get_create_title(self):
        return "New Custodian"
