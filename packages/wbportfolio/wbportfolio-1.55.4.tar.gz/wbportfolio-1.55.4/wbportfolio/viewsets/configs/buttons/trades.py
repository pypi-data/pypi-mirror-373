from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbfdm.models import Instrument


class TradeButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {bt.WidgetButton(key="claims", label="Claims", icon=WBIcon.TRADE.icon)}

    def get_custom_instance_buttons(self):
        btn = self.get_custom_list_instance_buttons()
        btn.add(
            bt.HyperlinkButton(
                key="import_source",
                label="Import Source",
                icon=WBIcon.SAVE.icon,
            )
        )
        return btn


class TradeInstrumentButtonConfig(TradeButtonConfig):
    def get_custom_buttons(self):
        res = set()
        if instrument_id := self.view.kwargs.get("instrument_id", None):
            instrument = Instrument.objects.get(id=instrument_id)
            res = {
                bt.WidgetButton(
                    endpoint=reverse(
                        "wbportfolio:instrument-custodiandistribution-list", args=[instrument_id], request=self.request
                    ),
                    label="Custodian Distribution",
                ),
                bt.WidgetButton(
                    endpoint=reverse(
                        "wbportfolio:instrument-customerdistribution-list", args=[instrument_id], request=self.request
                    ),
                    label="Customer Distribution",
                ),
            }
            if instrument.security_instrument_type.key == "product":
                res.add(
                    bt.WidgetButton(
                        endpoint=reverse(
                            "wbportfolio:product-nominalchart-list", args=[instrument_id], request=self.request
                        ),
                        label="Nominal Chart",
                    )
                )
                res.add(
                    bt.WidgetButton(
                        endpoint=reverse(
                            "wbportfolio:product-aumchart-list", args=[instrument_id], request=self.request
                        ),
                        label="AUM Chart",
                    )
                )
        return res
