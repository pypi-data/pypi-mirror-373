import typing

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig

if typing.TYPE_CHECKING:
    from wbfdm.viewsets import StatementPandasViewSet


class StatementDisplayViewConfig(DisplayViewConfig):
    view: "StatementPandasViewSet"
    DEFAULT_COL_WIDTH = 100

    def get_list_display(self) -> dp.ListDisplay:
        def generate_year_field(year: str) -> dp.Field:
            year_col = f"{year}-Y"
            year_column = dp.Field(
                key=year,
                label=year,
                open_by_default=False,
                children=[
                    *map(
                        lambda interim_col: dp.Field(
                            key=interim_col,
                            label=interim_col[5:],
                            show="open",
                            width=self.DEFAULT_COL_WIDTH,
                        ),
                        filter(lambda col: year in col, self.view.interim_columns),
                    ),
                    dp.Field(
                        key=year_col,
                        label="Y",
                        width=self.DEFAULT_COL_WIDTH,
                    ),
                ],
            )

            return year_column

        return dp.ListDisplay(
            fields=[
                dp.Field(key="external_code", label="Code", pinned="left", width=self.DEFAULT_COL_WIDTH),
                dp.Field(key="external_description", label="Description", pinned="left"),
                dp.Field(key="progress", label="Yearly Trend", pinned="left"),
                *map(lambda x: generate_year_field(str(x)), self.view.year_columns),
            ],
        )
