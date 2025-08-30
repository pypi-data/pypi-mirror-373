from .util import blocklist_form_url_or_file


def test_blocklist_from_file(tmp_path):
    filename = tmp_path / "list"
    with open(filename, "w") as fp:
        fp.write(
            """blocked.test
evil.test
bad.test"""
        )

    result = blocklist_form_url_or_file(str(filename))

    assert result == {"blocked.test", "evil.test", "bad.test"}
