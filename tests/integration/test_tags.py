import re
from typing import List

from toot import api, cli
from toot.entities import FeaturedTag, Tag, from_dict, from_dict_list


def test_tags(run):
    result = run(cli.tags, "followed")
    assert result.exit_code == 0
    assert result.stdout.strip() == "You're not following any hashtags"

    result = run(cli.tags, "follow", "foo")
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ You are now following #foo"

    result = run(cli.tags, "followed")
    assert result.exit_code == 0
    assert _find_tags(result.stdout) == ["#foo"]

    result = run(cli.tags, "follow", "bar")
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ You are now following #bar"

    result = run(cli.tags, "followed")
    assert result.exit_code == 0
    assert _find_tags(result.stdout) == ["#bar", "#foo"]

    result = run(cli.tags, "unfollow", "foo")
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ You are no longer following #foo"

    result = run(cli.tags, "followed")
    assert result.exit_code == 0
    assert _find_tags(result.stdout) == ["#bar"]

    result = run(cli.tags, "unfollow", "bar")
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ You are no longer following #bar"

    result = run(cli.tags, "followed")
    assert result.exit_code == 0
    assert result.stdout.strip() == "You're not following any hashtags"


def test_tags_json(run_json):
    result = run_json(cli.tags, "followed", "--json")
    assert result == []

    result = run_json(cli.tags, "follow", "foo", "--json")
    tag = from_dict(Tag, result)
    assert tag.name == "foo"
    assert tag.following is True

    result = run_json(cli.tags, "followed", "--json")
    [tag] = from_dict_list(Tag, result)
    assert tag.name == "foo"
    assert tag.following is True

    result = run_json(cli.tags, "follow", "bar", "--json")
    tag = from_dict(Tag, result)
    assert tag.name == "bar"
    assert tag.following is True

    result = run_json(cli.tags, "followed", "--json")
    tags = from_dict_list(Tag, result)
    [bar, foo] = sorted(tags, key=lambda t: t.name)
    assert foo.name == "foo"
    assert foo.following is True
    assert bar.name == "bar"
    assert bar.following is True

    result = run_json(cli.tags, "unfollow", "foo", "--json")
    tag = from_dict(Tag, result)
    assert tag.name == "foo"
    assert tag.following is False

    result = run_json(cli.tags, "unfollow", "bar", "--json")
    tag = from_dict(Tag, result)
    assert tag.name == "bar"
    assert tag.following is False

    result = run_json(cli.tags, "followed", "--json")
    assert result == []


def test_tags_featured(run, app, user):
    result = run(cli.tags, "featured")
    assert result.exit_code == 0
    assert result.stdout.strip() == "You don't have any featured hashtags"

    result = run(cli.tags, "feature", "foo")
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ Tag #foo is now featured"

    result = run(cli.tags, "featured")
    assert result.exit_code == 0
    assert _find_tags(result.stdout) == ["#foo"]

    result = run(cli.tags, "feature", "bar")
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ Tag #bar is now featured"

    result = run(cli.tags, "featured")
    assert result.exit_code == 0
    assert _find_tags(result.stdout) == ["#bar", "#foo"]

    # Unfeature by Name
    result = run(cli.tags, "unfeature", "foo")
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ Tag #foo is no longer featured"

    result = run(cli.tags, "featured")
    assert result.exit_code == 0
    assert _find_tags(result.stdout) == ["#bar"]

    # Unfeature by ID
    tag = api.find_featured_tag(app, user, "bar")
    assert tag is not None

    result = run(cli.tags, "unfeature", tag["id"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "✓ Tag #bar is no longer featured"

    result = run(cli.tags, "featured")
    assert result.exit_code == 0
    assert result.stdout.strip() == "You don't have any featured hashtags"


def test_tags_featured_json(run_json):
    result = run_json(cli.tags, "featured", "--json")
    assert result == []

    result = run_json(cli.tags, "feature", "foo", "--json")
    tag = from_dict(FeaturedTag, result)
    assert tag.name == "foo"

    result = run_json(cli.tags, "featured", "--json")
    [tag] = from_dict_list(FeaturedTag, result)
    assert tag.name == "foo"

    result = run_json(cli.tags, "feature", "bar", "--json")
    tag = from_dict(FeaturedTag, result)
    assert tag.name == "bar"

    result = run_json(cli.tags, "featured", "--json")
    tags = from_dict_list(FeaturedTag, result)
    [bar, foo] = sorted(tags, key=lambda t: t.name)
    assert foo.name == "foo"
    assert bar.name == "bar"

    result = run_json(cli.tags, "unfeature", "foo", "--json")
    assert result == {}

    result = run_json(cli.tags, "unfeature", "bar", "--json")
    assert result == {}

    result = run_json(cli.tags, "featured", "--json")
    assert result == []


def _find_tags(txt: str) -> List[str]:
    return sorted(re.findall(r"#\w+", txt))
