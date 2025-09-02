from wbcore.metadata.configs.titles import TitleViewConfig

from wbportfolio.models import Product


class PortfolioRoleTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Portfolio Roles"

    def get_instance_title(self):
        return "Portfolio Role"

    def get_create_title(self):
        return "Create New Role"


class PortfolioRoleInstrumentTitleConfig(PortfolioRoleTitleConfig):
    def get_list_title(self):
        product = Product.objects.get(id=self.view.kwargs["instrument_id"])
        return f"Portfolio Role for {product.name}"

    def get_create_title(self):
        product = Product.objects.get(id=self.view.kwargs["instrument_id"])
        return f"New Portfolio Role for {product.name}"
