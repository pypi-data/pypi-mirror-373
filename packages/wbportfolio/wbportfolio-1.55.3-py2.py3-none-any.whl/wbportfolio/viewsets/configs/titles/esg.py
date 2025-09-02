from wbcore.metadata.configs.titles import TitleViewConfig


class ESGMetricAggregationPortfolioPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if esg_aggregation := self.view.esg_aggregation:
            metric_label = f"{esg_aggregation.value} ({esg_aggregation.get_aggregation().value})"
        else:
            metric_label = "ESG metric"
        return f"{self.view.portfolio}: {metric_label}"
