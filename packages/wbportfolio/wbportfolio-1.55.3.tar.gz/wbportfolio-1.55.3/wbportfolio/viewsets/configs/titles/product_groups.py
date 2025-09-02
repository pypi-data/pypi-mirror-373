from wbcore.metadata.configs.titles import TitleViewConfig


class ProductGroupTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Product Groups"

    def get_instance_title(self):
        return "Product Group: {{title}} {{umbrella}}"

    def get_create_title(self):
        return "New Product Group"
