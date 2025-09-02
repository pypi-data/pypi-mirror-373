from datetime import date

from faker import Faker
from pandas.tseries.offsets import BDay
from wbcompliance.factories.risk_management import (
    RiskRuleFactory,
    RuleBackendFactory,
    RuleThresholdFactory,
)
from wbcore.contrib.authentication.factories import (
    InternalUserFactory,
    SuperUserFactory,
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
    AdjustmentFactory,
    AssetPositionFactory,
    ClaimFactory,
    CustodianFactory,
    CustomerTradeFactory,
    DividendTransactionsFactory,
    FeesFactory,
    IndexFactory,
    IndexProductFactory,
    InstrumentPortfolioThroughModelFactory,
    ManagerPortfolioRoleFactory,
    ModelPortfolioFactory,
    ModelPortfolioWithBaseProductFactory,
    NegativeClaimFactory,
    PortfolioFactory,
    ProductFactory,
    ProductGroupFactory,
    ProductGroupRepresentantFactory,
    ProductPortfolioRoleFactory,
    TradeFactory,
    OrderProposalFactory,
    WhiteLabelProductFactory,
)

from ..factories import (
    AssetAllocationFactory,
    AssetAllocationTypeFactory,
    GeographicFocusFactory,
)

from wbcore.tests.conftest import *  # isort:skip


fake = Faker()

register(AccountFactory)
register(AccountWithOwnerFactory)
register(AccountRoleFactory)

register(ImportSourceFactory)
register(DataBackendFactory)
register(ProviderFactory)
register(SourceFactory)
register(ParserHandlerFactory)

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
register(DividendTransactionsFactory)
register(FeesFactory)
register(WhiteLabelProductFactory, "white_label_product")
register(InstrumentPriceFactory)
register(IndexProductFactory, "index_product")
register(CurrencyFXRatesFactory)
register(ProductPortfolioRoleFactory, "product_portfolio_role")
register(ManagerPortfolioRoleFactory, "manager_portfolio_role")

register(CurrencyFactory)
register(CityFactory)
register(StateFactory)
register(CountryFactory)
register(ContinentFactory)

register(CompanyFactory)
register(PersonFactory)
register(InternalUserFactory)
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

register(AssetAllocationTypeFactory)
register(AssetAllocationFactory)
register(GeographicFocusFactory)

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbportfolio"))
