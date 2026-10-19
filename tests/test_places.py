from jobradar.models import Job
from jobradar.places import fold, location_matches, open_to_spain


def test_fold_strips_accents():
    assert fold("Cataluña") == "cataluna"
    assert fold("València") == "valencia"


def test_city_aliases():
    assert location_matches("Barcelona, Catalonia, Spain", "barcelona")
    assert location_matches("Sant Cugat del Vallès", "Barcelona")
    assert location_matches("BCN Office", "barcelona")
    assert not location_matches("Madrid, Spain", "barcelona")


def test_open_to_spain():
    assert open_to_spain("Remote - Spain", True)
    assert open_to_spain("Remote, EMEA", True)
    assert not open_to_spain("Remote - US", True)
    assert not open_to_spain("Madrid, Spain", False)


def test_query_ignores_accents_and_case():
    job = Job("1", "Ingeniero de Datos", "Acme", "Cataluña", "https://x", "lever")
    assert job.matches("INGENIERO datos", city="catalunya")
