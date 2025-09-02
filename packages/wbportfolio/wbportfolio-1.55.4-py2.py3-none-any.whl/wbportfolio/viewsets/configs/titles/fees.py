from wbcore.metadata.configs.titles import TitleViewConfig


class FeesTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Fees"

    def get_instance_title(self):
        return "Fees: {{_product.name}} {{date}}"

    def get_create_title(self):
        return "New Fees"


class FeesProductTitleConfig(FeesTitleConfig):
    def get_list_title(self):
        return f"Fees: {self.view.product}"


class FeesAggregatedProductTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"Aggregated Fees for {self.view.product}"
