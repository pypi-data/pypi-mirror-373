from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class RegisterButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {bt.WidgetButton(key="trades", label="Trades", icon=WBIcon.TRADE.icon)}

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
