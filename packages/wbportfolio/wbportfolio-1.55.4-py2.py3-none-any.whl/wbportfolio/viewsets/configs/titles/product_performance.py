from wbcore.metadata.configs.titles import TitleViewConfig


class PerformancePandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Product Performances & AuM"


class PerformanceComparisonTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Product Performances Summary"


class ProductPerformanceNetNewMoneyTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Product Performance New Money"
