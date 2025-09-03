from dataclasses import dataclass
from parsley_coco import create_parsley


def test_empty_command_line(monkeypatch):
    @dataclass
    class Config:
        x: int = 42
        y: str = "default"

    # Simulate empty command line
    monkeypatch.setattr("sys.argv", ["script.py"])
    parser = create_parsley(Config)
    config = parser.parse_arguments()
    assert config.x == 42
    assert config.y == "default"
    print("Empty command line test passed.")
