from typing import Optional

from odp.util.cheapdantic import BaseModel


class ContactInfo(BaseModel):
    """Contact information for a user"""

    contact: str
    """Contact in the form `Firstname Lastname <email>`"""

    organisation: Optional[str] = None
    """Organisation name"""
