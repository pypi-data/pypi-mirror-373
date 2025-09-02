from wbcore.metadata.configs.titles import TitleViewConfig
from wbfdm.models import Instrument


class AdjustmentTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if instrument_id := self.view.kwargs.get("instrument_id", None):
            return f"Adjustments of {str(Instrument.objects.get(id=instrument_id))}"
        return "Adjustments"

    def get_instance_title(self):
        try:
            obj = self.view.get_object()
            return f"Adjustment: {str(obj)}"
        except AssertionError:
            return "Adjustment {{factor}} - {{date}} ({{_equity.computed_str}})"

    def get_create_title(self):
        return "New Adjustment"
