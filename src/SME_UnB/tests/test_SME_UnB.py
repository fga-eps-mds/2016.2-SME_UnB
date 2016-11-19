import pytest
import SME_UnB


def test_project_defines_author_and_version():
    assert hasattr(SME_UnB, '__author__')
    assert hasattr(SME_UnB, '__version__')
