from jobradar.connectors.ashby import fetch_ashby
from jobradar.connectors.greenhouse import fetch_greenhouse
from jobradar.connectors.lever import fetch_lever

CONNECTORS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
}

__all__ = ["CONNECTORS", "fetch_ashby", "fetch_greenhouse", "fetch_lever"]
