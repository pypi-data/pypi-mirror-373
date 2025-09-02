from datetime import datetime, timedelta

from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler
from wbfdm.import_export.handlers.instrument import InstrumentImportHandler


class AdjustmentImportHandler(ImportExportHandler):
    MODEL_APP_LABEL = "wbportfolio.Adjustment"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)

    def _deserialize(self, data):
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        data["instrument"] = self.instrument_handler.process_object(
            data["instrument"], only_security=True, read_only=True
        )[0]
        if data["factor"] is None:
            raise DeserializationError("Can't process this data: no factor")

    def _get_instance(self, data, history=None, **kwargs):
        self.import_source.log += "\nGet Adjustment Instance."
        self.import_source.log += f"\nParameter: Instrument={data['instrument']} Date={data['date']}"

        if exact_adjustment := data["instrument"].pms_adjustments.filter(date=data["date"]).first():
            return exact_adjustment
        potential_adjustments = data["instrument"].pms_adjustments.filter(
            date__gte=data["date"] - timedelta(days=7),
            date__lte=data["date"] + timedelta(days=7),
            factor=data["factor"],
        )
        if potential_adjustments.exists():
            return potential_adjustments.first()

    def _create_instance(self, data, **kwargs):
        self.import_source.log += "\nCreate Adjustment datapoint."
        return self.model.objects.create(**data, import_source=self.import_source)
