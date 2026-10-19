from jobradar.connectors.ashby import fetch_ashby
from jobradar.connectors.greenhouse import fetch_greenhouse
from jobradar.connectors.lever import fetch_lever
from jobradar.connectors.personio import fetch_personio
from jobradar.connectors.recruitee import fetch_recruitee
from jobradar.connectors.smartrecruiters import fetch_smartrecruiters
from jobradar.connectors.workable import fetch_workable

CONNECTORS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "workable": fetch_workable,
    "recruitee": fetch_recruitee,
    "personio": fetch_personio,
    "smartrecruiters": fetch_smartrecruiters,
}

__all__ = ["CONNECTORS"]
