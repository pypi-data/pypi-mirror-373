import shutil
from os.path import exists, join

from hecto import vcs


def test_get_repo():
    get = vcs.get_repo

    assert get("git@git.myproject.org:MyProject") == "git@git.myproject.org:MyProject"
    assert get("git://git.myproject.org/MyProject") == "git://git.myproject.org/MyProject"
    assert get("https://github.com/jpsca/hecto.git") == "https://github.com/jpsca/hecto.git"
    assert get("gh:/jpsca/hecto.git") == "https://github.com/jpsca/hecto.git"
    assert get("gh:jpsca/hecto.git") == "https://github.com/jpsca/hecto.git"
    assert get("gl:jpsca/hecto.git") == "https://gitlab.com/jpsca/hecto.git"
    assert get("git+https://git.myproject.org/MyProject") == "https://git.myproject.org/MyProject"
    assert get("git+ssh://git.myproject.org/MyProject") == "ssh://git.myproject.org/MyProject"
    assert get("git://git.myproject.org/MyProject.git@master")
    assert get("git://git.myproject.org/MyProject.git@v1.0")
    assert get("git://git.myproject.org/MyProject.git@da39a3ee5e6b4b0d3255bfef956018")

    assert get("http://google.com") is None
    assert get("git.myproject.org/MyProject") is None


def test_clone():
    tmp = vcs.clone("https://github.com/jpsca/hecto.git")
    assert tmp
    assert exists(join(tmp, "pyproject.toml"))
    shutil.rmtree(tmp)
