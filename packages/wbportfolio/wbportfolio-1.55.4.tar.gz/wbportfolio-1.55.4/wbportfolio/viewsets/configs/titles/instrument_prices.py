from wbcore.metadata.configs.titles import TitleViewConfig

from wbportfolio.models import Product


class InstrumentPriceAUMDataTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Assets under Management"


# Product Portfolio Viewsets
class NominalProductTitleConfig(TitleViewConfig):
    def get_list_title(self):
        product = Product.objects.get(id=self.view.kwargs["product_id"])
        return f"{str(product)}: Nominal Value"


class AUMProductTitleConfig(TitleViewConfig):
    def get_list_title(self):
        product = Product.objects.get(id=self.view.kwargs["product_id"])
        return f"{str(product)}: Assets under Management"
