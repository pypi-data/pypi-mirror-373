import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

import requests

from .internal import NormalisedAPIParameters
from .internal.Exceptions import InvalidParametersException
from .vuln_types import CVE
from .vuln_types.property_types.ChangeItem import ChangeItem

_url_base = "https://services.nvd.nist.gov/rest/json"


def _get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    api_version: str = "2.0",
) -> Any:
    """
    Helper method for building and making GET requests.
    Intentionally does not perform any sort of error handling
    so that the programmer is forced to be aware of errors.

    :param endpoint: The API endpoint to send the request to. For example, "/cves/2.0".
    :param params: An optional Dict of key/value pairs to be sent as GET parameters
    :return: A JSON object returned by the remote API.
    """

    resp = requests.get(
        f"{_url_base}{endpoint}/{api_version}",
        params=params,
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


def search_cves(
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
    hasCertAlerts: Optional[bool] = None,
    hasCertNotes: Optional[bool] = None,
    hasKev: Optional[bool] = None,
    hasOval: Optional[bool] = None,
    isVulnerable: Optional[bool] = None,
    keywordExactMatch: Optional[bool] = None,
    keywordSearch: Optional[str] = None,
    lastModStartDate: Optional[Union[str, datetime]] = None,
    lastModEndDate: Optional[Union[str, datetime]] = None,
    noRejected: Optional[bool] = None,
    pubStartDate: Optional[Union[str, datetime]] = None,
    pubEndDate: Optional[Union[str, datetime]] = None,
    resultsPerPage: int = 2000,
    startIndex: int = 0,
    sourceIdentifier: Optional[str] = None,
    versionEnd: Optional[str] = None,
    versionEndType: Optional[str] = None,
    versionStart: Optional[str] = None,
    versionStartType: Optional[str] = None,
    virtualMatchString: Optional[str] = None,
    nvdApiKey: Optional[str] = None,
    raw_json_response: bool = False,
) -> Dict[str, Any]:
    """
    Search the NVD CVE API for results matching query terms.
    This method enforces some 'sensible' limits for certain parameters, as noted per parameter.

    :param cpeName: This value is compared against the CPE Match Criteria within a CVE applicability statement.
    :param cveId: A specific vulnerability identified by its unique Common Vulnerabilities and Exposures identifier (the CVE ID).
    :param cveTag: A specific CVE Tag to search for. E.g. 'disputed'.
    :param cvssV2Metrics: Either full or partial vector strings may be used. This parameter cannot be used in requests that include cvssV3Metrics or cvssv4Metrics.
    :param cvssV2Severity: A specific CVSSv2 qualitative severity rating to search for. This parameter cannot be used in requests that include cvssV3Severity or cvssv4Severity.
    :param cvssV3Metrics: Either full or partial vector strings may be used. This parameter cannot be used in requests that include cvssV2Metrics or cvssv4Metrics.
    :param cvssV3Severity: A specific CVSSv3 qualitative severity rating to search for. This parameter cannot be used in requests that include cvssV2Severity or cvssv4Severity.
    :param cvssV4Metrics: Either full or partial vector strings may be used. This parameter cannot be used in requests that include cvssV2Metrics or cvssv3Metrics.
    :param cvssV4Severity: A specific CVSSv4 qualitative severity rating to search for. This parameter cannot be used in requests that include cvssV2Severity or cvssv3Severity.
    :param cweId: This parameter returns only the CVE that include a weakness identified by Common Weakness Enumeration using the provided {CWE-ID}.
    :param hasCertAlerts: This parameter returns only CVE's that contain a Technical Alert from US-CERT.
    :param hasCertNotes: This parameter returns CVE's that contain a Vulnerability Note from CERT/CC.
    :param hasKev: This parameter returns CVE's that appear in CISA's Known Exploited Vulnerabilities (KEV) Catalog.
    :param hasOval: This parameter returns CVE's that contain information from MITRE's Open Vulnerability and Assessment Language (OVAL) before this transitioned to the Center for Internet Security (CIS).
    :param isVulnerable: This parameter returns CVE's associated with a specific CPE, where the CPE is also considered vulnerable.
    :param keywordExactMatch: If the value of keywordSearch is a phrase, i.e., contains more than one term, including keywordExactMatch returns only the CVEs matching the phrase exactly. Otherwise, the results will contain records having any of the terms.
    :param keywordSearch: This parameter returns only the CVEs where a word or phrase is found in the current description.
    :param lastModStartDate: return only the CVEs that were last modified during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param lastModEndDate: return only the CVEs that were last modified during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param noRejected: This parameter excludes CVE records with the REJECT or Rejected status from API response.
    :param pubStartDate: These parameters return only the CVEs that were added to the NVD (i.e., published) during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param pubEndDate: These parameters return only the CVEs that were added to the NVD (i.e., published) during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param resultsPerPage: This parameter specifies the maximum number of CVE records to be returned in a single API response. For network considerations, the default value and maximum allowable limit is 2,000.
    :param startIndex: This parameter specifies the index of the first CVE to be returned in the response data. The index is zero-based, meaning the first CVE is at index zero.
    :param sourceIdentifier: CVE's where the exact value of `sourceIdentifier` appears as a data source in the CVE record.
    :param versionEnd: The virtualMatchString parameter may be combined with versionEnd and versionEndType to return only the CVEs associated with CPEs in specific version ranges.
    :param versionEndType: The virtualMatchString parameter may be combined with versionEnd and versionEndType to return only the CVEs associated with CPEs in specific version ranges.
    :param versionStart: The virtualMatchString parameter may be combined with versionStart and versionStartType to return only the CVEs associated with CPEs in specific version ranges.
    :param versionStartType: The virtualMatchString parameter may be combined with versionStart and versionStartType to return only the CVEs associated with CPEs in specific version ranges.
    :param virtualMatchString: This parameter filters CVE more broadly than cpeName. The exact value of `cpe match string` is compared against the CPE Match Criteria present on CVE applicability statements.
    :param nvdApiKey: Your API key for the NVD API.
    :param raw_json_response: Whether the resulting objects returned from the API should be converted to CVE objects. Otherwise they are left as JSON.
    :return: The CVE API returns seven primary objects in the body of the response: resultsPerPage, startIndex, totalResults, format, version, timestamp, and vulnerabilities.
    """

    params = NormalisedAPIParameters(
        cpeName,
        cveId,
        cveTag,
        cvssV2Metrics,
        cvssV2Severity,
        cvssV3Metrics,
        cvssV3Severity,
        cvssV4Metrics,
        cvssV4Severity,
        cweId,
        hasCertAlerts,
        hasCertNotes,
        hasKev,
        hasOval,
        isVulnerable,
        keywordExactMatch,
        keywordSearch,
        lastModStartDate,
        lastModEndDate,
        noRejected,
        pubStartDate,
        pubEndDate,
        resultsPerPage,
        startIndex,
        sourceIdentifier,
        versionEnd,
        versionEndType,
        versionStart,
        versionStartType,
        virtualMatchString,
    ).get_all_used_params()

    res = _get("/cves", params=params, headers={"nvdApiKey": nvdApiKey})

    if not raw_json_response:
        res["vulnerabilities"] = [
            CVE(elem.get("cve", {})) for elem in res.get("vulnerabilities", [])
        ]

    return res


def search_cves_all(
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
    hasCertAlerts: Optional[bool] = None,
    hasCertNotes: Optional[bool] = None,
    hasKev: Optional[bool] = None,
    hasOval: Optional[bool] = None,
    isVulnerable: Optional[bool] = None,
    keywordExactMatch: Optional[bool] = None,
    keywordSearch: Optional[str] = None,
    lastModStartDate: Optional[Union[str, datetime]] = None,
    lastModEndDate: Optional[Union[str, datetime]] = None,
    noRejected: Optional[bool] = None,
    pubStartDate: Optional[Union[str, datetime]] = None,
    pubEndDate: Optional[Union[str, datetime]] = None,
    sourceIdentifier: Optional[str] = None,
    versionEnd: Optional[str] = None,
    versionEndType: Optional[str] = None,
    versionStart: Optional[str] = None,
    versionStartType: Optional[str] = None,
    virtualMatchString: Optional[str] = None,
    nvdApiKey: Optional[str] = None,
    sleep_seconds_between_requests: Optional[int] = 6,
    raw_json_response: bool = False,
) -> Union[List[CVE], List[Dict[str, Any]]]:
    """
    Search the NVD CVE API for all results matching query terms.

    :param cpeName: This value is compared against the CPE Match Criteria within a CVE applicability statement.
    :param cveId: A specific vulnerability identified by its unique Common Vulnerabilities and Exposures identifier (the CVE ID).
    :param cveTag: A specific CVE Tag to search for. E.g. 'disputed'.
    :param cvssV2Metrics: Either full or partial vector strings may be used. This parameter cannot be used in requests that include cvssV3Metrics or cvssv4Metrics.
    :param cvssV2Severity: A specific CVSSv2 qualitative severity rating to search for. This parameter cannot be used in requests that include cvssV3Severity or cvssv4Severity.
    :param cvssV3Metrics: Either full or partial vector strings may be used. This parameter cannot be used in requests that include cvssV2Metrics or cvssv4Metrics.
    :param cvssV3Severity: A specific CVSSv3 qualitative severity rating to search for. This parameter cannot be used in requests that include cvssV2Severity or cvssv4Severity.
    :param cvssV4Metrics: Either full or partial vector strings may be used. This parameter cannot be used in requests that include cvssV2Metrics or cvssv3Metrics.
    :param cvssV4Severity: A specific CVSSv4 qualitative severity rating to search for. This parameter cannot be used in requests that include cvssV2Severity or cvssv3Severity.
    :param cweId: This parameter returns only the CVE that include a weakness identified by Common Weakness Enumeration using the provided {CWE-ID}.
    :param hasCertAlerts: This parameter returns only CVE's that contain a Technical Alert from US-CERT.
    :param hasCertNotes: This parameter returns CVE's that contain a Vulnerability Note from CERT/CC.
    :param hasKev: This parameter returns CVE's that appear in CISA's Known Exploited Vulnerabilities (KEV) Catalog.
    :param hasOval: This parameter returns CVE's that contain information from MITRE's Open Vulnerability and Assessment Language (OVAL) before this transitioned to the Center for Internet Security (CIS).
    :param isVulnerable: This parameter returns CVE's associated with a specific CPE, where the CPE is also considered vulnerable.
    :param keywordExactMatch: If the value of keywordSearch is a phrase, i.e., contains more than one term, including keywordExactMatch returns only the CVEs matching the phrase exactly. Otherwise, the results will contain records having any of the terms.
    :param keywordSearch: This parameter returns only the CVEs where a word or phrase is found in the current description.
    :param lastModStartDate: return only the CVEs that were last modified during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param lastModEndDate: return only the CVEs that were last modified during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param noRejected: This parameter excludes CVE records with the REJECT or Rejected status from API response.
    :param pubStartDate: These parameters return only the CVEs that were added to the NVD (i.e., published) during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param pubEndDate: These parameters return only the CVEs that were added to the NVD (i.e., published) during the specified period. Either a datetime.datetime object, or a string in ISO format.
    :param sourceIdentifier: CVE's where the exact value of `sourceIdentifier` appears as a data source in the CVE record.
    :param versionEnd: The virtualMatchString parameter may be combined with versionEnd and versionEndType to return only the CVEs associated with CPEs in specific version ranges.
    :param versionEndType: The virtualMatchString parameter may be combined with versionEnd and versionEndType to return only the CVEs associated with CPEs in specific version ranges.
    :param versionStart: The virtualMatchString parameter may be combined with versionStart and versionStartType to return only the CVEs associated with CPEs in specific version ranges.
    :param versionStartType: The virtualMatchString parameter may be combined with versionStart and versionStartType to return only the CVEs associated with CPEs in specific version ranges.
    :param virtualMatchString: This parameter filters CVE more broadly than cpeName. The exact value of `cpe match string` is compared against the CPE Match Criteria present on CVE applicability statements.
    :param nvdApiKey: Your API key for the NVD API.
    :param sleep_seconds_between_requests: The numebr of seconds to sleep between API requests. If an API key is not provided, a minumum value of 6 is enforced.
    :param raw_json_response: Whether the resulting objects returned from the API should be converted to CVE objects. Otherwise they are left as JSON.
    :return: The CVE API returns seven primary objects in the body of the response: resultsPerPage, startIndex, totalResults, format, version, timestamp, and vulnerabilities.
    """
    if nvdApiKey is None and sleep_seconds_between_requests < 6:
        sleep_seconds_between_requests = 6

    resp = search_cves(
        cpeName=cpeName,
        cveId=cveId,
        cveTag=cveTag,
        cvssV2Metrics=cvssV2Metrics,
        cvssV2Severity=cvssV2Severity,
        cvssV3Metrics=cvssV3Metrics,
        cvssV3Severity=cvssV3Severity,
        cvssV4Metrics=cvssV4Metrics,
        cvssV4Severity=cvssV4Severity,
        cweId=cweId,
        hasCertAlerts=hasCertAlerts,
        hasCertNotes=hasCertNotes,
        hasKev=hasKev,
        hasOval=hasOval,
        isVulnerable=isVulnerable,
        keywordExactMatch=keywordExactMatch,
        keywordSearch=keywordSearch,
        lastModStartDate=lastModStartDate,
        lastModEndDate=lastModEndDate,
        noRejected=noRejected,
        pubStartDate=pubStartDate,
        pubEndDate=pubEndDate,
        sourceIdentifier=sourceIdentifier,
        versionEnd=versionEnd,
        versionEndType=versionEndType,
        versionStart=versionStart,
        versionStartType=versionStartType,
        virtualMatchString=virtualMatchString,
        nvdApiKey=nvdApiKey,
        raw_json_response=raw_json_response,
    )

    vulns = []
    while resp.get("totalResults", 0) > resp.get("resultsPerPage", 0) * resp.get(
        "startIndex", 0
    ) + resp.get("resultsPerPage", 0):
        vulns += resp.get("vulnerabilities", [])
        time.sleep(sleep_seconds_between_requests)
        resp = search_cves(
            cpeName=cpeName,
            cveId=cveId,
            cveTag=cveTag,
            cvssV2Metrics=cvssV2Metrics,
            cvssV2Severity=cvssV2Severity,
            cvssV3Metrics=cvssV3Metrics,
            cvssV3Severity=cvssV3Severity,
            cvssV4Metrics=cvssV4Metrics,
            cvssV4Severity=cvssV4Severity,
            cweId=cweId,
            hasCertAlerts=hasCertAlerts,
            hasCertNotes=hasCertNotes,
            hasKev=hasKev,
            hasOval=hasOval,
            isVulnerable=isVulnerable,
            keywordExactMatch=keywordExactMatch,
            keywordSearch=keywordSearch,
            lastModStartDate=lastModStartDate,
            lastModEndDate=lastModEndDate,
            noRejected=noRejected,
            pubStartDate=pubStartDate,
            pubEndDate=pubEndDate,
            sourceIdentifier=sourceIdentifier,
            versionEnd=versionEnd,
            versionEndType=versionEndType,
            versionStart=versionStart,
            versionStartType=versionStartType,
            virtualMatchString=virtualMatchString,
            raw_json_response=raw_json_response,
        )

    vulns += resp.get("vulnerabilities", [])

    return vulns


def cve_history(
    changeStartDate: Optional[Union[str, datetime]] = None,
    changeEndDate: Optional[Union[str, datetime]] = None,
    cveId: Optional[str] = None,
    eventName: Optional[str] = None,
    resultsPerPage: int = 5000,
    startIndex: int = 0,
    nvdApiKey: Optional[str] = None,
    raw_json_response: bool = False,
) -> Dict[
    str,
    Union[int, str, List[Dict[str, Dict[str, Union[str, List[Dict[str, str]]]]]]],
]:
    """
    Paginated query for changes to the NVD database matching the relevant parameters.

    :param changeStartDate: Search from this date for the change. If filtering by the change date, both changeStartDate and changeEndDate are required.
    :param changeEndDate: Search until this date for the change. If filtering by the change date, both changeStartDate and changeEndDate are required.
    :param cveId: The complete change history for a specific vulnerability identified by its unique Common Vulnerabilities and Exposures identifier (the CVE ID).
    :param eventName: This parameter returns all CVE associated with a **single** specific type of change event.
    :param resultsPerPage: The number of results to return per page (default 5000).
    :param startIndex: The index of the first page to return from (default 0).
    :param nvdApiKey: Your API key for the NVD API.
    :param raw_json_response: If true, will return raw JSON response instead of converting to local classes.
    :return: A list of results that were returned from the NVD API matching the criteria.
    """

    if sum([1 for p in (changeStartDate, changeEndDate) if p is not None]) == 1:
        raise InvalidParametersException(
            "If filtering by the change date, both changeStartDate and changeEndDate are required."
        )

    if resultsPerPage > 5000:
        raise InvalidParametersException(
            "The maximum allowable limit for resultsPerPage parameter is 5000"
        )

    if startIndex < 0:
        raise InvalidParametersException(
            "startIndex parameter must be a non-negative integer."
        )

    params = {
        "startIndex": startIndex,
        "resultsPerPage": resultsPerPage,
    }

    if changeStartDate is not None:
        params["startDate"] = changeStartDate
    if changeEndDate is not None:
        params["endDate"] = changeEndDate
    if cveId is not None:
        params["cveId"] = cveId
    if eventName is not None:
        params["eventName"] = eventName

    res = _get("/cvehistory", params=params, headers={"nvdApiKey": nvdApiKey})

    if not raw_json_response:
        res["cveChanges"] = [
            ChangeItem(
                elem.get("change", {}).get("cveId"),
                elem.get("change", {}).get("eventName"),
                elem.get("change", {}).get("cveChangeId"),
                elem.get("change", {}).get("sourceIdentifier"),
                elem.get("change", {}).get("created"),
                elem.get("change", {}).get("details"),
            )
            for elem in res.get("cveChanges", [])
        ]

    return res


def cve_history_all(
    changeStartDate: Optional[Union[str, datetime]] = None,
    changeEndDate: Optional[Union[str, datetime]] = None,
    cveId: Optional[str] = None,
    eventName: Optional[str] = None,
    resultsPerPage: int = 5000,
    startIndex: int = 0,
    nvdApiKey: Optional[str] = None,
    sleep_seconds_between_requests: Optional[int] = 6,
    raw_json_response: bool = False,
) -> Union[
    List[ChangeItem], List[Dict[str, Dict[str, Union[str, List[Dict[str, str]]]]]]
]:
    """
    Retrieves all change events in NVD matching the passed parameters.

    :param changeStartDate: Search from this date for the change. If filtering by the change date, both changeStartDate and changeEndDate are required.
    :param changeEndDate: Search until this date for the change. If filtering by the change date, both changeStartDate and changeEndDate are required.
    :param cveId: The complete change history for a specific vulnerability identified by its unique Common Vulnerabilities and Exposures identifier (the CVE ID).
    :param eventName: This parameter returns all CVE associated with a **single** specific type of change event.
    :param resultsPerPage: The number of results to return per page (default 5000).
    :param startIndex: The index of the first page to return from (default 0).
    :param nvdApiKey: Your API key for the NVD API.
    :param sleep_seconds_between_requests: The numebr of seconds to sleep between API requests. If an API key is not provided, a minumum value of 6 is enforced.
    :param raw_json_response: If true, will return raw JSON response instead of converting to local classes.
    :return: A list of results that were returned from the NVD API matching the criteria.
    """

    if nvdApiKey is None and sleep_seconds_between_requests < 6:
        sleep_seconds_between_requests = 6

    resp = cve_history(
        changeStartDate=changeStartDate,
        changeEndDate=changeEndDate,
        cveId=cveId,
        eventName=eventName,
        resultsPerPage=resultsPerPage,
        startIndex=startIndex,
        raw_json_response=raw_json_response,
    )

    changes = []
    while resp.get("totalResults", 0) > resp.get("resultsPerPage", 0) * resp.get(
        "startIndex", 0
    ) + resp.get("resultsPerPage", 0):
        changes += resp.get("cveChanges", [])
        time.sleep(sleep_seconds_between_requests)
        resp = cve_history(
            changeStartDate=changeStartDate,
            changeEndDate=changeEndDate,
            cveId=cveId,
            eventName=eventName,
            resultsPerPage=resultsPerPage,
            startIndex=startIndex,
            nvdApiKey=nvdApiKey,
            raw_json_response=raw_json_response,
        )

    changes += resp.get("cveChanges", [])

    return changes
