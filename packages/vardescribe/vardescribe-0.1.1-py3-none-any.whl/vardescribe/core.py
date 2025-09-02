# src/vardescribe/core.py

import subprocess
import inspect
import numpy as np

def vardescribe(obj):
    #Written by Igor Reidler 2025
    
    try:
        import pandas as pd
    except ImportError:
        pd = None

    TAB = 8

    def _fmt(x):
        x = float(x)
        if x == 0:
            return "0"
        if abs(x) >= 1e5 or abs(x) < 1e-2:
            return f"{x:.2g}"
        return f"{x:.2f}".rstrip("0").rstrip(".")

    def _tabs(n):
        return "\t" * ((n + TAB - 1) // TAB)

    def _lines(cur, lvl, top=False, name=None):
        indent = "\t" * lvl
        out = []

        # ---------- DataFrame ----------
        if pd is not None and isinstance(cur, pd.DataFrame):
            header = (
                f"{indent}dataframe {name} with {len(cur)} rows, {cur.shape[1]} columns"
                if top and name
                else f"{indent}DataFrame rows({len(cur)})"
            )
            out.append(header)
            max_name = max(len(repr(c)) for c in cur.columns)
            max_dtype = max(len(str(cur[c].dtype)) for c in cur.columns)
            for col in cur.columns:
                ser = cur[col]
                dtype = str(ser.dtype)
                pad1 = _tabs(max_name - len(repr(col)) + 1)
                pad2 = _tabs(max_dtype - len(dtype) + 1)
                stats = (
                    f"[min:{_fmt(ser.min())}, max:{_fmt(ser.max())}, avg:{_fmt(ser.mean())}]"
                    if np.issubdtype(ser.dtype, np.number)
                    else ""
                )
                out.append(f"{indent}\t{repr(col)}{pad1}{dtype}{pad2}{stats}")
            return out

        # ---------- dict ----------
        if isinstance(cur, dict):
            header = (
                f"{indent}dict {name} with {len(cur)} keys"
                if top and name
                else f"{indent}dict with {len(cur)} keys"
            )
            out.append(header)
            for k, v in cur.items():
                sub = _lines(v, lvl + 1)
                out.append(f"{indent}\t{repr(k)}\t{sub[0][lvl + 1 :]}")
                out.extend(sub[1:])
            return out

        # ---------- list ----------
        if isinstance(cur, list):
            counts = {}
            for x in cur:
                counts[type(x).__name__] = counts.get(type(x).__name__, 0) + 1
            info = (
                f" [all {next(iter(counts))}]"
                if len(counts) == 1
                else " [" + ", ".join(f"{t}:{c}" for t, c in counts.items()) + "]"
            )
            out.append(f"{indent}list size({len(cur)}){info}")
            if cur:
                out.extend(_lines(cur[0], lvl + 1))
            return out

        # ---------- tuple ----------
        if isinstance(cur, tuple):
            counts = {}
            for x in cur:
                counts[type(x).__name__] = counts.get(type(x).__name__, 0) + 1
            info = (
                f" [all {next(iter(counts))}]"
                if len(counts) == 1
                else " [" + ", ".join(f"{t}:{c}" for t, c in counts.items()) + "]"
            )
            out.append(f"{indent}tuple size({len(cur)}){info}")
            if cur:
                out.extend(_lines(cur[0], lvl + 1))
            return out

        # ---------- ndarray or similar ----------
        if hasattr(cur, "shape"):
            if cur.shape == ():
                desc = f"scalar {cur.dtype}"
                if cur.size:
                    desc += f" [value: {_fmt(cur.item())}]"
            else:
                desc = f"ndarray size{tuple(cur.shape)} {cur.dtype}"
                if cur.size and np.issubdtype(cur.dtype, np.number):
                    desc += (
                        f" [min:{_fmt(cur.min())}, max:{_fmt(cur.max())}, avg:{_fmt(cur.mean())}]"
                    )
            out.append(f"{indent}{desc}")
            return out

        # ---------- scalars / strings / others ----------
        if isinstance(cur, (int, float, complex, np.generic)):
            out.append(f"{indent}scalar {type(cur).__name__} [value: {_fmt(cur)}]")
        elif isinstance(cur, str):
            out.append(f"{indent}str [length: {len(cur)}]")
        else:
            out.append(f"{indent}{type(cur).__name__}")
        return out

    # Detect variable name for top-level object
    var_name = "unknown"
    frame = inspect.currentframe().f_back
    for n, v in frame.f_locals.items():
        if v is obj:
            var_name = n
            break

    lines = _lines(obj, 0, top=True, name=var_name)
    report = "\n".join(lines) + "\n"
    subprocess.run("clip", universal_newlines=True, input=report)
    print(report, end="")