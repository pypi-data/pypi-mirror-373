from datetime import datetime
from decimal import Decimal
from typing import Optional

from flux_sdk.flux_core.data_models import DeductionType


class EmployeeDeductionSetting(object):
    """
    This is the return type for "parse_deductions" method in the UpdateDeductionElections
    interface.
    """
    ssn: str
    client_id: Optional[str]  # The client identifier to be sent if available.
    effective_date: datetime
    deduction_type: DeductionType
    value: float
    is_percentage: bool
    id: str
    employee_id: Optional[str] = None  # The employee identifier to be sent if available.
    company_contribution: Optional[Decimal] = None  # The employer match amount
    company_contribution_is_percentage: Optional[bool] = None  # Whether the employer match is a percentage
