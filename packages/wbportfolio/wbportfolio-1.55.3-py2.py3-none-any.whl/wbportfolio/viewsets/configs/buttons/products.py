from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbfdm.viewsets.configs.buttons.instruments import InstrumentButtonViewConfig

from wbportfolio.models import Product


class ProductButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()

    def get_custom_instance_buttons(self):
        buttons = [
            bt.DropDownButton(
                label="Commission",
                icon=WBIcon.UNFOLD.icon,
                buttons=(
                    bt.WidgetButton(key="claims", label="Claims"),
                    bt.WidgetButton(key="aum", label="AUM per account"),
                ),
            ),
            *InstrumentButtonViewConfig(self.view, self.request, self.instance).get_custom_instance_buttons(),
            bt.DropDownButton(
                label="Risk Management",
                icon=WBIcon.UNFOLD.icon,
                buttons=[
                    bt.WidgetButton(
                        key="risk_rules",
                        label="Rules",
                        icon=WBIcon.CONFIGURE.icon,
                    ),
                    bt.WidgetButton(
                        key="risk_incidents",
                        label="Incidents",
                        icon=WBIcon.WARNING.icon,
                    ),
                ],
            ),
        ]
        if product_id := self.view.kwargs.get("pk", None):
            product = Product.objects.get(id=product_id)
            report_buttons = []
            for report in product.reports.filter(is_active=True):
                tmp_buttons = []
                if primary_version := report.primary_version:
                    tmp_buttons.append(
                        bt.HyperlinkButton(
                            label="Public Report",
                            endpoint=reverse(
                                "public_report:report_version", args=[primary_version.lookup], request=self.request
                            ),
                        ),
                    )
                    if self.request.user.profile.is_internal or self.request.user.is_superuser:
                        tmp_buttons.append(
                            bt.WidgetButton(
                                label="Widget",
                                endpoint=reverse("wbreport:report-detail", args=[report.id], request=self.request),
                            ),
                        )
                if tmp_buttons:
                    report_buttons.append(bt.DropDownButton(label=str(report), buttons=tmp_buttons))
            if report_buttons:
                buttons.append(bt.DropDownButton(label="Reports", buttons=report_buttons))

        return set(buttons)


class ProductCustomerButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(
                key="historical-chart",
                label="Historical Chart",
                icon=WBIcon.STATS.icon,
            )
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
