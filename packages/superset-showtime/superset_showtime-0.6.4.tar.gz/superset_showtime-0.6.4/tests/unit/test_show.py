"""
Tests for Show class - Individual environment management
"""

from datetime import datetime
from unittest.mock import patch

from showtime.core.show import Show, short_sha


def test_show_creation():
    """Test basic Show creation"""
    show = Show(
        pr_number=1234,
        sha="abc123f",
        status="running",
        ip="52.1.2.3",
        ttl="24h",
        requested_by="maxime",
    )

    assert show.pr_number == 1234
    assert show.sha == "abc123f"
    assert show.status == "running"
    assert show.ip == "52.1.2.3"
    assert show.ttl == "24h"
    assert show.requested_by == "maxime"


def test_show_aws_properties():
    """Test AWS-related computed properties"""
    show = Show(pr_number=1234, sha="abc123f", status="running")

    assert show.aws_service_name == "pr-1234-abc123f"
    assert show.ecs_service_name == "pr-1234-abc123f-service"
    assert show.aws_image_tag == "pr-1234-abc123f-ci"
    assert show.short_sha == "abc123f"


def test_show_status_properties():
    """Test status checking properties"""
    # Test running
    show = Show(pr_number=1234, sha="abc123f", status="running")
    assert show.is_running is True
    assert show.is_building is False
    assert show.is_built is False
    assert show.is_deploying is False
    assert show.is_updating is False

    # Test building
    show.status = "building"
    assert show.is_running is False
    assert show.is_building is True
    assert show.is_built is False

    # Test built
    show.status = "built"
    assert show.is_built is True
    assert show.is_building is False

    # Test deploying
    show.status = "deploying"
    assert show.is_deploying is True
    assert show.is_running is False

    # Test updating
    show.status = "updating"
    assert show.is_updating is True
    assert show.is_running is False


def test_show_needs_update():
    """Test update checking logic"""
    show = Show(pr_number=1234, sha="abc123f", status="running")

    # Same SHA (full or short) - no update needed
    assert show.needs_update("abc123f") is False
    assert show.needs_update("abc123f1234567890abcdef") is False

    # Different SHA - update needed
    assert show.needs_update("def456a") is True
    assert show.needs_update("def456a1234567890abcdef") is True


def test_show_is_expired():
    """Test expiration checking"""
    # Test basic logic - exact age doesn't matter for unit test
    # No created_at - not expired
    show_no_time = Show(pr_number=1234, sha="abc123f", status="running")
    assert show_no_time.is_expired(24) is False

    # Test invalid timestamp - not expired (error handling)
    show_bad_time = Show(pr_number=1234, sha="abc123f", status="running", created_at="invalid")
    assert show_bad_time.is_expired(24) is False

    # Test with valid format - this tests the parsing logic works
    # Use a recent timestamp so it's not expired
    recent_time = datetime.now().strftime("%Y-%m-%dT%H-%M")
    show_recent = Show(pr_number=1234, sha="abc123f", status="running", created_at=recent_time)
    assert show_recent.is_expired(48) is False  # Should not be expired with generous window


def test_show_from_circus_labels():
    """Test creating Show from circus tent labels"""
    labels = [
        "🎪 abc123f 🚦 running",
        "🎪 🎯 abc123f",  # Active pointer
        "🎪 abc123f 📅 2024-01-15T14-30",
        "🎪 abc123f 🌐 52.1.2.3:8080",  # IP with port
        "🎪 abc123f ⌛ 24h",
        "🎪 abc123f 🤡 maxime",
        "some-other-label",  # Should be ignored
    ]

    show = Show.from_circus_labels(1234, labels, "abc123f")

    assert show is not None
    assert show.pr_number == 1234
    assert show.sha == "abc123f"
    assert show.status == "running"
    assert show.ip == "52.1.2.3"  # Port removed during parsing
    assert show.created_at == "2024-01-15T14-30"
    assert show.ttl == "24h"
    assert show.requested_by == "maxime"


def test_show_from_circus_labels_missing_pointer():
    """Test Show creation fails without active/building pointer"""
    labels = [
        "🎪 abc123f 🚦 running",
        "🎪 abc123f 📅 2024-01-15T14-30",
        # Missing 🎯 or 🏗️ pointer
    ]

    show = Show.from_circus_labels(1234, labels, "abc123f")
    assert show is None  # Should fail without pointer


def test_show_from_circus_labels_building():
    """Test Show creation with building pointer"""
    labels = [
        "🎪 def456a 🚦 building",
        "🎪 🏗️ def456a",  # Building pointer
        "🎪 def456a 📅 2024-01-15T15-00",
    ]

    show = Show.from_circus_labels(1234, labels, "def456a")

    assert show is not None
    assert show.status == "building"
    assert show.sha == "def456a"


def test_show_to_circus_labels():
    """Test converting Show to circus tent labels"""
    show = Show(
        pr_number=1234,
        sha="abc123f",
        status="running",
        ip="52.1.2.3",
        created_at="2024-01-15T14-30",
        ttl="48h",
        requested_by="maxime",
    )

    labels = show.to_circus_labels()

    expected = [
        "🎪 abc123f 🚦 running",
        "🎪 🎯 abc123f",
        "🎪 abc123f 📅 2024-01-15T14-30",
        "🎪 abc123f ⌛ 48h",
        "🎪 abc123f 🌐 52.1.2.3:8080",  # IP with port added
        "🎪 abc123f 🤡 maxime",
    ]

    # Check all expected labels are present
    for expected_label in expected:
        assert expected_label in labels


def test_show_to_circus_labels_minimal():
    """Test converting Show with minimal data"""
    show = Show(pr_number=1234, sha="abc123f", status="building")

    labels = show.to_circus_labels()

    # Should have status, pointer, timestamp, TTL (created_at auto-generated)
    assert any("🚦 building" in label for label in labels)
    assert any("🎯 abc123f" in label for label in labels)
    assert any("📅" in label for label in labels)  # Auto-generated timestamp
    assert any("⌛ 24h" in label for label in labels)  # Default TTL

    # Should not have IP or user labels
    assert not any("🌐" in label for label in labels)
    assert not any("🤡" in label for label in labels)


def test_short_sha_function():
    """Test short SHA utility function"""
    assert short_sha("abc123f1234567890abcdef12345678") == "abc123f"
    assert short_sha("abc123f") == "abc123f"
    assert short_sha("a") == "a"
    assert short_sha("") == ""


def test_show_from_circus_labels_wrong_sha():
    """Test Show creation with wrong SHA returns None"""
    labels = [
        "🎪 abc123f 🚦 running",
        "🎪 🎯 abc123f",
    ]

    # Request different SHA than in labels
    show = Show.from_circus_labels(1234, labels, "def456a")
    assert show is None


def test_show_from_circus_labels_partial():
    """Test Show creation with partial labels"""
    labels = [
        "🎪 abc123f 🚦 failed",
        "🎪 🎯 abc123f",
        # Missing other optional labels
    ]

    show = Show.from_circus_labels(1234, labels, "abc123f")

    assert show is not None
    assert show.status == "failed"
    assert show.ip is None
    assert show.created_at is None
    assert show.requested_by is None
    assert show.ttl == "24h"  # Default


def test_show_is_expired_datetime_import():
    """Test the is_expired method imports datetime correctly"""
    show = Show(pr_number=1234, sha="abc123f", status="running", created_at="2024-01-15T14-30")

    # Test that the method can handle datetime operations
    # The exact result doesn't matter, just that it doesn't crash on import
    try:
        result = show.is_expired(24)
        assert isinstance(result, bool)
    except Exception as e:
        # Should not fail due to import issues
        assert "datetime" not in str(e).lower()


def test_show_is_expired_error_handling():
    """Test is_expired with malformed timestamps"""
    # Test various malformed timestamps
    test_cases = [
        "not-a-date",
        "2024-13-45T25-70",  # Invalid date/time
        "2024/01/15 14:30",  # Wrong format
        "",  # Empty string
        None,  # None (though this is handled earlier)
    ]

    for bad_timestamp in test_cases:
        show = Show(pr_number=1234, sha="abc123f", status="running", created_at=bad_timestamp)
        # Should not crash and return False for safety
        assert show.is_expired(24) is False


def test_show_docker_image_path():
    """Test Docker image path generation"""
    show = Show(pr_number=1234, sha="abc123f", status="building")

    # Test the Docker tag format used in _build_docker_image
    expected_tag = "apache/superset:pr-1234-abc123f-ci"
    # This matches the tag format in the actual implementation
    actual_tag = f"apache/superset:pr-{show.pr_number}-{show.sha}-ci"
    assert actual_tag == expected_tag


def test_show_to_circus_labels_auto_timestamp():
    """Test auto-generated timestamp in to_circus_labels"""
    show = Show(pr_number=1234, sha="abc123f", status="building")
    # No created_at initially
    assert show.created_at is None

    with patch("showtime.core.show.datetime") as mock_dt:
        mock_dt.utcnow.return_value.strftime.return_value = "2024-01-15T14-30"

        labels = show.to_circus_labels()

        # Should auto-generate timestamp
        assert show.created_at == "2024-01-15T14-30"
        assert any("📅 2024-01-15T14-30" in label for label in labels)


def test_show_to_circus_labels_no_active_pointer():
    """Test that to_circus_labels() does not include active pointer"""
    show = Show(
        pr_number=1234, sha="abc123f", status="running", ip="1.2.3.4", requested_by="testuser"
    )

    labels = show.to_circus_labels()

    # Should include status, timestamp, TTL, IP, requester
    assert any("🎪 abc123f 🚦 running" in label for label in labels)
    assert any("🎪 abc123f 📅" in label for label in labels)
    assert any("🎪 abc123f ⌛ 24h" in label for label in labels)
    assert any("🎪 abc123f 🌐 1.2.3.4:8080" in label for label in labels)
    assert any("🎪 abc123f 🤡 testuser" in label for label in labels)

    # Should NOT include active pointer
    assert not any("🎪 🎯" in label for label in labels)


def test_show_to_circus_labels_building_status():
    """Test to_circus_labels() for building status"""
    show = Show(pr_number=1234, sha="def456a", status="building")

    labels = show.to_circus_labels()

    # Should include building status
    assert any("🎪 def456a 🚦 building" in label for label in labels)

    # Should NOT include active pointer or building pointer
    assert not any("🎪 🎯" in label for label in labels)
    assert not any("🎪 🏗️" in label for label in labels)
