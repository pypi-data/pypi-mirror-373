from __future__ import annotations

from typing import Any, Callable, Dict, Generator, Optional, Type

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing_extensions import Self


class KRN:
    """Kelvin Resource Name representation"""

    _KRN_TYPES: Dict[str, Type[KRN]] = {}
    _NS_ID: Optional[str] = None

    ns_id: str
    ns_string: str

    def __init_subclass__(cls) -> None:
        if cls._NS_ID:
            KRN._KRN_TYPES[cls._NS_ID] = cls

    def __init__(self, ns_id: str, ns_string: str) -> None:
        self.ns_id = ns_id
        self.ns_string = ns_string

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
        yield cls.validate

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            handler(Any),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.encode),
        )

    @classmethod
    def validate(cls, v: Any) -> KRN:
        if isinstance(v, str):
            return cls.from_string(v)

        if isinstance(v, KRN):
            return v

        raise TypeError("Invalid type for KRN. KRN or string required.")

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        return cls(ns_id, ns_string)

    @classmethod
    def from_string(cls, v: str) -> Self:
        try:
            krn, ns_id, ns_string = v.split(":", 2)
        except ValueError:
            raise ValueError("expected format 'krn:<nid>:<nss>'")

        if krn != "krn":
            raise ValueError("expected start by 'krn'")

        T = KRN._KRN_TYPES.get(ns_id, KRN)
        return T.from_krn(ns_id, ns_string)  # type: ignore

    def __eq__(self, other: Any) -> bool:
        return self.ns_id == other.ns_id and self.ns_string == other.ns_string

    def __hash__(self) -> int:
        return hash((self.ns_id, self.ns_string))

    def __str__(self) -> str:
        return f"krn:{self.ns_id}:{self.ns_string}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)})"

    def encode(self) -> str:
        return str(self)


class KRNAsset(KRN):
    _NS_ID: str = "asset"
    """Kelvin Resource Name Asset Metric"""
    asset: str

    def __init__(self, asset: str) -> None:
        super().__init__(self._NS_ID, asset)
        self.asset = asset

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(asset='{self.asset}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        return cls(ns_string)


class KRNAssetMetric(KRN):
    _NS_ID: str = "am"
    """*Deprecated* Kelvin Resource Name Asset Metric"""
    asset: str
    metric: str

    def __init__(self, asset: str, metric: str) -> None:
        super().__init__(KRNAssetDataStream._NS_ID, asset + "/" + metric)
        self.asset = asset
        self.metric = metric

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(asset='{self.asset}', metric='{self.metric}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            asset, metric = ns_string.split("/", 1)
        except ValueError:
            raise ValueError("expected format 'krn:am:<asset>/<metric>'")

        return cls(asset, metric)


class KRNAssetDataStream(KRN):
    _NS_ID: str = "ad"
    """Kelvin Resource Name Asset Data"""
    asset: str
    data_stream: str

    def __init__(self, asset: str, data_stream: str) -> None:
        super().__init__(self._NS_ID, asset + "/" + data_stream)
        self.asset = asset
        self.data_stream = data_stream

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(asset='{self.asset}', data_stream='{self.data_stream}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            asset, data_stream = ns_string.split("/", 1)
        except ValueError:
            raise ValueError("expected format 'krn:am:<asset>/<data_stream>'")

        return cls(asset, data_stream)

    @property
    def data(self) -> str:
        return self.data_stream


class KRNAssetParameter(KRN):
    _NS_ID: str = "ap"
    """Kelvin Resource Name Asset Parameter"""
    asset: str
    parameter: str

    def __init__(self, asset: str, parameter: str) -> None:
        super().__init__(self._NS_ID, asset + "/" + parameter)
        self.asset = asset
        self.parameter = parameter

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(asset='{self.asset}', parameter='{self.parameter}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            asset, parameter = ns_string.split("/", 1)
        except ValueError:
            raise ValueError("expected format 'krn:am:<asset>/<parameter>'")

        return cls(asset, parameter)


class KRNParameter(KRN):
    _NS_ID: str = "param"
    """Kelvin Resource Name Parameter"""
    parameter: str

    def __init__(self, parameter: str) -> None:
        super().__init__(self._NS_ID, parameter)
        self.parameter = parameter

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(parameter='{self.parameter}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        return cls(ns_string)


class KRNWorkload(KRN):
    _NS_ID: str = "wl"
    """Kelvin Resource Name Workload"""
    node: str
    workload: str

    def __init__(self, node: str, workload: str) -> None:
        super().__init__(self._NS_ID, node + "/" + workload)
        self.node = node
        self.workload = workload

    @property
    def node_name(self) -> str:
        "Backwards compatibility"
        return self.node

    @property
    def workload_name(self) -> str:
        "Backwards compatibility"
        return self.workload

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(node='{self.node}', workload='{self.workload}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            node, workload = ns_string.split("/", 1)
        except ValueError:
            raise ValueError("expected format 'krn:wl:<node>/<workload>'")

        return cls(node, workload)


class KRNWorkloadAppVersion(KRN):
    _NS_ID: str = "wlappv"
    """Kelvin Resource Name Workload App"""
    node: str
    workload: str
    app: str
    version: str

    def __init__(self, node: str, workload: str, app: str, version: str) -> None:
        super().__init__(self._NS_ID, node + "/" + workload + ":" + app + "/" + version)
        self.node = node
        self.workload = workload
        self.app = app
        self.version = version

    @property
    def node_name(self) -> str:
        "Backwards compatibility"
        return self.node

    @property
    def workload_name(self) -> str:
        "Backwards compatibility"
        return self.workload

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(node='{self.node}', workload='{self.workload}', "
            f"app='{self.app}, version='{self.version}')"
        )

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            node_workload, app_version = ns_string.split(":", 1)
            node, workload = node_workload.split("/", 1)
            app, version = app_version.split("/", 1)
        except ValueError:
            raise ValueError("expected format 'krn:wl:<node>/<workload>:<app>/<version>'")

        return cls(node, workload, app, version)


class KRNRecommendation(KRN):
    _NS_ID: str = "recommendation"
    """Kelvin Resource Name Recommendation"""
    recommendation_id: str

    def __init__(self, recommendation_id: str) -> None:
        super().__init__(self._NS_ID, recommendation_id)
        self.recommendation_id = recommendation_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(recommendation_id='{self.recommendation_id}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        return cls(ns_string)


class KRNAppVersion(KRN):
    _NS_ID: str = "appversion"
    """Kelvin Resource Name Recommendation"""

    app: str
    version: str

    def __init__(self, app: str, version: str) -> None:
        super().__init__(self._NS_ID, app + "/" + version)
        self.app = app
        self.version = version

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(app='{self.app}, version={self.version}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            app, version = ns_string.split("/", 1)
        except ValueError:
            raise ValueError(f"expected format 'krn:{cls._NS_ID}:<app>/<version>'")

        return cls(app, version)


class KRNApp(KRN):
    _NS_ID: str = "app"
    """Kelvin Resource Name Application"""

    app: str

    def __init__(self, app: str) -> None:
        super().__init__(self._NS_ID, app)
        self.app = app

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(app='{self.app}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        return cls(ns_string)


class KRNDatastream(KRN):
    _NS_ID: str = "datastream"
    """Kelvin Resource Name Datastream"""

    datastream: str

    def __init__(self, datastream: str) -> None:
        super().__init__(self._NS_ID, datastream)
        self.datastream = datastream

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(datastream='{self.datastream}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        return cls(ns_string)


class KRNUser(KRN):
    _NS_ID: str = "user"
    """Kelvin Resource Name User"""

    user: str

    def __init__(self, user: str) -> None:
        super().__init__(self._NS_ID, user)
        self.user = user

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(user='{self.user}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        return cls(ns_string)


class KRNServiceAccount(KRN):
    _NS_ID: str = "srv-acc"
    """Kelvin Resource Name Service Account"""

    service_account: str

    def __init__(self, service_account: str) -> None:
        super().__init__(self._NS_ID, service_account)
        self.service_account = service_account

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(service_account='{self.service_account}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        return cls(ns_string)


class KRNJob(KRN):
    _NS_ID: str = "job"
    """Kelvin Resource Name Job"""

    job: str
    job_run_id: str

    def __init__(self, job: str, job_run_id: str) -> None:
        super().__init__(self._NS_ID, job + "/" + job_run_id)
        self.job = job
        self.job_run_id = job_run_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(job='{self.job}, version={self.job_run_id}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            job, job_run_id = ns_string.split("/", 1)
        except ValueError:
            raise ValueError(f"expected format 'krn:{cls._NS_ID}:<job>/<job_run_id>'")

        return cls(job, job_run_id)


class KRNSchedule(KRN):
    _NS_ID: str = "schedule"
    """Kelvin Resource Name Schedule"""

    schedule: str

    def __init__(self, schedule: str) -> None:
        super().__init__(self._NS_ID, schedule)
        self.schedule = schedule

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(schedule='{self.schedule}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")
        return cls(ns_string)


class KRNAssetDataQuality(KRN):
    _NS_ID: str = "dqasset"
    """Kelvin Resource Name Asset DataQuality
    eg: krn:dqasset:score:pcp_01
    """

    asset: str
    data_quality: str

    def __init__(self, asset: str, data_quality: str) -> None:
        super().__init__(self._NS_ID, data_quality + ":" + asset)
        self.asset = asset
        self.data_quality = data_quality

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(asset='{self.asset}', data_quality='{self.data_quality}')"

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            data_quality, asset = ns_string.split(":", 1)
        except ValueError:
            raise ValueError("expected format 'krn:dqasset:<data_quality>:<asset>'")

        return cls(asset, data_quality)


class KRNAssetDataStreamDataQuality(KRN):
    _NS_ID: str = "dqad"
    """Kelvin Resource Name Asset DataStream DataQuality
    eg: krn:dqad:timestamp_anomaly:pcp_01/gas_flow
    """

    asset: str
    data_stream: str
    data_quality: str

    def __init__(self, asset: str, data_stream: str, data_quality: str) -> None:
        super().__init__(self._NS_ID, data_quality + ":" + asset + "/" + data_stream)
        self.asset = asset
        self.data_stream = data_stream
        self.data_quality = data_quality

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"asset='{self.asset}', "
            f"data_stream='{self.data_stream}', "
            f"data_quality='{self.data_quality}'"
            f")"
        )

    @classmethod
    def from_krn(cls, ns_id: str, ns_string: str) -> Self:
        if ns_id != cls._NS_ID:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._NS_ID}, got {ns_id}")

        try:
            data_quality, ad = ns_string.split(":", 1)
            asset, data_stream = ad.split("/", 1)
        except ValueError:
            raise ValueError("expected format 'krn:dqad:<data_quality>:<asset>/<data_stream>'")

        return cls(asset, data_stream, data_quality)
