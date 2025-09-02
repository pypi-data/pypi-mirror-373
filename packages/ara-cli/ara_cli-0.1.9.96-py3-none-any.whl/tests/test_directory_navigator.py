from ara_cli.directory_navigator import DirectoryNavigator
import pytest


@pytest.fixture
def navigator():
    return DirectoryNavigator()
