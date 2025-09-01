from liveramp_automation import __version__ as liveramp_automation_version


def test_version_file_attributes():
    assert hasattr(liveramp_automation_version, '__version__')
    assert hasattr(liveramp_automation_version, '__author__')
    assert hasattr(liveramp_automation_version, '__title__')
    assert hasattr(liveramp_automation_version, '__description__')
    assert hasattr(liveramp_automation_version, '__url__')
    assert hasattr(liveramp_automation_version, '__build__')
    assert hasattr(liveramp_automation_version, '__author_email__')
    assert hasattr(liveramp_automation_version, '__license__')
    assert hasattr(liveramp_automation_version, '__copyright__')
    assert hasattr(liveramp_automation_version, '__cake__')
