from typing import Literal, Optional

from .BaseCVSSMetric import BaseCVSSMetric


class CVSSMetricV30(BaseCVSSMetric):

    def __init__(
        self,
        attackVector: Optional[str] = None,
        attackComplexity: Optional[str] = None,
        privilegesRequired: Optional[str] = None,
        userInteraction: Optional[str] = None,
        scope: Optional[str] = None,
        confidentialityImpact: Optional[str] = None,
        integrityImpact: Optional[str] = None,
        availabilityImpact: Optional[str] = None,
        baseScore: float = None,
        baseSeverity: Optional[str] = None,
        exploitCodeMaturity: Optional[str] = None,
        remediationLevel: Optional[str] = None,
        reportConfidence: Optional[str] = None,
        temporalScore: Optional[float] = None,
        temporalSeverity: Optional[str] = None,
        confidentialityRequirement: Optional[str] = None,
        integrityRequirement: Optional[str] = None,
        availabilityRequirement: Optional[str] = None,
        modifiedAttackVector: Optional[str] = None,
        modifiedAttackComplexity: Optional[str] = None,
        modifiedPrivilegesRequired: Optional[str] = None,
        modifiedUserInteraction: Optional[str] = None,
        modifiedScope: Optional[str] = None,
        modifiedConfidentialityImpact: Optional[str] = None,
        modifiedIntegrityImpact: Optional[str] = None,
        modifiedAvailabilityImpact: Optional[str] = None,
        environmentalScore: Optional[float] = None,
        environmentalSeverity: Optional[str] = None,
        vectorString: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            attackVector,
            attackComplexity,
            baseScore,
            remediationLevel,
            reportConfidence,
            confidentialityRequirement,
            integrityRequirement,
            availabilityRequirement,
            environmentalScore,
            vectorString,
        )
        self._privilegesRequired = privilegesRequired
        self._userInteraction = userInteraction
        self._scope = scope
        self._confidentialityImpact = confidentialityImpact
        self._integrityImpact = integrityImpact
        self._availabilityImpact = availabilityImpact
        self._baseSeverity = baseSeverity
        self._exploitCodeMaturity = exploitCodeMaturity
        self._temporalScore = temporalScore
        self._temporalSeverity = temporalSeverity
        self._modifiedAttackVector = modifiedAttackVector
        self._modifiedAttackComplexity = modifiedAttackComplexity
        self._modifiedPrivilegesRequired = modifiedPrivilegesRequired
        self._modifiedUserInteraction = modifiedUserInteraction
        self._modifiedScope = modifiedScope
        self._modifiedConfidentialityImpact = modifiedConfidentialityImpact
        self._modifiedIntegrityImpact = modifiedIntegrityImpact
        self._modifiedAvailabilityImpact = modifiedAvailabilityImpact
        self._environmentalSeverity = environmentalSeverity

        self._vector_pattern = "^CVSS:3[.]0/((AV:[NALP]|AC:[LH]|PR:[UNLH]|UI:[NR]|S:[UC]|[CIA]:[NLH]|E:[XUPFH]|RL:[XOTWU]|RC:[XURC]|[CIA]R:[XLMH]|MAV:[XNALP]|MAC:[XLH]|MPR:[XUNLH]|MUI:[XNR]|MS:[XUC]|M[CIA]:[XNLH])/)*(AV:[NALP]|AC:[LH]|PR:[UNLH]|UI:[NR]|S:[UC]|[CIA]:[NLH]|E:[XUPFH]|RL:[XOTWU]|RC:[XURC]|[CIA]R:[XLMH]|MAV:[XNALP]|MAC:[XLH]|MPR:[XUNLH]|MUI:[XNR]|MS:[XUC]|M[CIA]:[XNLH])$"
        self._version = "3.0"

    @property
    def privileges_required(self) -> Optional[Literal["HIGH", "LOW", "NONE"]]:
        return self._privilegesRequired

    @property
    def user_interaction(self) -> Optional[Literal["NONE", "REQUIRED"]]:
        return self._userInteraction

    @property
    def scope(self) -> Optional[Literal["UNCHANGED", "CHANGED"]]:
        return self._scope

    @property
    def confidentiality_impact(self) -> Optional[Literal["NONE", "LOW", "HIGH"]]:
        return self._confidentialityImpact

    @property
    def integrity_impact(self) -> Optional[Literal["NONE", "LOW", "HIGH"]]:
        return self._integrityImpact

    @property
    def availability_impact(self) -> Optional[Literal["NONE", "LOW", "HIGH"]]:
        return self._availabilityImpact

    @property
    def base_severity(self) -> Literal["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        return self._baseSeverity

    @property
    def exploit_code_maturity(
        self,
    ) -> Optional[
        Literal["UNPROVEN", "PROOF_OF_CONCEPT", "FUNCTIONAL", "HIGH", "NOT_DEFINED"]
    ]:
        return self._exploitCodeMaturity

    @property
    def temporal_score(self) -> Optional[float]:
        return self._temporalScore

    @property
    def temporal_severity(
        self,
    ) -> Optional[Literal["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]]:
        return self._temporalSeverity

    @property
    def modified_attack_vector(
        self,
    ) -> Optional[
        Literal["NETWORK", "ADJACENT_NETWORK", "LOCAL", "PHYSICAL", "NOT_DEFINED"]
    ]:
        return self._modifiedAttackVector

    @property
    def modified_attack_complexity(
        self,
    ) -> Optional[Literal["HIGH", "LOW", "NOT_DEFINED"]]:
        return self._modifiedAttackComplexity

    @property
    def modified_privileges_required(
        self,
    ) -> Optional[Literal["HIGH", "LOW", "NONE", "NOT_DEFINED"]]:
        return self._modifiedPrivilegesRequired

    @property
    def modified_user_interaction(
        self,
    ) -> Optional[Literal["NONE", "REQUIRED", "NOT_DEFINED"]]:
        return self._modifiedUserInteraction

    @property
    def modified_scope(
        self,
    ) -> Optional[Literal["UNCHANGED", "CHANGED", "NOT_DEFINED"]]:
        return self._modifiedScope

    @property
    def modified_confidentiality_impact(
        self,
    ) -> Optional[Literal["NONE", "LOW", "HIGH", "NOT_DEFINED"]]:
        return self._modifiedConfidentialityImpact

    @property
    def modified_integrity_impact(
        self,
    ) -> Optional[Literal["NONE", "LOW", "HIGH", "NOT_DEFINED"]]:
        return self._modifiedIntegrityImpact

    @property
    def modified_availability_impact(
        self,
    ) -> Optional[Literal["NONE", "LOW", "HIGH", "NOT_DEFINED"]]:
        return self._modifiedAvailabilityImpact

    @property
    def environmental_severity(
        self,
    ) -> Optional[Literal["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]]:
        return self._environmentalSeverity
