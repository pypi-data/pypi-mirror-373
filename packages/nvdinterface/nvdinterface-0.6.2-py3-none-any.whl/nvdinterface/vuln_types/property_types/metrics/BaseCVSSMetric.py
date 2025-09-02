import re
from typing import Literal, Optional


class BaseCVSSMetric:
    """
    A base class to be inherited from.
    Should not be instantiated by the programmer directly, but rather exists to be subclassed.

    Should contain properties common across all CWE version that may be returned by the NVD API.
    """

    def __init__(
        self,
        attackVector: str,
        attackComplexity: str,
        baseScore: float,
        remediationLevel: str,
        reportConfidence: str,
        confidentialityRequirement: str,
        integrityRequirement: str,
        availabilityRequirement: str,
        environmentalScore: float,
        vectorString: str,
    ):
        self._attackVector = attackVector
        self._attackComplexity = attackComplexity
        self._baseScore = baseScore
        self._remediationLevel = remediationLevel
        self._reportConfidence = reportConfidence
        self._confidentialityRequirement = confidentialityRequirement
        self._integrityRequirement = integrityRequirement
        self._availabilityRequirement = availabilityRequirement
        self._environmentalScore = environmentalScore
        self._vectorString = vectorString

        self._vector_pattern = "^INVALID_PATTERN - OVERWRITE IN SUBCLASS$"

        self._version = None

    @property
    def version(self) -> str:
        if self._version is None:
            raise NotImplementedError(
                "This class has not implemented it's version string - it is likely incomplete."
            )
        return self._version

    @property
    def attack_vector(self) -> Literal["NETWORK", "ADJACENT_NETWORK", "LOCAL"]:
        return self._attackVector

    @property
    def attack_complexity(self) -> Optional[Literal["HIGH", "MEDIUM", "LOW"]]:
        return self._attackComplexity

    @property
    def base_score(self) -> float:
        return self._baseScore

    @property
    def remediation_level(
        self,
    ) -> Optional[
        Literal[
            "OFFICIAL_FIX", "TEMPORARY_FIX", "WORKAROUND", "UNAVAILABLE", "NOT_DEFINED"
        ]
    ]:
        return self._remediationLevel

    @property
    def report_confidence(
        self,
    ) -> Optional[Literal["UNCONFIRMED", "UNCORROBORATED", "CONFIRMED", "NOT_DEFINED"]]:
        return self._reportConfidence

    @property
    def confidentiality_requirement(
        self,
    ) -> Optional[Literal["LOW", "MEDIUM", "HIGH", "NOT_DEFINED"]]:
        return self._confidentialityRequirement

    @property
    def integrity_requirement(
        self,
    ) -> Optional[Literal["LOW", "MEDIUM", "HIGH", "NOT_DEFINED"]]:
        return self._integrityRequirement

    @property
    def availability_requirement(
        self,
    ) -> Optional[Literal["LOW", "MEDIUM", "HIGH", "NOT_DEFINED"]]:
        return self._availabilityRequirement

    @property
    def environmental_score(self) -> Optional[float]:
        return

    @property
    def vector(self) -> str:
        if not re.match(self._vector_pattern, self._vectorString):
            raise ValueError(
                f"Vector string does not match required pattern.\nPattern: {self._vector_pattern}\nVector string: {self._vectorString}"
            )
        return self._vectorString
