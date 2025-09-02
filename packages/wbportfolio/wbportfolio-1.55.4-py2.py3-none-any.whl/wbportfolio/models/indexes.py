from wbfdm.models.instruments import InstrumentType

from .mixins.instruments import PMSInstrumentAbstractModel


class Index(PMSInstrumentAbstractModel):
    def pre_save(self):
        super().pre_save()
        self.instrument_type = InstrumentType.INDEX
        if "market_data" not in self.dl_parameters:
            # we default to the internal dataloader
            self.dl_parameters["market_data"] = {
                "path": "wbfdm.contrib.internal.dataloaders.market_data.MarketDataDataloader"
            }
        self.is_managed = True

    class Meta:
        verbose_name = "Index"
        verbose_name_plural = "Indexes"
