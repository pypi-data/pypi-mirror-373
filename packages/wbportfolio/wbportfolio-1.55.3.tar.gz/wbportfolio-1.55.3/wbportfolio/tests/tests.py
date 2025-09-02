import pytest
from wbcore.test import GenerateTest, default_config

config = {}
for key, value in default_config.items():
    config[key] = list(
        filter(
            lambda x: x.__module__.startswith("wbportfolio")
            and x.__name__
            not in [
                "AggregatedAssetPositionLiquidityPandasView",
                "OrderOrderProposalModelViewSet",
                "PortfolioSwingPricing",
                "PortfolioCashTarget",
                "PortfolioSwingPricingModelViewSet",
                "AccountReconciliationModelViewSet",
                "AccountReconciliationLineModelViewSet",
                "AccountReconciliation",
                "AccountReconciliationLine",
                "TopDownPortfolioCompositionPandasAPIView",
                "CompositionModelPortfolioPandasView",
                "DistributionChartViewSet",
                "DistributionTableViewSet",
                # "ClaimModelViewSet",
                # "ClaimModelSerializer",
            ],
            value,
        )
    )


@pytest.mark.django_db
@GenerateTest(config)
class TestProject:
    pass
