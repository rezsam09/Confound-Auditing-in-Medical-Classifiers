import re, numpy as np

def groups_from_names(names, mode="prefix"):
    """NIH malaria file names look like C100P61ThinF_IMG_20150918_144104_cell_162.png.
    mode 'prefix': 'C100P61' (slide/patient token, conservative to the extent C is a sub-unit of P)
    mode 'pnum'  : 'P61'     (coarser; use this as the stricter patient-level grouping)
    NOTE: the grouping is parsed from file names; verify against the dataset readme before calling it 'patient-level'."""
    out = []
    for n in names:
        m = re.match(r"^(C\d+)(P\d+)thinf", str(n), flags=re.I)
        out.append((m.group(1) + m.group(2)) if (m and mode == "prefix") else (m.group(2) if m else str(n).split("_")[0]))
    return np.array(out)
