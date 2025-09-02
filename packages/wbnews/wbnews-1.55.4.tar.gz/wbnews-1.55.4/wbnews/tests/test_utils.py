from wbnews.models.utils import endpoint_to_author


def test_endpoint_to_author():
    assert endpoint_to_author("test@test_test\\.com") == "Test Test"
    assert endpoint_to_author("http://somesubdomain.domain.com") == "Domain"
    assert endpoint_to_author("test") == "Test"
