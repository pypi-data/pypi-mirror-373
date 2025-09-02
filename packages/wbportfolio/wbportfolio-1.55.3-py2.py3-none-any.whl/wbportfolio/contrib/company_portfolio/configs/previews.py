from wbcore.contrib.directory.viewsets.previews import EntryPreviewConfig
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field


class CompanyPreviewConfig(EntryPreviewConfig):
    def get_display(self) -> Display:
        fields = [
            [repeat_field(2, "computed_str")],
            ["primary_telephone", "primary_email"],
            [repeat_field(2, "primary_manager")],
            ["asset_under_management", "invested_assets_under_management_usd"],
            [repeat_field(2, "potential")],
        ]
        try:
            entry = self.view.get_object()
            if entry.profile_image:
                fields.insert(0, [repeat_field(2, "profile_image")])
        except Exception:
            pass

        return create_simple_display(fields)

    def get_buttons(self):
        buttons = super().get_buttons()
        buttons.append(
            bt.WidgetButton(key="asset_allocation_table", icon=WBIcon.DATA_LIST.icon, label="Asset Allocation"),
        )
        buttons.append(
            bt.WidgetButton(key="geographic_focus_table", icon=WBIcon.DATA_LIST.icon, label="Geographic Focus"),
        )
        return buttons
