from wbcore.metadata.configs.titles import TitleViewConfig


class CurrencyTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "{{key}} ({{symbol}})"
