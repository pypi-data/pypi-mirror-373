from datetime import datetime
from typing import Union


class VendorComment:

    def __init__(
        self, organization: str, comment: str, last_modified: Union[str, datetime]
    ):
        """

        :param organization: The organization responsible for the comment.
        :param comment: The comment text.
        :param last_modified: The last modified date of the comment, in ISO format.
        """
        self.organization = organization
        self.comment = comment
        if isinstance(last_modified, datetime):
            self.last_modified = last_modified
        else:
            self.last_modified = datetime.fromisoformat(last_modified)
