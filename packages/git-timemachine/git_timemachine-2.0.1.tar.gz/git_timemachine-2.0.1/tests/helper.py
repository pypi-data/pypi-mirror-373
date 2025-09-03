from pathlib import Path

from chance import chance
from pygit2 import Repository


def repo_add_new_file(repo: Repository) -> Path:
    path = Path(repo.workdir, chance.word())
    path.write_text(chance.sentence(), encoding='utf-8')

    repo.index.add_all()
    repo.index.write()

    return path
