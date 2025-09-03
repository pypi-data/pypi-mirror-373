import pytest
from wayback_machine_archiver.clients import LegacyClient
from requests.adapters import HTTPAdapter
import requests


@pytest.fixture
def session():
    session = requests.Session()
    session.mount("https://", HTTPAdapter())
    session.mount("http://", HTTPAdapter())
    return session


def test_legacy_client_archive(requests_mock, session):
    url = "https://web.archive.org/save/yahoo.com"
    requests_mock.head(url)
    client = LegacyClient(session=session)
    client.archive(url, rate_limit_wait=0)
    assert True


def test_legacy_client_archive_with_404(requests_mock, session):
    url = "https://web.archive.org/save/yahoo.com"
    requests_mock.head(url, status_code=404)
    with pytest.raises(requests.exceptions.HTTPError):
        client = LegacyClient(session=session)
        client.archive(url, rate_limit_wait=0)
