def get_level_by_xp(xp):
    xp_levels = [
        (0, 99),
        (100, 249),
        (250, 499),
        (500, 999),
        (1000, 1999),
        (2000, 3999),
        (4000, 6999),
        (7000, 9999),
        (10000, 14999),
        (15000, float("inf")),
    ]

    for level, (min_xp, max_xp) in enumerate(xp_levels, start=1):
        if min_xp <= xp <= max_xp:
            return level
    return 1
