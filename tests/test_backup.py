import random
import pytest

from rolling_backup import backup

CONTENT = "Hello"


def create_backups(image_file, num: int):
    for i in range(num):
        image_file.write(f"{CONTENT} - {i}")
        assert backup(str(image_file), num_to_keep=num)
        d = image_file.dirpath()
        should = d / f"{image_file.basename}.{i:02d}"
        assert should.exists()

    for i in range(num):
        d = image_file.dirpath()
        should = d / f"{image_file.basename}.{i:02d}"
        assert should.read() == f"{CONTENT} - {num - i - 1}"


@pytest.fixture(scope="function")
def image_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("img.png")
    fn.write(CONTENT)
    return fn


def test_dummy(image_file):
    create_backups(image_file, 12)


def test_rollover(image_file):
    NUM = 12
    create_backups(image_file, NUM)

    assert len(image_file.dirpath().listdir()) == NUM + 1
    assert backup(str(image_file), num_to_keep=NUM)
    assert len(image_file.dirpath().listdir()) == NUM + 1


def test_missing(image_file):
    NUM = 12
    create_backups(image_file, NUM)
    n = random.choice(range(NUM))
    d = image_file.dirpath()
    to_del = d / f"{image_file.basename}.{n:02d}"
    to_del.remove()
    assert not to_del.exists()
    image_file.write("xxx")
    assert backup(str(image_file), NUM)
    assert to_del.exists()

    assert (d / f"{image_file.basename}.00").read() == "xxx"
    assert (d / f"{image_file.basename}.{n:02d}").read() == f"{CONTENT} - {NUM - n}"
    assert (d / f"{image_file.basename}.{(n + 1):02d}").read() == f"{CONTENT} - {NUM - n - 2}"


def test_non_existing_dir():
    assert not backup("xxxyyyzzz")