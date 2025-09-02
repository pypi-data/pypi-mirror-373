from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class FeesButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.HyperlinkButton(
                key="import_source",
                label="Import Source",
                icon=WBIcon.SAVE.icon,
            )
        }
