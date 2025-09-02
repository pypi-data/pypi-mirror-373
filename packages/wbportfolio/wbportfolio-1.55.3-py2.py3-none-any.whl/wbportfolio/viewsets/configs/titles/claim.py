from wbcore.metadata.configs.titles import TitleViewConfig


class ClaimTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Claims"

    def get_instance_title(self):
        return "{{_claimant.computed_str}}: {{shares}} of {{_product.name}} ({{bank}} - {{date}})"

    def get_create_title(self):
        return "New Claim"


class ClaimProductTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"Claims for Product {self.view.product.computed_str}"

    def get_instance_title(self):
        return f"Claim for Product {self.view.product.computed_str}"

    def get_create_title(self):
        return f"New Claim for Product {self.view.product.computed_str}"


class ClaimAccountTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"Claims for Account {self.view.account.computed_str}"

    def get_instance_title(self):
        return f"Claim for Account {self.view.account.computed_str}"

    def get_create_title(self):
        return f"New Claim for Account {self.view.account.computed_str}"


class ClaimEntryTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"Claims from {self.view.entry.computed_str}"

    def get_instance_title(self):
        return f"Claim from {self.view.entry.computed_str}"

    def get_create_title(self):
        return f"New Claim for {self.view.entry.computed_str}"


class ClaimTradeTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"Claims for Customer Trade {str(self.view.trade)}"

    def get_instance_title(self):
        return f"Claim for Customer Trade {str(self.view.trade)}"

    def get_create_title(self):
        return f"New Claim for Customer Trade {str(self.view.trade)}"


class ConsolidatedTradeSummaryTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Consolidated Trade Summary"


class CumulativeNNMChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Cumulative NNM Chart"


class ConsolidatedTradeSummaryDistributionChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Consolidated Trade Summary Distribution Chart"


class ProfitAndLossPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Profit & Loss - Averaging Method (Experimental)"


class NegativeTermimalAccountPerProductTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Negative Sub-Accounts"
