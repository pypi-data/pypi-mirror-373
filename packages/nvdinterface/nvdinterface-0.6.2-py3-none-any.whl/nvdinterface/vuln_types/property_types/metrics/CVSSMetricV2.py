import re
from typing import Literal, Optional

from .BaseCVSSMetric import BaseCVSSMetric


class CVSSMetricV2(BaseCVSSMetric):

    def __init__(
        self,
        accessVector: Optional[str] = None,
        accessComplexity: Optional[str] = None,
        authentication: Optional[str] = None,
        confidentialityImpact: Optional[str] = None,
        integrityImpact: Optional[str] = None,
        availabilityImpact: Optional[str] = None,
        baseScore: Optional[float] = None,
        exploitability: Optional[str] = None,
        remediationLevel: Optional[str] = None,
        reportConfidence: Optional[str] = None,
        temporalScore: Optional[float] = None,
        collateralDamagepotential: Optional[str] = None,
        targetDistribution: Optional[str] = None,
        confidentialityRequirement: Optional[str] = None,
        integrityRequirement: Optional[str] = None,
        availabilityRequirement: Optional[str] = None,
        environmentalScore: Optional[float] = None,
        vectorString: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            accessVector,
            accessComplexity,
            baseScore,
            remediationLevel,
            reportConfidence,
            confidentialityRequirement,
            integrityRequirement,
            availabilityRequirement,
            environmentalScore,
            vectorString,
        )
        self._authentication = authentication
        self._confidentialityImpact = confidentialityImpact
        self._integrityImpact = integrityImpact
        self._availabilityImpact = availabilityImpact
        self._exploitability = exploitability
        self._temporalScore = temporalScore
        self._collateralDamagepotential = collateralDamagepotential
        self._targetDistribution = targetDistribution
        self._environmentalScore = environmentalScore
        self._vectorString = vectorString

        self._vector_pattern = "^((AV:[NAL]|AC:[LMH]|Au:[MSN]|[CIA]:[NPC]|E:(U|POC|F|H|ND)|RL:(OF|TF|W|U|ND)|RC:(UC|UR|C|ND)|CDP:(N|L|LM|MH|H|ND)|TD:(N|L|M|H|ND)|[CIA]R:(L|M|H|ND))/)*(AV:[NAL]|AC:[LMH]|Au:[MSN]|[CIA]:[NPC]|E:(U|POC|F|H|ND)|RL:(OF|TF|W|U|ND)|RC:(UC|UR|C|ND)|CDP:(N|L|LM|MH|H|ND)|TD:(N|L|M|H|ND)|[CIA]R:(L|M|H|ND))$"
        self._version = "2.0"

    @property
    def access_vector(
        self,
    ) -> Optional[Literal["NETWORK", "ADJACENT_NETWORK", "LOCAL"]]:
        return self.attack_vector

    @property
    def access_complexity(self) -> Optional[Literal["HIGH", "MEDIUM", "LOW"]]:
        return self.attack_complexity

    @property
    def authentication(self) -> Optional[Literal["MULTIPLE", "SINGLE", "NONE"]]:
        return self._authentication

    @property
    def confidentiality_impact(
        self,
    ) -> Optional[Literal["NONE", "PARTIAL", "COMPLETE"]]:
        return self._confidentialityImpact

    @property
    def integrity_impact(self) -> Optional[Literal["NONE", "PARTIAL", "COMPLETE"]]:
        return self._integrityImpact

    @property
    def availability_impact(self) -> Optional[Literal["NONE", "PARTIAL", "COMPLETE"]]:
        return self._availabilityImpact

    @property
    def base_score(self) -> Optional[float]:
        return self._baseScore

    @property
    def exploitability(
        self,
    ) -> Optional[
        Literal["UNPROVEN", "PROOF_OF_CONCEPT", "FUNCTIONAL", "HIGH", "NOT_DEFINED"]
    ]:
        return self._exploitability

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
    def temporal_score(self) -> Optional[float]:
        return self._temporalScore

    @property
    def collateral_damage_potential(self):
        return self._collateralDamagepotential

    @property
    def target_distribution(
        self,
    ) -> Optional[Literal["NONE", "LOW", "MEDIUM", "HIGH", "NOT_DEFINED"]]:
        return self._targetDistribution

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
    def environment_score(self) -> float:
        return self._environmentalScore

    @property
    def vector(self) -> str:
        if not re.match(self._vector_pattern, self._vectorString):
            raise ValueError(
                f"Vector string does not match required pattern.\nPattern: {self._vector_pattern}\nVector string: {self._vectorString}"
            )
        return self._vectorString
