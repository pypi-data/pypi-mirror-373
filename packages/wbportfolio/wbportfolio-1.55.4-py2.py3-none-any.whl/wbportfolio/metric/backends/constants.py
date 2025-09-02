from wbfdm.contrib.metric.dto import MetricField, MetricKey

PORTFOLIO_EBIT = MetricKey(
    key="portfolio_ebit",
    label="EBIT",
    subfields=[
        MetricField(
            key="fy_3",
            label="FY-3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_2",
            label="FY-2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_1",
            label="FY-1",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy0",
            label="FY0",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(key="fy1", label="FY1", decorators=[{"position": "left", "value": "$"}]),
        MetricField(
            key="fy2",
            label="FY2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy3",
            label="FY3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy4",
            label="FY4",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
    ],
)

PORTFOLIO_TOTAL_ASSETS = MetricKey(
    key="portfolio_total_assets",
    label="Total Assets",
    subfields=[
        MetricField(
            key="fy_3",
            label="FY-3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_2",
            label="FY-2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_1",
            label="FY-1",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy0",
            label="FY0",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(key="fy1", label="FY1", decorators=[{"position": "left", "value": "$"}]),
        MetricField(
            key="fy2",
            label="FY2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy3",
            label="FY3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy4",
            label="FY4",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
    ],
)

PORTFOLIO_LIABILITIES = MetricKey(
    key="portfolio_liabilities",
    label="Liabilities",
    subfields=[
        MetricField(
            key="fy_3",
            label="FY-3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_2",
            label="FY-2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_1",
            label="FY-1",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy0",
            label="FY0",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(key="fy1", label="FY1", decorators=[{"position": "left", "value": "$"}]),
        MetricField(
            key="fy2",
            label="FY2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy3",
            label="FY3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy4",
            label="FY4",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
    ],
)

PORTFOLIO_CAPITAL_EMPLOYED = MetricKey(
    key="portfolio_capital_employed",
    label="Capital Employed",
    subfields=[
        MetricField(
            key="fy_3",
            label="FY-3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_2",
            label="FY-2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy_1",
            label="FY-1",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy0",
            label="FY0",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(key="fy1", label="FY1", decorators=[{"position": "left", "value": "$"}]),
        MetricField(
            key="fy2",
            label="FY2",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy3",
            label="FY3",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
        MetricField(
            key="fy4",
            label="FY4",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
        ),
    ],
)

PORTFOLIO_ROCE = MetricKey(
    key="portfolio_roce",
    label="ROCE",
    subfields=[
        MetricField(
            key="fy_3", label="FY-3", list_display_kwargs={"show": "open"}, serializer_kwargs={"percent": True}
        ),
        MetricField(
            key="fy_2", label="FY-2", list_display_kwargs={"show": "open"}, serializer_kwargs={"percent": True}
        ),
        MetricField(
            key="fy_1", label="FY-1", list_display_kwargs={"show": "open"}, serializer_kwargs={"percent": True}
        ),
        MetricField(key="fy0", label="FY0", list_display_kwargs={"show": "open"}, serializer_kwargs={"percent": True}),
        MetricField(key="fy1", label="FY1", serializer_kwargs={"percent": True}),
        MetricField(key="fy2", label="FY2", list_display_kwargs={"show": "open"}, serializer_kwargs={"percent": True}),
        MetricField(key="fy3", label="FY3", list_display_kwargs={"show": "open"}, serializer_kwargs={"percent": True}),
        MetricField(key="fy4", label="FY4", list_display_kwargs={"show": "open"}, serializer_kwargs={"percent": True}),
    ],
)
