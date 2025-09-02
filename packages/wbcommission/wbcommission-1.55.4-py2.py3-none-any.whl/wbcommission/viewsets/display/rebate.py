from typing import Optional

from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class RebatePandasViewDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                *[dp.Field(key="rebate_" + k, label=v) for k, v in self.view.rebate_types.items()],
                dp.Field(key="rebate_total", label="Total Rebate"),
            ]
        )


class RebateProductMarginalityDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Product", width=Unit.PIXEL(400)),
                dp.Field(
                    label="Management",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="base_management_fees_percent", label="Base Fees", width=Unit.PIXEL(400)),
                        dp.Field(key="management_fees", label="Fees", width=Unit.PIXEL(120)),
                        dp.Field(key="management_rebates", label="Rebates", width=Unit.PIXEL(120)),
                        dp.Field(key="management_marginality", label="Marginality", width=Unit.PIXEL(120)),
                        dp.Field(
                            key="net_management_marginality",
                            label="Net Marginality",
                            width=Unit.PIXEL(150),
                            formatting_rules=[
                                dp.FormattingRule(
                                    style={
                                        "fontWeight": "bold",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
                dp.Field(
                    label="Performance",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="base_performance_fees_percent", label="Base Fees", width=Unit.PIXEL(120)),
                        dp.Field(key="performance_fees", label="Fees", width=Unit.PIXEL(120)),
                        dp.Field(key="performance_rebates", label="Rebates", width=Unit.PIXEL(120)),
                        dp.Field(key="performance_marginality", label="Marginality", width=Unit.PIXEL(120)),
                        dp.Field(
                            key="net_performance_marginality",
                            label="Net Marginality",
                            width=Unit.PIXEL(150),
                            formatting_rules=[
                                dp.FormattingRule(
                                    style={
                                        "fontWeight": "bold",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
                dp.Field(
                    label="Total",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="total_fees", label="Fees", width=Unit.PIXEL(120)),
                        dp.Field(key="total_rebates", label="Rebates", width=Unit.PIXEL(120)),
                        dp.Field(key="total_marginality_percent", label="Marginality", width=Unit.PIXEL(120)),
                        dp.Field(
                            key="total_fees_usd",
                            label="Fees ($)",
                            width=Unit.PIXEL(120),
                            formatting_rules=[
                                dp.FormattingRule(
                                    style={
                                        "fontWeight": "bold",
                                    },
                                ),
                            ],
                        ),
                        dp.Field(
                            key="total_rebates_usd",
                            label="Rebates ($)",
                            width=Unit.PIXEL(120),
                            formatting_rules=[
                                dp.FormattingRule(
                                    style={
                                        "fontWeight": "bold",
                                    },
                                ),
                            ],
                        ),
                        dp.Field(
                            key="total_marginality_usd",
                            label="Net Marginality ($)",
                            width=Unit.PIXEL(120),
                            formatting_rules=[
                                dp.FormattingRule(
                                    style={
                                        "fontWeight": "bold",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        )
