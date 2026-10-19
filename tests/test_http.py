from jobradar.http import USER_AGENT, make_client


def test_client_identifies_itself_and_has_timeouts():
    with make_client() as client:
        assert client.headers["user-agent"] == USER_AGENT and "JobRadar" in USER_AGENT
        assert client.timeout.read == 20 and client.timeout.connect == 10
