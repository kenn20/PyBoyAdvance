from types import SimpleNamespace

import pytest

from pyboy_advance import PyBoyAdvance


EWRAM_START = 0x02000000
IWRAM_START = 0x03000000


@pytest.fixture
def emulator() -> PyBoyAdvance:
    emulator = object.__new__(PyBoyAdvance)
    emulator.memory = SimpleNamespace(
        ewram=bytearray(0x40000),
        iwram=bytearray(0x8000),
    )
    emulator.scheduler = SimpleNamespace(cycles=123456)
    return emulator


def test_peek_reads_ewram_and_iwram_without_advancing_scheduler(emulator: PyBoyAdvance) -> None:
    emulator.memory.ewram[0:4] = b"\x78\x56\x34\x12"
    emulator.memory.iwram[0:4] = b"\xEF\xCD\xAB\x89"

    before = emulator.scheduler.cycles

    assert emulator.peek_u8(EWRAM_START) == 0x78
    assert emulator.peek_u16(EWRAM_START) == 0x5678
    assert emulator.peek_u32(EWRAM_START) == 0x12345678
    assert emulator.peek_u32(IWRAM_START) == 0x89ABCDEF
    assert emulator.scheduler.cycles == before


@pytest.mark.parametrize(
    "address",
    [
        EWRAM_START - 1,
        EWRAM_START + 0x40000,
        IWRAM_START - 1,
        IWRAM_START + 0x8000,
        0x04000000,
    ],
)
def test_peek_rejects_addresses_outside_work_ram(emulator: PyBoyAdvance, address: int) -> None:
    with pytest.raises(ValueError, match="wholly in EWRAM or IWRAM"):
        emulator.peek_u8(address)


@pytest.mark.parametrize(
    ("method", "address"),
    [
        ("peek_u16", EWRAM_START + 0x3FFFF),
        ("peek_u32", IWRAM_START + 0x7FFD),
    ],
)
def test_peek_rejects_widths_that_cross_work_ram_boundary(
    emulator: PyBoyAdvance, method: str, address: int
) -> None:
    with pytest.raises(ValueError, match="wholly in EWRAM or IWRAM"):
        getattr(emulator, method)(address)


def test_peek_surface_has_no_write_operation() -> None:
    assert not any(name.startswith(("poke", "write")) for name in PyBoyAdvance.__dict__)
