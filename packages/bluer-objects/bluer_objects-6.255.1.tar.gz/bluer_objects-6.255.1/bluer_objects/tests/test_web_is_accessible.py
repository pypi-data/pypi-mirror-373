from bluer_objects.web.functions import is_accessible
from bluer_ai.env import abcli_is_github_workflow


def test_url_is_accessible():
    success = is_accessible("void")
    assert not success

    url = "https://cnn.com" if abcli_is_github_workflow else "https://iribnews.ir"
    success = is_accessible(url)
    assert success
