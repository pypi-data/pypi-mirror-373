from datetime import datetime
from typing import Optional, List, Dict, Union
from uuid import UUID


class ChangeDetail:

    def __init__(
        self,
        change_type: str,
        action: Optional[str] = None,
        oldValue: Optional[str] = None,
        newValue: Optional[str] = None,
    ):
        self.type = change_type
        self.action = action
        self.old_value = oldValue
        self.new_value = newValue


class ChangeItem:

    def __init__(
        self,
        cveId: str,
        eventName: str,
        cveChangeId: str,
        sourceIdentifier: str,
        created: Optional[Union[str, datetime]] = None,
        details: Optional[List[Union[Dict[str, str], ChangeDetail]]] = None,
    ):
        self.details = []
        if details is not None:
            for detail in details:
                if isinstance(detail, ChangeDetail):
                    self.details.append(detail)
                elif isinstance(detail, Dict):
                    self.details.append(
                        ChangeDetail(
                            detail.get("type"),
                            detail.get("action"),
                            detail.get("oldValue"),
                            detail.get("newValue"),
                        )
                    )
                else:
                    raise TypeError(
                        f"details list must be a List of Dict's or nvdinterface.ChangeDetail's"
                    )

        self._eventName = eventName
        self._cveId = cveId
        self._cveChangeId = UUID(cveChangeId)
        self._sourceIdentifier = sourceIdentifier
        self._created = (
            created
            if isinstance(created, datetime)
            else datetime.fromisoformat(created)
        )

    @property
    def event_name(self):
        return self._eventName

    @property
    def cve_id(self):
        return self._cveId

    @property
    def cve_change_id(self):
        return str(self._cveChangeId)

    @property
    def source_identifier(self):
        return self._sourceIdentifier

    @property
    def created(self):
        return self._created

    @property
    def created_str(self):
        return self._created.isoformat()
