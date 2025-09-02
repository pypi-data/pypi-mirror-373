from datetime import datetime, timedelta
from typing import Optional, Dict, Union

from .Exceptions import InvalidParametersException


class NormalisedAPIParameters:
    """
    An internal helper class to hold logic for checking correctness of parameters.
    """

    def __init__(
        self,
        cpeName: Optional[str] = None,
        cveId: Optional[str] = None,
        cveTag: Optional[str] = None,
        cvssV2Metrics: Optional[str] = None,
        cvssV2Severity: Optional[str] = None,
        cvssV3Metrics: Optional[str] = None,
        cvssV3Severity: Optional[str] = None,
        cvssV4Metrics: Optional[str] = None,
        cvssV4Severity: Optional[str] = None,
        cweId: Optional[str] = None,
        hasCertAlerts: Optional[bool] = False,
        hasCertNotes: Optional[bool] = False,
        hasKev: Optional[bool] = False,
        hasOval: Optional[bool] = False,
        isVulnerable: Optional[bool] = None,
        keywordExactMatch: bool = False,
        keywordSearch: Optional[str] = None,
        lastModStartDate: Optional[Union[str, datetime]] = None,
        lastModEndDate: Optional[Union[str, datetime]] = None,
        noRejected: Optional[bool] = False,
        pubStartDate: Optional[Union[str, datetime]] = None,
        pubEndDate: Optional[Union[str, datetime]] = None,
        resultsPerPage: Optional[int] = 2000,
        startIndex: Optional[int] = None,
        sourceIdentifier: Optional[str] = None,
        versionEnd: Optional[str] = None,
        versionEndType: Optional[str] = None,
        versionStart: Optional[str] = None,
        versionStartType: Optional[str] = None,
        virtualMatchString: Optional[str] = None,
    ):

        if isVulnerable and cpeName is None:
            raise InvalidParametersException(
                "If filtering by isVulnerable, cpeName is required."
            )

        if keywordExactMatch is True and keywordSearch is None:
            raise InvalidParametersException(
                "If filtering by keywordExactMatch, keywordSearch is required."
            )

        # if lastModStartDate or lastModEndDate are specified, ensure both are given.
        if sum([1 for v in (lastModStartDate, lastModEndDate) if v is None]) == 1:
            raise InvalidParametersException(
                "If filtering by the last modified date, both lastModStartDate and lastModEndDate are required."
            )

        if lastModStartDate is not None or lastModEndDate is not None:
            if isinstance(lastModStartDate, str):
                lastModStartDate = datetime.fromisoformat(lastModStartDate)
            if isinstance(lastModEndDate, str):
                lastModEndDate = datetime.fromisoformat(lastModEndDate)
            if lastModEndDate - lastModStartDate > timedelta(days=120):
                raise InvalidParametersException(
                    "The maximum allowable range when using any date range parameters is 120 consecutive days."
                    " This is violated by lastModStartDate/lastModEndDate.\n"
                    f"LastModStartDate: {lastModStartDate.isoformat()}\n"
                    f"LastModEndDate: {lastModEndDate.isoformat()}\n"
                    f"Range: {(lastModEndDate - lastModStartDate).days} days."
                )

        # if pubStartDate or pubEndDate are specified, ensure both are given.
        if sum([1 for v in (pubStartDate, pubEndDate) if v is None]) == 1:
            raise InvalidParametersException(
                "If filtering by the published date, both pubStartDate and pubEndDate are required"
            )

        if lastModStartDate is not None or lastModEndDate is not None:
            if isinstance(pubStartDate, str):
                pubStartDate = datetime.fromisoformat(pubStartDate)
            if isinstance(pubEndDate, str):
                pubEndDate = datetime.fromisoformat(pubEndDate)
            if pubEndDate - pubStartDate > timedelta(days=120):
                raise InvalidParametersException(
                    "The maximum allowable range when using any date range parameters is 120 consecutive days."
                    " This is violated by pubStartDate/pubEndDate.\n"
                    f"pubStartDate: {pubStartDate.isoformat()}\n"
                    f"pubEndDate: {pubEndDate.isoformat()}\n"
                    f"Range: {(pubEndDate - pubStartDate).days} days."
                )

        if resultsPerPage is not None and resultsPerPage > 2000:
            resultsPerPage = 2000

        if startIndex is not None and startIndex < 0:
            raise InvalidParametersException("Cannot search for a negative startIndex.")

        if versionEnd is not None or versionEndType is not None:
            if (
                versionEnd is None
                or versionEndType is None
                or virtualMatchString is None
            ):
                raise InvalidParametersException(
                    "If filtering by the ending version, versionEnd, versionEndType, and virtualMatchString are required."
                )

        if versionStart is not None or versionStartType is not None:
            if (
                versionStart is None
                or versionStartType is None
                or virtualMatchString is None
            ):
                raise InvalidParametersException(
                    "If filtering by the starting version, versionStart, versionStartType, and virtualMatchString are required."
                )

        # Now save all values
        self.cpeName = cpeName
        self.cveId = cveId
        self.cveTag = cveTag
        self.cvssV2Metrics = cvssV2Metrics
        self.cvssV2Severity = cvssV2Severity
        self.cvssV3Metrics = cvssV3Metrics
        self.cveV3Severity = cvssV3Severity
        self.cvssV4Metrics = cvssV4Metrics
        self.cvssV4Severity = cvssV4Severity
        self.cweId = cweId
        self.hasCertAlerts = hasCertAlerts
        self.hasCertNotes = hasCertNotes
        self.hasKev = hasKev
        self.hasOval = hasOval
        self.isVulnerable = isVulnerable
        self.keywordExactMatch = keywordExactMatch
        self.keywordSearch = keywordSearch
        self.lastModStartDate = lastModStartDate
        self.lastModEndDate = lastModEndDate
        self.noRejected = noRejected
        self.pubStartDate = pubStartDate
        self.pubEndDate = pubEndDate
        self.resultsPerPage = resultsPerPage
        self.startIndex = startIndex
        self.sourceIdentifier = sourceIdentifier
        self.versionEnd = versionEnd
        self.versionEndType = versionEndType
        self.versionStart = versionStart
        self.versionStartType = versionStartType
        self.virtualMatchString = virtualMatchString

    def get_all_used_params(self) -> Dict[str, Union[str, bool]]:
        return {k: v for k, v in self.__dict__.items() if v is not None}
