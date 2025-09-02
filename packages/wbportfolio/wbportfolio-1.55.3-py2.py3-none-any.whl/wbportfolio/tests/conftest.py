from pytest_factoryboy import register
from wbcompliance.factories.risk_management import (
    RiskRuleFactory,
    RuleBackendFactory,
    RuleThresholdFactory,
)
from wbcore.contrib.authentication.factories import (
    InternalUserFactory,
    SuperUserFactory,
    UserFactory
)
from wbcore.contrib.currency.factories import CurrencyFactory, CurrencyFXRatesFactory
from wbcore.contrib.directory.factories.entries import (
    CompanyFactory,
    CompanyTypeFactory,
    CustomerStatusFactory,
    EntryFactory,
    PersonFactory,
)
from wbcore.contrib.geography.factories import CityFactory, CountryFactory, StateFactory
from wbcore.contrib.io.factories import (
    CrontabScheduleFactory,
    DataBackendFactory,
    ImportSourceFactory,
    ParserHandlerFactory,
    ProviderFactory,
    SourceFactory,
)
from wbcrm.factories import AccountFactory, AccountRoleFactory, AccountWithOwnerFactory
from wbfdm.factories import (
    CashFactory,
    ClassificationFactory,
    ClassificationGroupFactory,
    EquityFactory,
    ExchangeFactory,
    InstrumentFactory,
    InstrumentListFactory,
    InstrumentPriceFactory,
    InstrumentTypeFactory,
)
from wbportfolio.factories import (
    AccountReconciliationFactory,
    AccountReconciliationLineFactory,
    AdjustmentFactory,
    AssetPositionFactory,
    ClaimFactory,
    CustodianFactory,
    CustomerTradeFactory,
    DailyPortfolioCashFlowFactory,
    DividendTransactionsFactory,
    FeesFactory,
    IndexFactory,
    IndexProductFactory,
    InstrumentPortfolioThroughModelFactory,
    ManagerPortfolioRoleFactory,
    ModelPortfolioFactory,
    ModelPortfolioWithBaseProductFactory,
    NegativeClaimFactory,
    PortfolioCashTargetFactory,
    PortfolioFactory,
    PortfolioSwingPricingFactory,
    ProductFactory,
    ProductGroupFactory,
    ProductGroupRepresentantFactory,
    ProductPortfolioRoleFactory,
    TradeFactory,
    OrderFactory,
    OrderProposalFactory,
    WhiteLabelProductFactory,
    RebalancerFactory,
    RebalancingModelFactory
)
from wbreport.factories import ReportFactory, ReportAssetFactory, ReportVersionFactory, ReportClassFactory, ReportCategoryFactory
from wbcore.tests.conftest import *  # isort:skip

register(AccountFactory)
register(AccountWithOwnerFactory)
register(AccountRoleFactory)

register(ImportSourceFactory)
register(DataBackendFactory)
register(ProviderFactory)
register(SourceFactory)
register(ParserHandlerFactory)
register(CrontabScheduleFactory)
register(AssetPositionFactory)
register(ProductFactory)
register(ProductGroupFactory)
register(ProductGroupRepresentantFactory)
register(PortfolioFactory)
register(InstrumentPortfolioThroughModelFactory)
register(ModelPortfolioFactory)
register(ModelPortfolioWithBaseProductFactory, "model_portfolio_with_base_product")
register(TradeFactory)
register(CustomerTradeFactory)
register(OrderProposalFactory)
register(OrderFactory)
register(DividendTransactionsFactory)
register(FeesFactory)
register(WhiteLabelProductFactory, "white_label_product")
register(InstrumentPriceFactory)
register(IndexProductFactory, "index_product")
register(CurrencyFXRatesFactory)
register(ProductPortfolioRoleFactory, "product_portfolio_role")
register(ManagerPortfolioRoleFactory, "manager_portfolio_role")
register(RebalancerFactory)
register(RebalancingModelFactory)

register(CurrencyFactory)
register(CityFactory)
register(StateFactory)
register(CountryFactory)

register(CompanyFactory)
register(PersonFactory)
register(InternalUserFactory, "internal_user")
register(EntryFactory)
register(CustomerStatusFactory)
register(CompanyTypeFactory)

register(UserFactory)
register(SuperUserFactory, "superuser")
register(CustodianFactory)

register(AdjustmentFactory)
register(IndexFactory)


register(RuleThresholdFactory)
register(RiskRuleFactory)
register(RuleBackendFactory)

register(ClaimFactory)
register(NegativeClaimFactory, "negative_claim")

register(InstrumentFactory)
register(InstrumentTypeFactory)
register(EquityFactory, "equity")
register(CashFactory, "cash")
register(InstrumentListFactory)
register(ExchangeFactory)
register(ClassificationFactory)
register(ClassificationGroupFactory)
register(PortfolioSwingPricingFactory)
register(PortfolioCashTargetFactory)
register(DailyPortfolioCashFlowFactory)

register(AccountReconciliationFactory)
register(AccountReconciliationLineFactory)
register(ReportFactory)
register(ReportAssetFactory)
register(ReportVersionFactory)
register(ReportClassFactory)
register(ReportCategoryFactory)

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbportfolio"))
from .signals import *  # noqa: F401
