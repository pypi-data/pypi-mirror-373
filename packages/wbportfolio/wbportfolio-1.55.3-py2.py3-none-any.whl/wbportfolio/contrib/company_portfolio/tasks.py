from datetime import date

from celery import shared_task
from django.db.models import Exists, OuterRef
from tqdm import tqdm
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import Company
from wbcrm.models import Account

from .models import CompanyPortfolioData, Updater


@shared_task(queue="portfolio")
def update_all_portfolio_data(val_date: date | None = None):
    if not val_date:
        val_date = CurrencyFXRates.objects.latest("date").date
    updater = Updater(val_date)
    qs = Company.objects.annotate(
        has_account=Exists(Account.objects.filter(owner=OuterRef("pk"))),
        has_portfolio_data=Exists(CompanyPortfolioData.objects.filter(company=OuterRef("pk"))),
    )
    for company in tqdm(qs, total=qs.count()):
        updater.update_company_data(company)
