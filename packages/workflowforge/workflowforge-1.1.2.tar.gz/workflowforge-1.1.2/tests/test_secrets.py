"""Tests for secrets and variables."""

from workflowforge.secrets import github_context, secret, variable


def test_secret_creation():
    """Test secret reference creation."""
    secret_ref = secret("MY_SECRET")
    assert secret_ref == "${{ secrets.MY_SECRET }}"


def test_variable_creation():
    """Test variable reference creation."""
    var_ref = variable("MY_VAR")
    assert var_ref == "${{ vars.MY_VAR }}"


def test_github_context():
    """Test GitHub context helpers."""
    ctx = github_context()
    assert ctx.event_name() == "${{ github.event_name }}"
    assert ctx.ref() == "${{ github.ref }}"
    assert ctx.sha() == "${{ github.sha }}"
