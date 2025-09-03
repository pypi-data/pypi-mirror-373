#!/usr/bin/env python3
helptext = """
Example Options:
  data.npy
  data.npy -i w h
  data.npy -i * c w h
  data.npy -i * c ...       # will automatically pick w, h
  data.npy -i *             # will automatically pick c, w, h
  data.npy -i c w h100:200
  data.npy -i *10:20 w h c

Index specs for -i are given for each axis in order.
They can be any of:
- "*" marks the interactive axis. Example: "*" or as prefix: "*10:20".
- Prefix "w" or "h" marks width or height axis. Example: "w", "h", "w0:100", etc.
- Optional "c" marks a color axis. Can be "c", "c:...", etc.
- Single integer -> constant index for that axis.
- numpy-like slices with ":", e.g. ":", "10:100", "0:100:2".
- Comma-separated list "2,5,7" selects those indices (order is kept).
  Can optionally be wrapped in "()" or "[]" without effect on behavior.
- "..." fills remaining axes with ":".

If no "w" or "h" is given, the two largest remaining axes are used as (w,h),\
with w being the larger of the two.
If no "c" is given, all remaining axes except (w,h) are treated as color axes.

Colors are computed as follows:
- If color dimension count = 1 -> greyscale.
- If color dimension count = 2 -> mapped to R and B, G=0.
- If color channels > 3 -> reduced to 3 via PCA across the color axes of the displayed frame.

Interactive Controls:
- Left/Down: previous index on the "*" axis
- Right/Up: next index on the "*" axis
- "0": reset to initial index
- "q" or "escape": close
"""

import argparse
from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np


# ---------- Parsing ----------

class DimSpec:
    def __init__(self,
                 role=None,
                 is_interactive=False,
                 slc: Optional[slice] = None,
                 indices: Optional[List[int]] = None):
        self.role = role  # None | 'w' | 'h' | 'c'
        self.is_interactive = is_interactive
        self.slc = slc  # slice or None
        self.indices = indices  # list[int] or None


def _clean_token(tok: str) -> str:
    # remove whitespace and outer brackets
    tok = tok.strip()
    if tok.startswith("(") and tok.endswith(")"):
        tok = tok[1:-1]
    if tok.startswith("[") and tok.endswith("]"):
        tok = tok[1:-1]
    return tok.strip()


def _parse_range(tok: str) -> Tuple[slice, Optional[List[int]]]:
    """
    :param tok: token string
    :return: (slice, indices) where indices is a list of ints or None
    """
    tok = tok.strip()
    if tok == "" or tok == ":":
        return slice(None, None, None), None
    if "," in tok:
        parts = [p for p in tok.split(",") if p.strip() != ""]
        idxs = [int(p.strip()) for p in parts]
        return slice(None, None, None), idxs
    if ":" in tok:
        parts = tok.split(":")
        a = int(parts[0]) if parts[0] != "" else None
        b = int(parts[1]) if len(parts) > 1 and parts[1] != "" else None
        c = int(parts[2]) if len(parts) > 2 and parts[2] != "" else None
        return slice(a, b, c), None
    # single number -> keep axis with width 1
    x = int(tok)
    return slice(x, x + 1, None), None


def parse_index_specs(spec_items: List[str], ndim: int) -> List[DimSpec]:
    # Expand "..." if present. Allow comma-separated tokens within one item.
    tokens: List[str] = []
    for s in spec_items:
        s = s.strip()
        if s == "":
            continue
        # allow a single argument like "...,w,h"
        if "," in s and not any(ch in s for ch in ("[", "]", "(", ")")):
            tokens.extend([t for t in s.split(",")])
        else:
            tokens.append(s)

    # Handle ellipsis
    if "..." in tokens:
        k = tokens.index("...")
        left = tokens[:k]
        right = tokens[k + 1:]
        needed = max(0, ndim - (len(left) + len(right)))
        tokens = left + [":" for _ in range(needed)] + right

    # Pad or trim to ndim
    if len(tokens) < ndim:
        tokens += [":" for _ in range(ndim - len(tokens))]
    if len(tokens) > ndim:
        raise ValueError(f"Too many index specs ({len(tokens)}) for array ndim={ndim}")

    out: List[DimSpec] = []
    interactive_seen = False
    for t in tokens:
        t = _clean_token(t)
        is_interactive = False
        if t.startswith("*"):
            is_interactive = True
            t = t[1:].strip()
            if t == "":
                t = ":"

        role = None
        # role prefixes 'w','h','c' allowed without separator
        if len(t) >= 1 and t[0] in ("w", "h", "c"):
            role = t[0]
            t = t[1:].strip()
            if t == "":
                t = ":"

        slc, idxs = _parse_range(t)
        spec = DimSpec(role=role, is_interactive=is_interactive, slc=slc, indices=idxs)
        if spec.is_interactive:
            if interactive_seen:
                # only first "*" is honored
                spec.is_interactive = False
            else:
                interactive_seen = True
        out.append(spec)
    return out


# ---------- Slicing plan ----------

class SlicePlan:
    def __init__(self, base_slices: List[slice], list_axes: List[Tuple[int, List[int]]],
                 roles: List[Optional[str]], interactive_axis: Optional[int]):
        self.base_slices = base_slices
        self.list_axes = list_axes
        self.roles = roles
        self.interactive_axis = interactive_axis


def build_plan(arr: np.ndarray, specs: List[DimSpec]) -> SlicePlan:
    if arr.ndim != len(specs):
        raise ValueError("specs length mismatch")

    base_slices: List[slice] = []
    list_axes: List[Tuple[int, List[int]]] = []
    roles: List[Optional[str]] = []
    interactive_axis: Optional[int] = None

    for ax, sp in enumerate(specs):
        roles.append(sp.role)
        if sp.is_interactive:
            interactive_axis = ax
        # always keep dimension using a slice
        slc = sp.slc if sp.slc is not None else slice(None)
        base_slices.append(slc)
        if sp.indices is not None:
            list_axes.append((ax, sp.indices))

    return SlicePlan(base_slices, list_axes, roles, interactive_axis)


def apply_plan(arr: np.ndarray, plan: SlicePlan) -> np.ndarray:
    sub = arr[tuple(plan.base_slices)]
    # apply list selections with take to preserve axes
    for ax, idxs in plan.list_axes:
        sub = np.take(sub, idxs, axis=ax)
    return sub


def apply_plan_with_index(arr: np.ndarray, specs: List[DimSpec], plan: SlicePlan, idx: Optional[int]) -> np.ndarray:
    # If interactive_axis is set and idx is not None, override its slice to select that single element
    if plan.interactive_axis is None or idx is None:
        return apply_plan(arr, plan)

    ax = plan.interactive_axis
    # compute the allowed indices along the interactive axis after base slice and optional list selection
    sp = specs[ax]
    # derive the concrete sequence of indices
    if sp.indices is not None:
        seq = sp.indices
    else:
        start, stop, step = sp.slc.start, sp.slc.stop, sp.slc.step
        length = arr.shape[ax]
        a = start if start is not None else 0
        b = stop if stop is not None else length
        c = step if step is not None else 1
        seq = list(range(a, b, c))
    if len(seq) == 0:
        raise ValueError("Interactive axis has empty index set")
    # clamp idx
    idx = max(0, min(idx, len(seq) - 1))
    chosen = seq[idx]

    # override base slice at that axis with chosen:chosen+1
    base = list(plan.base_slices)
    base[ax] = slice(chosen, chosen + 1, None)
    sub = arr[tuple(base)]
    # apply list selections
    for ax2, idxs in plan.list_axes:
        sub = np.take(sub, idxs, axis=ax2)
    return sub


# ---------- Image shaping ----------

def _find_axes(shape: Tuple[int, ...], roles: List[Optional[str]]) -> Tuple[int, int, List[int]]:
    # find w, h axes by roles; fall back to last two axes
    w_ax = None
    h_ax = None
    color_axes: List[int] = []

    for i, r in enumerate(roles):
        if r == 'w':
            w_ax = i
        elif r == 'h':
            h_ax = i

    # if not specified, choose last two axes as w,h (order w,h)
    if w_ax is None or h_ax is None:
        # choose by largest sizes
        axes_sorted = sorted(range(len(shape)), key=lambda i: (shape[i], i))
        # pick the two largest
        a, b = axes_sorted[-2], axes_sorted[-1]
        # set w to a, h to b
        if w_ax is None: w_ax = a
        if h_ax is None: h_ax = b

    # color axes: explicit 'c' or all others not w/h
    explicit_c = any(r == 'c' for r in roles)
    for i, r in enumerate(roles):
        if i in (w_ax, h_ax):
            continue
        if explicit_c:
            if r == 'c':
                color_axes.append(i)
        else:
            color_axes.append(i)

    # make sure w != h
    if w_ax == h_ax:
        raise ValueError("w and h axes resolve to the same axis")
    return w_ax, h_ax, color_axes


def _move_to_image(sub: np.ndarray, roles: List[Optional[str]]) -> np.ndarray:
    # returns (img, is_color). Expects sub to have kept singleton dims for fixed axes.
    shape = sub.shape
    w_ax, h_ax, c_axes = _find_axes(shape, roles)

    # move axes to (h, w, c_flat)
    axes_order = [h_ax, w_ax] + [ax for ax in range(sub.ndim) if ax not in (h_ax, w_ax)]
    x = np.moveaxis(sub, axes_order, range(sub.ndim))
    h, w = x.shape[0], x.shape[1]
    if x.ndim == 2:
        x = x.reshape(h, w, 1)
    else:
        c_flat = int(np.prod(x.shape[2:])) if len(x.shape) > 2 else 1
        x = x.reshape(h, w, c_flat)

    # convert to displayable image
    if x.shape[2] == 1:
        # black-white
        img = x[..., 0]
        img = _normalize_01(img)
        return img
    if x.shape[2] == 2:
        # map to R and B, G=0
        r = _normalize_01(x[..., 0])
        b = _normalize_01(x[..., 1])
        g = np.zeros_like(r)
        img = np.stack([r, g, b], axis=-1)
        return img
    if x.shape[2] == 3:
        # map to RGB
        img = np.stack([_normalize_01(x[..., 0]),
                        _normalize_01(x[..., 1]),
                        _normalize_01(x[..., 2])], axis=-1)
        return img
    # channels > 3 -> PCA to 3
    img = _pca_to_rgb(x)
    return img


def _normalize_01(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float32)
    finite = np.isfinite(a)
    if not np.any(finite):
        return np.zeros_like(a, dtype=np.float32)
    mn = np.nanmin(a[finite])
    mx = np.nanmax(a[finite])
    if mx == mn:
        return np.zeros_like(a, dtype=np.float32)
    out = (a - mn) / (mx - mn)
    out[~finite] = 0.0
    return out


def _pca_to_rgb(x_hwk: np.ndarray) -> np.ndarray:
    # x shape (h,w,k). Flatten to (n,k), center, SVD, take top 3
    h, w, k = x_hwk.shape
    X = x_hwk.reshape(-1, k).astype(np.float32)
    # center
    mean = np.nanmean(X, axis=0, keepdims=True)
    Xc = np.where(np.isfinite(X), X - mean, 0.0)
    # SVD on covariance across channels (k x k) via economy SVD on Xc (n x k)
    # Compute SVD of Xc with shape (n, k)
    try:
        U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
        W = Xc @ Vt[:3].T  # (n,3)
        # normalize each component to 0..1
        W0 = _normalize_01(W[:, 0])
        W1 = _normalize_01(W[:, 1]) if W.shape[1] > 1 else np.zeros_like(W0)
        W2 = _normalize_01(W[:, 2]) if W.shape[1] > 2 else np.zeros_like(W0)
        rgb = np.stack([W0, W1, W2], axis=-1).reshape(h, w, 3)
    except np.linalg.LinAlgError:
        # fallback: take first three channels normalized
        rgb = np.stack([_normalize_01(x_hwk[..., i % k]) for i in range(3)], axis=-1)
    return rgb


# ---------- Plotting and interaction ----------

def display_interactive(window_title: str,
                        arr: np.ndarray,
                        specs: List[DimSpec],
                        plan: SlicePlan,
                        interactive_index_start: int):
    # Determine interactive sequence length
    ax = plan.interactive_axis
    if ax is None:
        # static
        sub = apply_plan(arr, plan)
        img = _move_to_image(sub, plan.roles)
        _show_image(img, title=None)
        return

    # build index sequence
    sp = specs[ax]
    if sp.indices is not None:
        seq = sp.indices
    else:
        start, stop, step = sp.slc.start, sp.slc.stop, sp.slc.step
        length = arr.shape[ax]
        a = start if start is not None else 0
        b = stop if stop is not None else length
        c = step if step is not None else 1
        seq = list(range(a, b, c))
    if len(seq) == 0:
        raise ValueError("Interactive axis has empty index set")

    # compute initial_seq_index from interactive_index_start
    if interactive_index_start is None:
        interactive_index_start = 0
    initial_seq_index = 0
    if interactive_index_start <= seq[0]:
        initial_seq_index = 0
    elif interactive_index_start >= seq[-1]:
        initial_seq_index = len(seq) - 1
    else:
        # pick the closest index (floor)
        for i, v in enumerate(seq):
            if v > interactive_index_start:
                initial_seq_index = i - 1
                break

    state = {"i": initial_seq_index}

    def title():
        return f"dim {plan.interactive_axis} = {seq[state['i']]}  ({state['i'] + 1}/{len(seq)})"

    # initial display
    sub0 = apply_plan_with_index(arr, specs, plan, state["i"])
    img0 = _move_to_image(sub0, plan.roles)
    fig, axp = plt.subplots()
    fig.canvas.manager.set_window_title(window_title)
    handle = axp.imshow(img0, interpolation="nearest")
    if img0.ndim == 2:
        handle.set_clim(vmin=0.0, vmax=1.0)
        handle.set_cmap("gray")
    axp.set_title(title())
    axp.axis("off")

    def redraw():
        sub = apply_plan_with_index(arr, specs, plan, state["i"])
        img = _move_to_image(sub, plan.roles)
        handle.set_data(img)
        if img.ndim == 2:
            handle.set_clim(vmin=0.0, vmax=1.0)
            handle.set_cmap("gray")
        axp.set_title(title())
        fig.canvas.draw_idle()

    def on_key(event):
        if event.key in ("right", "down"):
            if state["i"] < len(seq) - 1:
                state["i"] += 1
                redraw()
        elif event.key in ("left", "up"):
            if state["i"] > 0:
                state["i"] -= 1
                redraw()
        elif event.key == "0":
            state["i"] = initial_seq_index
            redraw()
        elif event.key in ("q", "escape"):
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", on_key)

    def on_scroll(event):
        if event.button == "down":
            if state["i"] < len(seq) - 1:
                state["i"] += 1
                redraw()
        elif event.button == "up":
            if state["i"] > 0:
                state["i"] -= 1
                redraw()

    fig.canvas.mpl_connect("scroll_event", on_scroll)

    plt.show()


def _show_image(img: np.ndarray, title: Optional[str]):
    plt.figure()
    if img.ndim == 2:
        plt.imshow(img, interpolation="nearest", cmap="gray", vmin=0.0, vmax=1.0)
    else:
        plt.imshow(img, interpolation="nearest")
    if title:
        plt.title(title)
    plt.axis("off")
    plt.show()


# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(description="Render a slice of a .npy array as an image.",
                                epilog=helptext,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("npy_path", help=".npy file path")
    p.add_argument("-i", "--index", nargs="*", default=[],
                   help="Index specs for each axis. See explanation below.")
    p.add_argument("-s", "--start", type=int, default=None,
                   help="Start index for the interactive axis.")
    args = p.parse_args()

    arr = np.load(args.npy_path, allow_pickle=False)
    specs = parse_index_specs(args.index, arr.ndim)
    plan = build_plan(arr, specs)
    display_interactive(args.npy_path, arr, specs, plan, args.start)


if __name__ == "__main__":
    main()
