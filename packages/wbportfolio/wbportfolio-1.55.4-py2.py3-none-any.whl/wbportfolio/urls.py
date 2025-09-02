from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbportfolio import viewsets

router = WBCoreRouter()
router.register(r"assetposition", viewsets.AssetPositionModelViewSet, basename="assetposition")
router.register(r"adjustment", viewsets.AdjustmentModelViewSet, basename="adjustment")
router.register(r"product", viewsets.ProductModelViewSet, basename="product")
router.register(r"product_group", viewsets.ProductGroupModelViewSet, basename="product_group")
router.register(r"productcustomer", viewsets.ProductCustomerModelViewSet, basename="productcustomer")
router.register(r"productrepresentation", viewsets.ProductRepresentationViewSet, basename="productrepresentation")
router.register(
    r"product_grouprepresentation", viewsets.ProductGroupRepresentationViewSet, basename="product_grouprepresentation"
)
router.register(
    r"custodianrepresentation", viewsets.CustodianRepresentationViewSet, basename="custodianrepresentation"
)


router.register(r"portfolio", viewsets.PortfolioModelViewSet, basename="portfolio")
router.register(r"portfoliocashflow", viewsets.DailyPortfolioCashFlowModelViewSet, basename="portfoliocashflow")
router.register(r"portfolioswingpricing", viewsets.PortfolioSwingPricingModelViewSet, basename="portfolioswingpricing")
router.register(r"portfoliocashtarget", viewsets.PortfolioCashTargetModelViewSet, basename="portfoliocashtarget")

router.register(
    r"portfoliorepresentation", viewsets.PortfolioRepresentationViewSet, basename="portfoliorepresentation"
)

router.register(r"portfoliorole", viewsets.PortfolioRoleModelViewSet, basename="portfoliorole")


router.register(r"fees", viewsets.FeesModelViewSet, basename="fees")
router.register(r"trade", viewsets.TradeModelViewSet, basename="trade")
router.register(
    r"subscriptionredemption", viewsets.SubscriptionRedemptionModelViewSet, basename="subscriptionredemption"
)

router.register(r"traderepresentation", viewsets.TradeRepresentationViewSet, basename="traderepresentation")
router.register(
    r"orderproposalrepresentation", viewsets.OrderProposalRepresentationViewSet, basename="orderproposalrepresentation"
)
router.register(
    r"rebalancingmodelrepresentation",
    viewsets.RebalancingModelRepresentationViewSet,
    basename="rebalancingmodelrepresentation",
)
router.register(
    r"rebalancerrepresentation",
    viewsets.RebalancerRepresentationViewSet,
    basename="rebalancerrepresentation",
)
router.register(
    r"rebalancer",
    viewsets.RebalancerModelViewSet,
    basename="rebalancer",
)
router.register(
    r"feesproductperformance", viewsets.ProductPerformanceFeesModelViewSet, basename="feesproductperformance"
)
router.register(r"aumchart", viewsets.InstrumentPriceAUMDataChartView, basename="aumchart")

router.register(r"custodian", viewsets.CustodianModelViewSet, basename="custodian")

router.register(r"orderproposal", viewsets.OrderProposalModelViewSet, basename="orderproposal")

router.register(
    r"assetandnetnewmoneyprogression",
    viewsets.AssetAndNetNewMoneyProgressionChartViewSet,
    basename="assetandnetnewmoneyprogression",
)


# Subrouter for Portfolio
portfolio_router = WBCoreRouter()
portfolio_router.register(
    r"portfoliocashflow", viewsets.DailyPortfolioCashFlowModelViewSet, basename="portfolio-portfoliocashflow"
)
portfolio_router.register(r"asset", viewsets.AssetPositionPortfolioModelViewSet, basename="portfolio-asset")
portfolio_router.register(r"contributor", viewsets.ContributorPortfolioChartView, basename="portfolio-contributor")
portfolio_router.register(r"trade", viewsets.TradePortfolioModelViewSet, basename="portfolio-trade")
portfolio_router.register(
    r"instrument", viewsets.InstrumentPortfolioThroughPortfolioModelViewSet, basename="portfolio-instrument"
)
portfolio_router.register(
    r"preferredclassification",
    viewsets.InstrumentPreferedClassificationThroughProductModelViewSet,
    basename="portfolio-preferredclassification",
)
portfolio_router.register(
    r"orderproposal", viewsets.OrderProposalPortfolioModelViewSet, basename="portfolio-orderproposal"
)
portfolio_router.register(
    r"dependencyportfolio", viewsets.PortfolioPortfolioThroughModelViewSet, basename="portfolio-dependencyportfolio"
)
portfolio_router.register(
    r"modelcompositionpandas",
    viewsets.CompositionModelPortfolioPandasView,
    basename="portfolio-modelcompositionpandas",
)

portfolio_router.register(
    r"distributionchart",
    viewsets.DistributionChartViewSet,
    basename="portfolio-distributionchart",
)
portfolio_router.register(
    r"distributiontable",
    viewsets.DistributionTableViewSet,
    basename="portfolio-distributiontable",
)
portfolio_router.register(
    r"esgaggregation",
    viewsets.ESGMetricAggregationPortfolioPandasViewSet,
    basename="portfolio-esgaggregation",
)
portfolio_router.register(
    r"treegraphchart",
    viewsets.PortfolioTreeGraphChartViewSet,
    basename="portfolio-treegraphchart",
)
portfolio_router.register(
    r"topdowncomposition",
    viewsets.TopDownPortfolioCompositionPandasAPIView,
    basename="portfolio-topdowncomposition",
)

router.register(r"register", viewsets.RegisterModelViewSet, basename="register")
router.register(r"registerrepresentation", viewsets.RegisterRepresentationViewSet, basename="registerrepresentation")


# Subrouter for Products
product_router = WBCoreRouter()
product_router.register(r"nominalchart", viewsets.NominalProductChartView, basename="product-nominalchart")
product_router.register(r"aumchart", viewsets.AUMProductChartView, basename="product-aumchart")
product_router.register(r"claim", viewsets.ClaimProductModelViewSet, basename="product-claim")
product_router.register(r"feesaggregated", viewsets.FeesAggregatedProductPandasView, basename="product-feesaggregated")
product_router.register(r"fees", viewsets.FeesProductModelViewSet, basename="product-fees")

# Subrouter for Order Proposal
order_proposal_router = WBCoreRouter()
order_proposal_router.register(r"trade", viewsets.OrderOrderProposalModelViewSet, basename="orderproposal-order")

trade_router = WBCoreRouter()
trade_router.register(r"claim", viewsets.ClaimTradeModelViewSet, basename="trade-claim")

instrument_router = WBCoreRouter()

instrument_router.register(r"trade", viewsets.TradeInstrumentModelViewSet, basename="instrument-trade")
instrument_router.register(
    r"subscriptionredemption",
    viewsets.SubscriptionRedemptionInstrumentModelViewSet,
    basename="instrument-subscriptionredemption",
)
instrument_router.register(
    r"custodiandistribution",
    viewsets.CustodianDistributionInstrumentChartViewSet,
    basename="instrument-custodiandistribution",
)
instrument_router.register(
    r"customerdistribution",
    viewsets.CustomerDistributionInstrumentChartViewSet,
    basename="instrument-customerdistribution",
)
instrument_router.register(r"asset", viewsets.AssetPositionInstrumentModelViewSet, basename="instrument-asset")

instrument_router.register(
    r"portfoliorole", viewsets.PortfolioRoleInstrumentModelViewSet, basename="instrument-portfoliorole"
)

instrument_router.register(r"adjustment", viewsets.AdjustmentEquityModelViewSet, basename="instrument-adjustment")
instrument_router.register(
    r"assetpositionchart",
    viewsets.AssetPositionUnderlyingInstrumentChartViewSet,
    basename="instrument-assetpositionchart",
)

# app_name = 'wbportfolio'

router.register(r"productperformance", viewsets.PerformancePandasView, basename="productperformance")
router.register(
    r"productperformancennmlist",
    viewsets.ProductPerformanceNetNewMoneyListViewSet,
    basename="productperformancennmlist",
)
router.register(
    r"productperformancecomparison", viewsets.PerformanceComparisonPandasView, basename="productperformancecomparison"
)
router.register(r"productcashposition", viewsets.CashPositionPortfolioPandasAPIView, basename="productcashposition")
router.register(r"assetpositiongroupby", viewsets.AssetPositionPandasView, basename="assetpositiongroupby")
router.register(
    r"aggregatedassetpositionliquidity",
    viewsets.AggregatedAssetPositionLiquidityPandasView,
    basename="aggregatedassetpositionliquidity",
)

router.register(r"accountreconciliation", viewsets.AccountReconciliationModelViewSet, basename="accountreconciliation")
router.register(
    r"accountreconciliationline", viewsets.AccountReconciliationLineModelViewSet, basename="accountreconciliationline"
)

account_reconciliation_router = WBCoreRouter()
account_reconciliation_router.register(
    r"accountreconciliationline",
    viewsets.AccountReconciliationLineModelViewSet,
    basename="accountreconciliation-accountreconciliationline",
)

# Claim routers
router.register(r"claimrepresentation", viewsets.ClaimRepresentationViewSet, basename="claimrepresentation")
router.register(r"claim", viewsets.ClaimModelViewSet, basename="claim")
router.register(r"claim-api", viewsets.ClaimAPIModelViewSet, basename="claim-api")
router.register(
    r"negativeaccountproduct",
    viewsets.NegativeTermimalAccountPerProductModelViewSet,
    basename="negativeaccountproduct",
)
router.register(
    r"aumtable",
    viewsets.ConsolidatedTradeSummaryTableView,
    basename="aumtable",
)
router.register(
    r"consolidatedtradesummarydistributionchart",
    viewsets.ConsolidatedTradeSummaryDistributionChart,
    basename="consolidatedtradesummarydistributionchart",
)
router.register(
    r"cumulativennmchart",
    viewsets.CumulativeNNMChartView,
    basename="cumulativennmchart",
)

router.register(
    r"pnltable",
    viewsets.ProfitAndLossPandasView,
    basename="pnltable",
)

account_router = WBCoreRouter()
account_router.register(r"claim", viewsets.ClaimAccountModelViewSet, basename="account-claim")


entry_router = WBCoreRouter()
entry_router.register(r"claim", viewsets.ClaimEntryModelViewSet, basename="entry-claim")


urlpatterns = [
    path("", include(router.urls)),
    path("product/<int:product_id>/", include(product_router.urls)),
    path("trade/<int:trade_id>/", include(trade_router.urls)),
    path("portfolio/<int:portfolio_id>/", include(portfolio_router.urls)),
    path("orderproposal/<int:order_proposal_id>/", include(order_proposal_router.urls)),
    path("instrument/<int:instrument_id>/", include(instrument_router.urls)),
    path("account/<int:account_id>/", include(account_router.urls)),
    path("entry/<int:entry_id>/", include(entry_router.urls)),
    path("accountreconciliation/<int:accountreconciliation_id>/", include(account_reconciliation_router.urls)),
]
