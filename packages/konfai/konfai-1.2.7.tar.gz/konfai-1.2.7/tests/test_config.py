import pytest
from pathlib import Path
from konfai.utils.config import config

# ---- Classe enfant pour les objets imbriqués ----
class SubObject:

    @config("SubObject")
    def __init__(self, z: float = 0.5):
        self.z = z

# ---- Classe principale testant tous les types pris en charge ----
class DummyAllTypes:
    @config("MainTest")
    def __init__(
        self,
        a: int = 1,
        b: str = "hello",
        c: bool = True,
        d: float = 3.14,
        e: list[int] = [1, 2, 3],
        f: list[str] = ["a", "b"],
        g: list[bool] = [True, False],
        h: list[float] = [1.0, 2.0],
        i: dict[str, int] = {"x": 1},
        j: SubObject = None,
        l: dict[str, SubObject] = {"A" : SubObject(), "B" : SubObject()}
    ):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g
        self.h = h
        self.i = i
        self.j = j
        self.l = l

@pytest.fixture
def dummy_config_file(tmp_path: Path):
    yaml_path = tmp_path / "config.yml"
    yaml_content = """
MainTest:
  a: 42
  b: test
  c: false
  d: 2.718
  e: [10, 20]
  f: [x, y]
  g: [true, false, true]
  h: [0.1, 0.2]
  i: {"foo": 9}
  j:
    z: 9.99
  l:
    key1:
      z: 7.7
    key2:
      z: 8.8
"""
    yaml_path.write_text(yaml_content)
    return yaml_path

def test_config_instantiation(monkeypatch):
    dummy_config_file = "./tests/dummy_data/dummy_config.yml"
    monkeypatch.setenv("KONFAI_CONFIG_FILE", str(dummy_config_file))
    monkeypatch.setenv("KONFAI_CONFIG_MODE", "Done")

    obj = DummyAllTypes(config=str(dummy_config_file))

    assert obj.a == 42
    assert obj.b == "test"
    assert obj.c is False
    assert abs(obj.d - 2.718) < 1e-6
    assert obj.e == [10, 20]
    assert obj.f == ["x", "y"]
    assert obj.g == [True, False, True]
    assert obj.h == [0.1, 0.2]
    assert obj.i == {"foo": 9}
    assert isinstance(obj.j, SubObject)
    assert obj.j.z == 9.99
    assert isinstance(obj.l, dict)
    assert set(obj.l.keys()) == {"key1", "key2"}
    assert obj.l["key1"].z == 7.7
    assert obj.l["key2"].z == 8.8
  
def test_config_create(monkeypatch):
    dummy_config_file = "./tests/dummy_data/dummy_default_config.yml"
    monkeypatch.setenv("KONFAI_CONFIG_FILE", str(dummy_config_file))
    monkeypatch.setenv("KONFAI_CONFIG_MODE", "Done")

    obj = DummyAllTypes(config=str(dummy_config_file))

    assert obj.a == 1
    assert obj.b == "hello"
    assert obj.c is True
    assert abs(obj.d - 3.14) < 1e-6
    assert obj.e == [1,2,3]
    assert obj.f == ["a", "b"]
    assert obj.g == [True, False]
    assert obj.h == [1, 2]
    assert obj.i == {}
    assert isinstance(obj.j, SubObject)
    assert obj.j.z == 0.5
    assert isinstance(obj.l, dict)
    assert set(obj.l.keys()) == {"A", "B"}
    assert obj.l["A"].z == 0.5
    assert obj.l["B"].z == 0.5