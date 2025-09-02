from datetime import datetime, date
from typing import Optional, List, Dict, Literal, Union

from . import (
    BaseCVSSMetric,
    CVSSMetricV40,
    CVSSMetricV31,
    CVSSMetricV2,
    CVSSMetricV30,
    Weakness,
    Configuration,
    VendorComment,
    Description,
    Reference,
)

# ref https://csrc.nist.gov/schema/nvd/api/2.0/cve_api_json_2.0.schema
_valid_cve_props = (
    "id",
    "sourceIdentifier",
    "vulnStatus",
    "published",
    "lastModified",
    "evaluatorComment",
    "evaluatorSolution",
    "evaluatorImpact",
    "cisaExploitAdd",
    "cisaActionDue",
    "cisaRequiredAction",
    "cisaVulnerabilityName",
    "cveTags",
    "descriptions",
    "references",
    "metrics",
    "weaknesses",
    "configurations",
    "vendorComments",
)


class CVE:
    """
    Represents details for a specific CVE.
    """

    def __init__(self, *args, **kwargs):
        """
        Pass a dictionary of key, value pairs. If these are valid keys, they will be set as properties.
        """
        # handle common errors
        if isinstance(args, dict) and kwargs == {}:
            dat = args
        elif (
            isinstance(args, tuple)
            and len(args) == 1
            and isinstance(args[0], dict)
            and kwargs == {}
        ):
            dat = args[0]
        else:
            dat = kwargs
        for k, v in dat.items():
            if k not in _valid_cve_props:
                raise ValueError(
                    f"'{k}' is not a valid property for a CVE object.\n"
                    f"It must be one of {_valid_cve_props}"
                )
            setattr(self, k, v)

    @property
    def id_str(self) -> str:
        return self.id

    @property
    def source_identifier(self) -> Optional[str]:
        if hasattr(self, "sourceIdentifier"):
            return self.sourceIdentifier
        return None

    @property
    def vuln_status(self) -> Optional[str]:
        if hasattr(self, "vulnStatus"):
            return self.vulnStatus
        return None

    @property
    def published_str(self) -> str:
        return self.published

    @property
    def published_datetime(self) -> datetime:
        return datetime.fromisoformat(self.published_str)

    @property
    def last_modified_str(self) -> str:
        return self.lastModified

    @property
    def last_modified_datetime(self) -> datetime:
        return datetime.fromisoformat(self.last_modified_str)

    @property
    def evaluator_comment(self) -> Optional[str]:
        if hasattr(self, "evaluatorComment"):
            return self.evaluatorComment
        return None

    @property
    def evaluator_solution(self) -> Optional[str]:
        if hasattr(self, "evaluatorSolution"):
            return self.evaluatorSolution
        return None

    @property
    def evaluator_impact(self) -> Optional[str]:
        if hasattr(self, "evaluatorImpact"):
            return self.evaluatorImpact
        return None

    @property
    def cisa_exploit_added_date_str(self) -> Optional[str]:
        if hasattr(self, "cisaExploitAdd"):
            return self.cisaExploitAdd
        return None

    @property
    def cisa_exploit_added_date(self) -> Optional[date]:
        s = self.cisa_exploit_added_date_str
        if s is not None:
            return date.fromisoformat(self.cisa_exploit_added_date_str)
        return None

    @property
    def cisa_action_due_date_str(self) -> Optional[str]:
        if hasattr(self, "cisaActionDue"):
            return self.cisaActionDue
        return None

    @property
    def cisa_action_due_date(self):
        s = self.cisa_action_due_date_str
        if s is not None:
            return date.fromisoformat(s)
        return None

    @property
    def cisa_required_action(self) -> Optional[str]:
        if hasattr(self, "cisaRequiredAction"):
            return self.cisaRequiredAction
        return None

    @property
    def cisa_vulnerability_name(self) -> Optional[str]:
        if hasattr(self, "cisaVulnerabilityName"):
            return self.cisaVulnerabilityName
        return None

    @property
    def cve_tags(
        self,
    ) -> Optional[
        List[
            Dict[
                str,
                Union[
                    str,
                    List[
                        Literal[
                            "unsupported-when-assigned",
                            "exclusively-hosted-service",
                            "disputed",
                        ]
                    ],
                ],
            ]
        ]
    ]:
        if hasattr(self, "cveTags"):
            return self.cveTags
        return None

    @property
    def descriptions_list(self) -> List[Description]:
        return [
            Description(lang=desc.get("lang"), value=desc.get("value"))
            for desc in self.descriptions
        ]

    @property
    def references_list(self) -> List[Reference]:
        return [
            Reference(
                source=ref.get("source"),
                tags=ref.get("tags"),
                url=ref.get("url"),
            )
            for ref in self.references
        ]

    @property
    def metrics_list(self) -> List[BaseCVSSMetric]:
        metrics = []
        for m in self.metrics.get("cvssMetricV40", []):
            metrics.append(CVSSMetricV40(m))
        for m in self.metrics.get("cvssMetricV31", []):
            metrics.append(CVSSMetricV31(m))
        for m in self.metrics.get("cvssMetricV30", []):
            metrics.append(CVSSMetricV30(m))
        for m in self.metrics.get("cvssMetricV2", []):
            metrics.append(CVSSMetricV2(m))

        return metrics

    @property
    def weaknesses_list(self) -> List[Weakness]:
        return [
            Weakness(elem.get("source", {}), elem.get("type"), elem.get("description"))
            for elem in self.weaknesses
        ]

    @property
    def configurations_list(self) -> Optional[List[Configuration]]:
        if hasattr(self, "configurations"):
            return [Configuration(elem) for elem in self.configurations]
        return None

    @property
    def vendor_comment_list(self) -> List[VendorComment]:
        if hasattr(self, "vendorComments"):
            return [VendorComment(elem) for elem in self.vendorComments]
        return None
