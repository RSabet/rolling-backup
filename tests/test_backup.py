import pytest

from rolling_backup import backup

CONTENT = "Hello"


@pytest.fixture(scope="function")
def image_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("img.png")
    fn.write(CONTENT)
    return fn


def test_dummy(image_file):
    NUM = 12
    for i in range(NUM):
        backup(str(image_file), num_to_keep=NUM)
        d = image_file.dirpath()
        should = d / f"{image_file.basename}.{i:02d}"
        assert should.exists()
        assert should.read() == CONTENT


def test_rollover(image_file):
    NUM = 12
    for i in range(NUM):
        backup(str(image_file), num_to_keep=NUM)
        d = image_file.dirpath()
        should = d / f"{image_file.basename}.{i:02d}"
        assert should.exists()

    assert len(image_file.dirpath().listdir()) == NUM + 1
    backup(str(image_file), num_to_keep=NUM)
    assert len(image_file.dirpath().listdir()) == NUM + 1
