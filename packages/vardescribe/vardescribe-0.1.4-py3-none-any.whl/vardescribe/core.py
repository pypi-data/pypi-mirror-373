# src/vardescribe/core.py

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
                f"{indent}dataframe '{name}' with {len(cur)} rows, {cur.shape[1]} columns"
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
                f"{indent}dict '{name}' with {len(cur)} keys"
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
            header = (
                f"{indent}list '{name}' size({len(cur)}){info}"
                if top and name
                else f"{indent}list size({len(cur)}){info}"
            )
            out.append(header)
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
            header = (
                f"{indent}tuple {name} size({len(cur)}){info}"
                if top and name
                else f"{indent}tuple size({len(cur)}){info}"
            )
            out.append(header)
            if cur:
                out.extend(_lines(cur[0], lvl + 1))
            return out

# ---------- ndarray or similar ----------
        if hasattr(cur, "shape"):
            # Handle scalar arrays (0-dimensional)
            if cur.shape == ():
                type_name = "scalar"
                details = f"{cur.dtype}"
                if cur.size:
                    details += f" [value: {_fmt(cur.item())}]"
            # Handle ndarrays (1-dimensional or more)
            else:
                type_name = "ndarray"
                details = f"size{tuple(cur.shape)} {cur.dtype}"
                if cur.size and np.issubdtype(cur.dtype, np.number):
                    details += (
                        f" [min:{_fmt(cur.min())}, max:{_fmt(cur.max())}, avg:{_fmt(cur.mean())}]"
                    )

            # Conditionally construct the final description string
            if top and name:
                # If it's the top-level variable, insert the name in the middle
                desc = f"{type_name} '{name}' {details}"
            else:
                # Otherwise, use the standard format
                desc = f"{type_name} {details}"
                
            out.append(f"{indent}{desc}")
            return out

# ---------- scalars / strings / others ----------
        type_name = ""
        details = ""

        if isinstance(cur, (int, float, complex, np.generic)):
            type_name = "scalar"
            details = f"{type(cur).__name__} [value: {_fmt(cur)}]"
        elif isinstance(cur, str):
            type_name = "str"
            details = f"[length: {len(cur)}]"
        else:
            # For any other types, the name is the full description
            type_name = f"{type(cur).__name__}"
            details = ""

        # Conditionally construct the final description string
        if top and name:
            # If it's the top-level variable, insert the name in the middle
            # .strip() handles cases where details might be empty
            desc = f"{type_name} '{name}' {details}".strip()
        else:
            # Otherwise, use the standard format
            desc = f"{type_name} {details}".strip()
            
        out.append(f"{indent}{desc}")
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
    # The original function included a copy-to-clipboard functionality
    # which may not be desired in all environments. It can be uncommented if needed.
    # try:
    #     subprocess.run("clip", universal_newlines=True, input=report, check=True)
    # except (FileNotFoundError, subprocess.CalledProcessError):
    #     pass # Handle cases where 'clip' is not available or fails
    print(report, end="")
