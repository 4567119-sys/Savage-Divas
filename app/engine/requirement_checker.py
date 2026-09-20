from typing import List, Tuple

from app.models.case import Case


def check_requirements(case: Case) -> Tuple[bool, List[str]]:
    """
    Check whether all requirements for a case have been fulfilled.

    Returns:
        (all_fulfilled, missing_requirements)
    """
    missing_requirements = [
        requirement.title
        for requirement in case.requirements
        if not requirement.is_fulfilled
    ]

    return len(missing_requirements) == 0, missing_requirements