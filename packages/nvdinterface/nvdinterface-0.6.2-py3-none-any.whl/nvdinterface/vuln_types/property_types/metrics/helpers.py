from typing import Any, Dict, Union

from . import CVSSMetricV2, CVSSMetricV30, CVSSMetricV31, CVSSMetricV40


def build_from_api_response(
    d: Dict[str, Any],
) -> Union[CVSSMetricV2, CVSSMetricV30, CVSSMetricV31, CVSSMetricV40]:
    dat = d.copy()
    for k, v in d.get("cvssData", {}).items():
        dat[k] = v
    dat.pop("cvssData")

    if dat.get("version") == "2.0":
        t = CVSSMetricV2
    elif dat.get("version") == "3.0":
        t = CVSSMetricV30
    elif dat.get("version") == "3.1":
        t = CVSSMetricV31
    elif dat.get("version") == "4.0":
        t = CVSSMetricV40
    else:
        raise ValueError(
            f"Could not find a valid version for the CVSS metric.\ndata:\n{dat}"
        )

    return t(**dat)
