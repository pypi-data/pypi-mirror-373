from __future__ import annotations

try:
    import pillow_avif

    assert pillow_avif
except ImportError:
    pass
try:
    import pillow_jxl

    assert pillow_jxl
except ImportError:
    pass
