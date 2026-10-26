import pytest

from jobradar.profile import ProfileError, load_profile


def test_profile_rejects_non_boolean_remote(tmp_path):
    profile = tmp_path / "profile.yaml"
    profile.write_text("remote: maybe\n", encoding="utf-8")
    with pytest.raises(ProfileError):
        load_profile(profile)


def test_profile_rejects_unknown_level(tmp_path):
    profile = tmp_path / "profile.yaml"
    profile.write_text("levels: [expert]\n", encoding="utf-8")
    with pytest.raises(ProfileError):
        load_profile(profile)
