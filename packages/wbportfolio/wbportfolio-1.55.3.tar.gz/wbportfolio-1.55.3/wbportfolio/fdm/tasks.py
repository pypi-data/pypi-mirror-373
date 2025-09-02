from celery import shared_task
from tqdm import tqdm
from wbfdm.models import Controversy, Instrument

from wbportfolio.models import AssetPosition


@shared_task(queue="portfolio")
def synchronize_portfolio_controversies():
    qs = AssetPosition.objects.values("underlying_instrument").distinct("underlying_instrument")
    for row in tqdm(qs, total=qs.count()):
        for controversy in Instrument.objects.filter(id=row["underlying_instrument"]).dl.esg_controversies():
            Controversy.sync_from_dataloader(controversy)
