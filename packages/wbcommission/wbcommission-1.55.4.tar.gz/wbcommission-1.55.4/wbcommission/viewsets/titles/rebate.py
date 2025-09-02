from wbcore.metadata.configs.titles import TitleViewConfig


class RebatePandasViewTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Rebates"


class RebateProductMarginalityTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Marginality per Product"
