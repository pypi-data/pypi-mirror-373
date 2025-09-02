def parse_time(s: str) -> float:
    s = s.strip()
    if s.replace(".", "", 1).isdigit():
        return float(s)
    parts = s.split(":")
    if len(parts) == 2:
        m, sec = parts
        return int(m) * 60 + float(sec)
    if len(parts) == 3:
        h, m, sec = parts
        return int(h) * 3600 + int(m) * 60 + float(sec)
    raise ValueError(f"Invalid time: {s}")


def hhmmss(t: float) -> str:
    t = max(0.0, float(t))
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return (
        f"{h:02d}:{m:02d}:{int(s):02d}"
        if s.is_integer()
        else f"{h:02d}:{m:02d}:{s:06.3f}"
    )
