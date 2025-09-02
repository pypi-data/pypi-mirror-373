from contextlib import suppress

from rest_framework.reverse import reverse
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig

from wbportfolio.models.portfolio import Portfolio, PortfolioPortfolioThroughModel


class AssetPositionButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return set()

    def get_custom_instance_buttons(self):
        return set()


class AssetPositionPortfolioButtonConfig(AssetPositionButtonConfig):
    def get_custom_buttons(self):
        btns = []
        with suppress(Portfolio.DoesNotExist):
            portfolio = Portfolio.objects.get(id=self.view.kwargs.get("portfolio_id", None))
            btns.append(
                bt.WidgetButton(
                    endpoint=reverse(
                        "wbportfolio:portfolio-contributor-list", args=[portfolio.id], request=self.request
                    ),
                    label="Contributor",
                )
            )
            btns.append(
                bt.WidgetButton(
                    endpoint=(
                        reverse(
                            "wbportfolio:portfolio-distributionchart-list",
                            args=[portfolio.id],
                            request=self.request,
                        )
                    ),
                    label="Distribution Charts",
                )
            )
            btns.append(
                bt.WidgetButton(
                    endpoint=(
                        reverse(
                            "wbportfolio:portfolio-esgaggregation-list",
                            args=[portfolio.id],
                            request=self.request,
                        )
                    ),
                    label="ESG Aggregation",
                )
            )
            cash_management_btns = []

            if portfolio.daily_cashflows.all().exists():
                cash_management_btns.append(
                    bt.WidgetButton(
                        label="Cash Flow",
                        endpoint=reverse(
                            "wbportfolio:portfolio-portfoliocashflow-list",
                            args=[portfolio.id],
                            request=self.request,
                        ),
                    )
                )

            if portfolio.bank_accounts.all().exists():
                bank_account_ids = map(lambda i: str(i), portfolio.bank_accounts.all().values_list("id", flat=True))
                base_url = reverse("wbaccounting:futurecashflow-list", request=self.request)
                cash_flow_url = f"{base_url}?banking_contact={", ".join(bank_account_ids)}"
                cash_management_btns.append(
                    bt.WidgetButton(
                        label="Bank Accounts",
                        endpoint=cash_flow_url,
                    )
                )

            if len(cash_management_btns) > 0:
                btns.append(
                    bt.DropDownButton(
                        label="Cash Management",
                        buttons=cash_management_btns,
                    )
                )
            for rel in PortfolioPortfolioThroughModel.objects.filter(portfolio=portfolio):
                dependency_portfolio = rel.dependency_portfolio
                if dependency_portfolio.assets.exists():
                    btns.append(
                        bt.WidgetButton(
                            endpoint=(
                                reverse(
                                    "wbportfolio:portfolio-asset-list",
                                    args=[dependency_portfolio.id],
                                    request=self.request,
                                )
                            ),
                            label=f"{PortfolioPortfolioThroughModel.Type[rel.type].label} Portfolio",
                        )
                    )
        return set(btns)


class AssetPositionInstrumentButtonConfig(AssetPositionButtonConfig):
    def get_custom_buttons(self):
        if instrument_id := self.view.kwargs.get("instrument_id", None):
            return {
                bt.WidgetButton(
                    endpoint=reverse(
                        "wbportfolio:instrument-assetpositionchart-list", args=[instrument_id], request=self.request
                    ),
                    label="Portfolio Allocation ",
                ),
            }
        return set()


class DistributionChartButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self) -> set:
        if portfolio_id := self.view.kwargs.get("portfolio_id", None):
            return {
                bt.WidgetButton(
                    endpoint=(
                        f"{reverse('wbportfolio:portfolio-distributiontable-list', args=[portfolio_id], request=self.request)}"
                        f"?group_by={self.request.GET.get('group_by')}"
                    ),
                    label="Table Form",
                ),
            }
        return set()


class DistributionTableButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self) -> set:
        if portfolio_id := self.view.kwargs.get("portfolio_id", None):
            return {
                bt.WidgetButton(
                    endpoint=(
                        f"{reverse('wbportfolio:portfolio-distributionchart-list', args=[portfolio_id], request=self.request)}"
                        f"?group_by={self.request.GET.get('group_by')}"
                    ),
                    label="Chart Form",
                ),
            }
        return set()
