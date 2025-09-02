from wbcore.metadata.configs.buttons.enums import Button
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class OrderOrderProposalButtonConfig(ButtonViewConfig):
    def get_create_buttons(self):
        return {
            Button.SAVE_AND_CLOSE.value,
        }
