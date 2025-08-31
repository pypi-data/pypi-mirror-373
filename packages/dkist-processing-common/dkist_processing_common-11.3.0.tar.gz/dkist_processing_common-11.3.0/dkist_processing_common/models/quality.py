"""Support classes used to create a quality report."""

from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo


class Plot2D(BaseModel):
    """Support class use to hold the data for creating a 2D plot in the quality report."""

    xlabel: str
    ylabel: str
    series_data: dict[str, list[list[Any]]]
    series_name: str | None = None
    ylabel_horizontal: bool = False
    ylim: tuple[float, float] | None = None
    plot_kwargs: dict[str, dict[str, Any]] = Field(default_factory=dict)
    sort_series: bool = True


class VerticalMultiPanePlot2D(BaseModel):
    """
    Support class to hold a multi-pane plot with plots stacked vertically.

    This type of metric is really geared towards plots that share an X axis and have no gap between them. If you just
    want two separate plots it's probably better to use a list of `Plot2D` objects.
    """

    top_to_bottom_plot_list: list[Plot2D]
    match_x_axes: bool = True
    no_gap: bool = True
    top_to_bottom_height_ratios: list[float] | None = None

    @field_validator("top_to_bottom_height_ratios")
    @classmethod
    def ensure_same_number_of_height_ratios_and_plots(
        cls, height_ratios: list[float] | None, info: ValidationInfo
    ) -> list[float]:
        """
        Make sure that the number of height ratios is the same as the number of plots.

        Also populates default, same-size ratios if no ratios were given.
        """
        try:
            plot_list = info.data["top_to_bottom_plot_list"]
        except KeyError:
            # The plot list didn't validate for some reason. We're about to error anyway.
            return [1.0]

        num_plots = len(plot_list)
        if height_ratios is None:
            return [1.0] * num_plots

        if len(height_ratios) != num_plots:
            raise ValueError(
                f"The number of items in `top_to_bottom_height_ratios` list ({len(height_ratios)}) is not "
                f"the same as the number of plots ({num_plots})"
            )

        return height_ratios


class SimpleTable(BaseModel):
    """Support class to hold a simple table to be inserted into the quality report."""

    rows: list[list[Any]]
    header_row: bool = True
    header_column: bool = False


class ModulationMatrixHistograms(BaseModel):
    """Support class for holding the big ol' grid of histograms that represent the modulation matrix fits."""

    modmat_list: list[list[list[float]]]


class EfficiencyHistograms(BaseModel):
    """Support class for holding 4 histograms that correspond to efficiencies of the 4 stokes components."""

    efficiency_list: list[list[float]]


class PlotHistogram(BaseModel):
    """Support class to hold 1D data for plotting a histogram."""

    xlabel: str
    series_data: dict[str, list[float]]
    series_name: str | None = None
    vertical_lines: dict[str, float] | None


class PlotRaincloud(BaseModel):
    """Support class to hold data series for fancy-ass violin plots."""

    xlabel: str
    ylabel: str
    categorical_column_name: str
    distribution_column_name: str
    dataframe_json: str
    hue_column_name: str | None
    ylabel_horizontal: bool | None


class ReportMetric(BaseModel):
    """A Quality Report is made up of a list of metrics with the schema defined by this class."""

    name: str
    description: str
    metric_code: str
    facet: str | None = None
    statement: str | list[str] | None = None
    plot_data: Plot2D | list[Plot2D] | None = None
    multi_plot_data: VerticalMultiPanePlot2D | None = None
    histogram_data: PlotHistogram | list[PlotHistogram] | None = None
    table_data: SimpleTable | list[SimpleTable] | None = None
    modmat_data: ModulationMatrixHistograms | None = None
    efficiency_data: EfficiencyHistograms | None = None
    raincloud_data: PlotRaincloud | None = None
    warnings: list[str] | None = None
