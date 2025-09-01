from datetime import datetime
from typing import Optional

from ..common import ContactInfo, License
from odp.util.cheapdantic import BaseModel


class Distribution(BaseModel):
    """Distribution information"""

    published_by: ContactInfo
    """Publisher information"""

    published_date: datetime
    """Date of first published"""

    website: str
    """Distribution website"""

    license: Optional[License] = None
    """Dataset license information"""
