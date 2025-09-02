def to_uint8(*args):
    """Convert a float value in the range [0, 1] to an unsigned 8-bit integer."""
    out = [0] * len(args)
    for i, arg in enumerate(args):
        if int(arg) == arg and 0 <= arg <= 255:
            out[i] = int(arg)
        elif 0 <= arg <= 1:
            out[i] = int(arg * 255)
        else:
            raise ValueError(f"Value {arg} is out of range [0, 1] or [0, 255] for conversion to uint8.")
    return tuple(out)


def print_in_color(text, foreground_rgb=None, background_rgb=None):
    out = text
    if foreground_rgb is not None:
        foreground_rgb = to_uint8(*foreground_rgb)
        foreground_rgb = [str(c) for c in foreground_rgb]
        out = f"\x1b[38;2;{';'.join(foreground_rgb)}m{text}"
    if background_rgb is not None:
        background_rgb = to_uint8(*background_rgb)
        background_rgb = [str(c) for c in background_rgb]
        out = f"\x1b[48;2;{';'.join(background_rgb)}m{text}"

    return f"{out}\x1b[0m"  # Reset all styles
