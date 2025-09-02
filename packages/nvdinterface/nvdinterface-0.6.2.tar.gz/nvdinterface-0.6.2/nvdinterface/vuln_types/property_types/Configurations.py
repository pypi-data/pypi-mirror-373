from typing import Literal, Optional, List
from uuid import UUID


class CPEMatch:
    """
    CPE match string or range.
    """

    def __init__(
        self,
        vulnerable: bool,
        criteria: str,
        matchCriteriaId: str,
        versionStartExcluding: Optional[str] = None,
        versionStartIncluding: Optional[str] = None,
        versionEndExcluding: Optional[str] = None,
        versionEndIncluding: Optional[str] = None,
    ):
        self.is_vulnerable = vulnerable
        self.criteria = criteria
        if matchCriteriaId is not None:
            self.matchCriteriaId = UUID(matchCriteriaId)
        else:
            self.matchCriteriaId = None
        self.versionStartExcluding = versionStartExcluding
        self.versionStartIncluding = versionStartIncluding
        self.versionEndExcluding = versionEndExcluding
        self.versionEndIncluding = versionEndIncluding


class ConfigurationNode:
    """
    Defines a configuration node in an NVD applicability statement.
    """

    def __init__(
        self,
        operator: Literal["AND", "OR"],
        cpe_matches: List[CPEMatch],
        negate: bool = False,
    ):
        self.operator = operator
        self.cpe_matches = cpe_matches
        self.negate = negate


class Configuration:
    """
    Defines a vulnerable configuration.
    """

    def __init__(
        self,
        nodes: List[ConfigurationNode],
        operator: Optional[Literal["AND", "OR"]],
        negate: bool = False,
    ):
        self.nodes = nodes
        self.operator = operator
        self.negate = negate
