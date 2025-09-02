from datetime import datetime
from typing import TYPE_CHECKING

from rest_framework.reverse import reverse
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig
from wbcore.utils.models import WBColor

if TYPE_CHECKING:
    from wbaccounting.viewsets.cashflows import FutureCashFlowPandasAPIViewSetMixin


class FutureCashFlowDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        view: "FutureCashFlowPandasAPIViewSetMixin" = self.view  # type: ignore
        fields = view.get_dataframe(self.request, view.get_queryset()).columns[view.DATE_COL_START :]
        return dp.ListDisplay(
            fields=[
                dp.Field(key="bank_account__iban", label="IBAN"),
                dp.Field(key="bank_account__currency__symbol", label="Currency"),
                *[
                    dp.Field(
                        key=field,
                        label=datetime.strptime(field, "%Y-%m-%d").strftime("%d.%m.%Y"),
                        formatting_rules=[
                            dp.FormattingRule(
                                style={"color": WBColor.GREEN_DARK.value},
                                condition=(">=", 0),
                            ),
                            dp.FormattingRule(
                                style={"color": WBColor.RED_DARK.value},
                                condition=("<", 0),
                            ),
                            *[
                                dp.FormattingRule(style={"fontWeight": "bold"})
                                if view.BOLD
                                else dp.FormattingRule(style={"fontWeight": "normal"})
                            ],
                        ],
                    )
                    for field in fields
                ],
            ],
            tree=True,
            tree_group_field="bank_account__iban",
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_depth=1,
                    lookup="bank_account__id",
                    filter_key="bank_account",
                    list_endpoint=reverse(
                        "wbaccounting:futurecashflowtransaction-list",
                        args=[],
                        request=self.request,
                    ),
                )
            ],
        )
