from datetime import datetime
from enum import Enum
from typing import ClassVar, List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field, StringConstraints, field_serializer
from typing_extensions import Annotated

from kelvin.krn import KRNAssetDataQuality, KRNAssetDataStream, KRNAssetDataStreamDataQuality
from kelvin.message.utils import to_rfc3339_timestamp


def to_camel(string: str) -> str:
    s = "".join(word.capitalize() for word in string.split("_"))
    return s[0].lower() + s[1:]


class Evidence(BaseModel):
    model_config = {"extra": "allow"}
    _TYPE: ClassVar[str] = ""


class BaseEvidence(BaseModel):
    type: str
    payload: Evidence


class Markdown(Evidence):
    """
    Evidence representing a block of markdown content.

    Attributes:
        title (Optional[str]): The title of the markdown content, displayed as a heading or label.
        markdown (str): The markdown-formatted text content to be rendered.

    Notes:
        - The `markdown` attribute should contain valid markdown syntax to ensure correct rendering.
    """

    _TYPE = "markdown"

    title: Optional[str] = None
    markdown: str


class IFrame(Evidence):
    """
    Evidence representing embedded iframe content, typically used to display external webpages or media as evidence.

    Attributes:
        title (Optional[str]): The title of the iframe content.
        url (AnyHttpUrl): The URL of the external content to be displayed within the iframe.

    Notes:
        - The `url` must be a valid HTTP or HTTPS URL for secure embedding.
    """

    _TYPE = "iframe"

    title: Optional[str] = None
    url: AnyHttpUrl


class Image(Evidence):
    """
    Evidence representing an image.

    Attributes:
        title (Optional[str]): The title of the image evidence.
        description (Optional[str]): A description or caption for the image, providing additional context.
        url (AnyHttpUrl): The URL of the image source, used for displaying the image.
        timestamp (Optional[datetime]): The timestamp related with the image was created.
    """

    _TYPE = "image"

    title: Optional[str] = None
    description: Optional[str] = None
    url: AnyHttpUrl
    timestamp: Optional[datetime] = None


class Chart(Evidence):
    """
    Evidence representing a generic chart, used as an interface for Highcharts configurations.
    For detailed chart options and configuration, see the [Highcharts API documentation]
    (https://api.highcharts.com/highcharts/).

    Attributes:
        timestamp (Optional[datetime]): The timestamp related with the chart.
        title (Optional[str]): The title displayed on the chart.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    model_config = {"extra": "allow", "alias_generator": to_camel, "populate_by_name": True}

    _TYPE = "chart"

    timestamp: Optional[datetime] = None
    title: Optional[str] = None


class Series(BaseModel):
    model_config = {"extra": "allow"}

    name: str
    type: Optional[str] = None
    data: list


class BarSeries(Series):
    type: str = "bar"


class LineSeries(Series):
    type: str = "line"


class LineChart(Chart):
    """
    Evidence representing a line chart configuration, extending the `Chart` base class.
    For detailed line chart options and configuration, see the [Highcharts Line Chart API]
    (https://api.highcharts.com/highcharts/series.line).

    Attributes:
        x_axis (dict): Configuration for the x-axis in the line chart, following Highcharts API.
        y_axis (dict): Configuration for the y-axis in the line chart, following Highcharts API.
        series (list): Data series to be displayed in the line chart, following Highcharts API.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    _TYPE = "line-chart"

    x_axis: dict = {}
    y_axis: dict = {}
    series: List[LineSeries] = []


class BarChart(Chart):
    """
    Evidence representing a bar chart configuration, extending the `Chart` base class.
    For detailed line chart options and configuration, see the [Highcharts Line Chart API]
    (https://api.highcharts.com/highcharts/series.bar).

    Attributes:
        x_axis (dict): Configuration for the x-axis in the line chart, following Highcharts API.
        y_axis (dict): Configuration for the y-axis in the line chart, following Highcharts API.
        series (list): Data series to be displayed in the line chart, following Highcharts API.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    _TYPE = "bar-chart"

    x_axis: dict = {}
    y_axis: dict = {}
    series: List[BarSeries] = []


class Dynacard(Chart):
    """
    Evidence for Dynacard representation. Defaults xAxis for Position(inch) and yAxis for Load(libs).
    This uses line chart configurations, for more details see the [Highcharts Line Chart API]
    (https://api.highcharts.com/highcharts/series.line).

    Attributes:
        series (list): Data series to be displayed in the line chart, following Highcharts API.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    _TYPE = "dynacard"

    series: List[Series] = []


class AggregationTypes(str, Enum):
    none = "none"
    mean = "mean"
    median = "median"
    sum = "sum"
    max = "max"
    min = "min"
    last = "last"
    first = "first"
    count_ = "count"
    distinct = "distinct"
    integral = "integral"
    mode = "mode"
    spread = "spread"
    stddev = "stddev"


class DataExplorerSelector(BaseModel):
    """
    Data selector to define specific resources and aggregations.

    Attributes:
        resource (KRNAssetDataStream | KRNAssetDataStreamDataQuality | KRNAssetDataQuality): The resource to select.
        agg (Optional[AggregationTypes]): The aggregation type to apply.
        time_bucket (Optional[str]): The time bucket of the aggregation.
    """

    resource: Union[KRNAssetDataStream, KRNAssetDataStreamDataQuality, KRNAssetDataQuality]
    agg: Optional[AggregationTypes] = None
    time_bucket: Optional[Annotated[str, StringConstraints(pattern=r"^\d+(ns|us|µs|ms|s|m|h)$")]] = Field(
        default=None,
        description=(
            "Must be a positive integer followed by a valid time unit. "
            'Valid units: "ns", "us" (or "µs"), "ms", "s", "m", "h". '
        ),
    )


class DataExplorer(Evidence):
    """Evidence for Data Explorer representation.

    Attributes:
        title (str): The title of the data explorer.
        start_time (datetime): The start time of the data exploration period.
        end_time (datetime): The end time of the data exploration period.
        selectors (list[DataExplorerSelector]): The data selectors.
    """

    _TYPE = "data-explorer"

    title: str
    start_time: datetime
    end_time: datetime

    selectors: List[DataExplorerSelector]

    @field_serializer("start_time", "end_time")
    def serialize_timestamp(self, ts: datetime) -> str:
        if ts.tzinfo is None:
            ts = ts.astimezone()  # uses local timezone
        return to_rfc3339_timestamp(ts)
