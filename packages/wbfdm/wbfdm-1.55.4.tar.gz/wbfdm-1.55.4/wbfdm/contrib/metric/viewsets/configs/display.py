from typing import Any, Optional

from rest_framework.reverse import reverse
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import Display
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbfdm.contrib.metric.dto import MetricField


class InstrumentMetricDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="basket_repr", label="Basket", pinned="left"),
                dp.Field(key="key", label="Key"),
                dp.Field(key="date", label="Date"),
                dp.Field(key="instrument", label="Instrument"),
                dp.Field(key="parent_metric", label="Parent Metric"),
            ],
            tree=True,
            tree_group_field="basket_repr",
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_key="parent_metric",
                    filter_depth=1,
                    # lookup="id_repr",
                    clear_filter=True,
                    filter_blacklist=["parent__isnull"],
                    list_endpoint=reverse(
                        "metric:instrumentmetric-list",
                        args=[],
                        request=self.request,
                    ),
                )
            ],
        )

    def get_instance_display(self) -> Display:
        children_metrics_section = create_simple_section(
            "children_metrics_section", "Child Metrics", [["children_metrics"]], "children_metrics", collapsed=True
        )
        return create_simple_display(
            [
                ["basket_content_type", "basket_id", "basket_repr"],
                ["date", "key", "instrument"],
                [repeat_field(3, "metrics")],
                [repeat_field(3, "children_metrics")],
            ],
            [children_metrics_section],
        )


class InstrumentMetricPivotedListDisplayConfig(DisplayViewConfig):
    """
    Instrument metric Class to register automatically metrics fields into the list display.

    The view attribute is expected to inherit from InstrumentMetricMixin
    """

    def _get_metric_field_attr(self, field: MetricField) -> dict[str, Any]:
        attrs = dict(width=75)
        attrs.update(field.list_display_kwargs)
        return attrs

    def _get_metric_list_display(self) -> dp.ListDisplay:
        metrics = []

        for metric_key in self.view.metric_keys:
            metric_label = metric_key.label
            fields = []
            for subfield in metric_key.subfields:
                field_key = f"{metric_key.key}_{subfield.key}"
                fields.append(dp.Field(key=field_key, label=subfield.label, **self._get_metric_field_attr(subfield)))
            metrics.append(dp.Field(key=None, label=metric_label, children=fields))

        return dp.ListDisplay(fields=[dp.Field(label="Metrics", open_by_default=False, key=None, children=metrics)])

    def _get_metadata(self) -> Any:
        display = self.get_metadata()
        if "list" in display:
            list_display = self._get_metric_list_display()
            if isinstance(list_display, Display):
                metrics_list_display = list_display.serialize()
            else:
                metrics_list_display = dict(list_display or {})
            display["list"]["fields"].extend(metrics_list_display["fields"])
        return display
