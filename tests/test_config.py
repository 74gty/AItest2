def test_config_has_remote_url(test_config):
    assert test_config["remote_url"] == "http://localhost:4444/wd/hub"
