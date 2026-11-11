from hybridml.environment import verify_environment


def test_environment_contract():
    info = verify_environment()
    assert info["torch_cuda"] is None
    assert info["torch_version"].startswith("2.1.2")
