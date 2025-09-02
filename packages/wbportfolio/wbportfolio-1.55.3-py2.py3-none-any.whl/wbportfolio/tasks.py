from contextlib import suppress
from datetime import date, timedelta

from django.db.models import ProtectedError, Q

from wbportfolio.models import Portfolio, Trade
from wbportfolio.models.products import Product

from .fdm.tasks import *  # noqa


@shared_task(queue="portfolio")
def daily_active_product_task(today: date | None = None):
    if not today:
        today = date.today()
    qs = Product.active_objects.all()
    for product in tqdm(qs, total=qs.count()):
        product.update_outstanding_shares()
        product.check_and_notify_product_termination_on_date(today)


@shared_task(queue="portfolio")
def periodically_clean_marked_for_deletion_trades(max_allowed_iterations: int = 5):
    # Get all trade marked for deletion or pending and older than 7 days (i.e. After 7 days, we consider the pending trade obselete)
    qs = Trade.objects.filter(
        Q(marked_for_deletion=True) | (Q(pending=True) & Q(transaction_date__lt=date.today() - timedelta(days=7)))
    )
    i = 0

    # We try several times in case the trades deletion mechanism shifts the marked for deletion tag forwards
    while i < max_allowed_iterations and qs.exists():
        for t in qs:
            with suppress(ProtectedError):
                t.delete()
        qs = Trade.objects.filter(marked_for_deletion=True)
        i += 1


# A Task to run every day to update automatically the preferred classification
# per instrument of each wbportfolio containing assets.
@shared_task(queue="portfolio")
def update_preferred_classification_per_instrument_and_portfolio_as_task():
    for portfolio in Portfolio.tracked_objects.all():
        portfolio.update_preferred_classification_per_instrument()


# This task needs to run at fix interval. It will trigger the basic wbportfolio synchronization update:
# - Fetch for stainly price at t-1
# - propagate (or update) t-2 asset positions into t-1
# - Synchronize wbportfolio at t-1
# - Compute Instrument Price estimate at t-1
