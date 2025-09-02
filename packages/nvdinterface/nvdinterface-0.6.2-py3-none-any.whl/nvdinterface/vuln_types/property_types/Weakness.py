from typing import Dict, List, Union

from .Description import Description


class Weakness:

    def __init__(
        self,
        source: str,
        weakness_type: str,
        descriptions: Union[List[Description], List[Dict]],
    ):
        if len(descriptions) < 1:
            raise ValueError("At least one valid description must be present")
        if isinstance(descriptions[0], dict):
            for desc in descriptions:
                if not isinstance(desc, dict):
                    raise ValueError(
                        "An element of the descriptions parameter was not a Dictionary."
                    )
            self.descriptions = [
                Description(d.get("lang"), d.get("value")) for d in descriptions
            ]
        elif isinstance(descriptions[0], Description):
            for desc in descriptions:
                if not isinstance(desc, Description):
                    raise ValueError(
                        "An element of the descriptions parameter was not a Description."
                    )
            self.descriptions = descriptions
        else:
            raise TypeError(
                f"Parameter 'descriptions' must be a list of entirely Dict's or nvdinterface.Description's."
            )
        self.source = source
        self.weakness_type = weakness_type
