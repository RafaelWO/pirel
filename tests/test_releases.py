from pirel.releases import PythonRelease


def test_release_with_no_status():
    data = {
        "branch": "",
        "pep": 826,
        "status": "",
        "first_release": "2027-10-06",
        "end_of_life": "2032-10",
        "release_manager": "Savannah Ostrowski",
    }
    release = PythonRelease("3.16", data)
    assert release.status == "[gray]n/a[/gray]"
