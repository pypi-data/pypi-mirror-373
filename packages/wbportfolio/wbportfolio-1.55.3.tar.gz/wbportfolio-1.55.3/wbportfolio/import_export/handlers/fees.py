from datetime import datetime

from wbcore.contrib.currency.import_export.handlers import CurrencyImportHandler
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler


class FeesImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbportfolio.Fees"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currency_handler = CurrencyImportHandler(self.import_source)

    def _deserialize(self, data):
        data["fee_date"] = datetime.strptime(
            data.get("fee_date", data.pop("transaction_date", None)), "%Y-%m-%d"
        ).date()
        from wbportfolio.models import Product

        try:
            product_data = data.pop("product", None)
            if isinstance(product_data, dict):
                data["product"] = Product.objects.get(**product_data)
            else:
                data["product"] = Product.objects.get(id=product_data)
        except Product.DoesNotExist:
            raise DeserializationError("There is no valid linked product for in this row.")

        if "currency" not in data:
            data["currency"] = data["product"].currency
        else:
            data["currency"] = self.currency_handler.process_object(data["currency"], read_only=True)[0]
        data["currency_fx_rate"] = 1.0
        data["total_value"] = data.get("total_value", data.get("total_value_gross", None))
        data["total_value_gross"] = data.get("total_value_gross", data["total_value"])
        data["calculated"] = data.get("calculated", False)

    def _get_instance(self, data, history=None, **kwargs):
        self.import_source.log += "\nGet Fees Instance."
        self.import_source.log += f"\nParameter: Product={data['product']} Date={data['fee_date']}"
        fees = self.model.objects.filter(
            product=data["product"],
            fee_date=data["fee_date"],
            transaction_subtype=data["transaction_subtype"],
            calculated=data["calculated"],
        )
        if fees.exists():
            if fees.count() > 1:
                raise ValueError(f'Number of similar fees found > 1: {fees.values_list("id", flat=True)}')
            self.import_source.log += "\nFees Instance Found." ""
            return fees.first()

    def _create_instance(self, data, **kwargs):
        self.import_source.log += "\nCreate Fees."
        return self.model.objects.create(**data, import_source=self.import_source)
