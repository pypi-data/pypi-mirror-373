"""
Diagnostic utilities for matched samples (ESS, covariate balance, plots, overlap via KDE), with before vs. after comparison
"""

from __future__ import annotations

from typing import Any, NamedTuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.stats import gaussian_kde


class BalanceTablesMulti(NamedTuple):
    ess: dict[str, Any]  # {"pre_match": dict[str,int], "per_draw": dict[str,ndarray], "combined": float}
    pre_match: pd.DataFrame  # idx = (covariate, pair) with ASMD & VarRatio before matching
    per_sample: pd.DataFrame  # idx = (draw, covariate, pair)  if G>2  else (draw,cov)
    summary: pd.DataFrame  # covariate × {"mean","q90","max"}
    fig: plt.Figure | None


BalanceTables = BalanceTablesMulti  # backward-compat alias

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _asmd(x_t: NDArray[np.floating], x_c: NDArray[np.floating]) -> NDArray[np.floating]:
    mean_t, mean_c = x_t.mean(0), x_c.mean(0)
    var_t, var_c = x_t.var(0, ddof=1), x_c.var(0, ddof=1)
    pooled_sd = np.sqrt((var_t + var_c) / 2.0)
    pooled_sd = np.where(pooled_sd == 0, np.nan, pooled_sd)
    return np.abs(mean_t - mean_c) / pooled_sd


def _var_ratio(
    x_t: NDArray[np.floating], x_c: NDArray[np.floating]
) -> NDArray[np.floating]:
    var_t, var_c = x_t.var(0, ddof=1), x_c.var(0, ddof=1)
    return np.where(var_c == 0, np.nan, var_t / var_c)


def _groupwise_ess(
    mask_mat: NDArray[np.bool_], groups: NDArray[np.integer]
) -> tuple[np.ndarray, float]:
    """
    mask_mat : (n_obs, n_draws)  – True where obs is matched in draw d
    groups   : (n_obs,)          – integer codes 0..G-1

    Returns
    -------
    per_draw : ndarray shape (G, n_draws)
    combined : float
    """
    G = np.unique(groups).size
    n_draws = mask_mat.shape[1]
    per_draw = np.zeros((G, n_draws), int)
    for g in range(G):
        per_draw[g] = (mask_mat & (groups[:, None] == g)).sum(0)

    counts = mask_mat.sum(1)  # how many draws each obs appears in
    w = counts / n_draws

    if w.size and w.sum() > 0:
        combined = (w.sum() ** 2) / np.sum(w**2)
    else:
        combined = 0.0

    return per_draw, float(combined)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def summarize_matching(
    cluster_ids: NDArray[np.integer],
    X,
    *,
    treatment: NDArray[np.integer] | None = None,
    ref_group: int | str | None = None,
    plot: bool = True,
) -> BalanceTablesMulti:
    """Compute balance diagnostics for matched samples.

    Parameters
    ----------
    cluster_ids : ndarray
        Matrix of cluster identifiers as returned by :func:`stochastic_match`.
    X : array-like or DataFrame
        Covariate matrix used to compute balance.
    treatment : ndarray, optional
        Treatment assignments corresponding to ``X``.
    ref_group : int or str, optional
        Reference treatment level when more than two arms are present.
    plot : bool, default ``True``
        If ``True`` return a :class:`matplotlib.figure.Figure` visualising
        distributions before and after matching.

    Returns
    -------
    BalanceTablesMulti
        Named tuple containing ESS, pre- and post-matching covariate summaries
        and optionally a figure.
    """
    # ---- basic shape checks ------------------------------------------
    cluster_ids = np.asarray(cluster_ids, dtype=int)
    if cluster_ids.ndim == 1:
        cluster_ids = cluster_ids[:, None]
    n_obs, n_draws = cluster_ids.shape

    # ---- covariate matrix --------------------------------------------
    if isinstance(X, pd.DataFrame):
        cov_names = X.columns.to_list()
        X = X.values
    else:
        X = np.asarray(X, dtype=float)
        cov_names = [f"x{i}" for i in range(X.shape[1])]
    if X.shape[0] != n_obs:
        raise ValueError("X and cluster_ids must align on rows.")

    # ---- treatment vector --------------------------------------------
    if treatment is None:
        raise ValueError("`treatment` must be supplied for multi-arm diagnostics.")
    treatment = np.asarray(treatment)
    if treatment.shape[0] != n_obs:
        raise ValueError("`treatment` length mismatch.")

    groups_unique = np.unique(treatment)
    G = groups_unique.size
    if G == 2 and ref_group is None:
        ref_group = groups_unique.max()  # preserve old “treated=1” heuristic
    if G > 2 and ref_group is None:
        raise ValueError("With >2 treatment arms you must give `ref_group`.")
    if ref_group not in groups_unique:
        raise ValueError("`ref_group` not found in treatment labels.")

    # integer-encode groups 0..G-1  (keeps plotting colours stable)
    grp_codes = {g: i for i, g in enumerate(groups_unique)}
    g_vec = np.vectorize(grp_codes.get)(treatment)
    ref_code = grp_codes[ref_group]

    # ---- ESS ----------------------------------------------------------
    matched_mask = cluster_ids >= 0  # bool matrix
    per_draw_ess, combined_ess = _groupwise_ess(matched_mask, g_vec)

    pre_counts = {groups_unique[g]: int((g_vec == g).sum()) for g in range(G)}
    per_draw_dict = {
        groups_unique[g]: per_draw_ess[g].astype(int) for g in range(G)
    }
    ess_dict = {
        "pre_match": pre_counts,
        "per_draw": per_draw_dict,
        "combined": combined_ess,
    }

    # ---- Balance computation -----------------------------------------
    records: list[dict[str, Any]] = []
    other_codes = [c for c in range(G) if c != ref_code]
    pairs = [(ref_code, c) for c in other_codes]

    # ---- Pre-matching ASMD and VarRatio ------------------------------
    pre_records: list[dict[str, Any]] = []
    m_ref_all = g_vec == ref_code
    for g1 in other_codes:
        m_other = g_vec == g1
        if not m_ref_all.any() or not m_other.any():
            continue
        asmd = _asmd(X[m_ref_all], X[m_other])
        vrat = _var_ratio(X[m_ref_all], X[m_other])
        for k, (a, v) in enumerate(zip(asmd, vrat)):
            pre_records.append(
                {
                    "pair": f"{groups_unique[g1]}_vs_{groups_unique[ref_code]}",
                    "covariate": cov_names[k],
                    "ASMD": a,
                    "VarRatio": v,
                }
            )
    pre_match = (
        pd.DataFrame.from_records(pre_records)
        .set_index(["covariate", "pair"])
        .sort_index()
    )

    for d in range(n_draws):
        m_d = matched_mask[:, d]
        for g0, g1 in pairs:
            m0 = m_d & (g_vec == g0)
            m1 = m_d & (g_vec == g1)
            if m0.sum() == 0 or m1.sum() == 0:
                continue
            asmd = _asmd(X[m0], X[m1])
            vrat = _var_ratio(X[m0], X[m1])
            for k, (a, v) in enumerate(zip(asmd, vrat)):
                records.append(
                    {
                        "draw": d,
                        "pair": f"{groups_unique[g1]}_vs_{groups_unique[g0]}",
                        "covariate": cov_names[k],
                        "ASMD": a,
                        "VarRatio": v,
                    }
                )

    per_sample = (
        pd.DataFrame.from_records(records)
        .set_index(["draw", "covariate", "pair"])
        .sort_index()
    )

    def q90(s):
        return s.quantile(0.9, interpolation="higher")

    summary = (
        per_sample.groupby("covariate")
        .agg(mean=("ASMD", "mean"), q90=("ASMD", q90), max=("ASMD", "max"))
        .reindex(cov_names)
    )

    # ---- Plotting -----------------------------------------------------
    fig: plt.Figure | None = None
    if plot:
        colors = plt.get_cmap("tab10")(range(G))
        # Define different markers for each group to help distinguish in greyscale
        markers = ['o', 's', '^', 'v', 'D', 'p', '*', 'h', 'H', '+', 'x']
        pair_colors = {
            f"{groups_unique[g]}_vs_{groups_unique[ref_code]}": colors[g]
            for g in other_codes
        }
        n_rows = 1 + len(cov_names)
        fig, axes = plt.subplots(n_rows, 2, figsize=(12, 2 * n_rows))

        # Row-0 dot-plot of ASMD after matching
        ax0 = axes[0, 1]
        after_vals: list[np.ndarray] = []
        for i, (pair, grp) in enumerate(per_sample.groupby("pair")):
            vals = grp.groupby("covariate")["ASMD"].mean().reindex(cov_names)
            marker = markers[i % len(markers)]
            ax0.scatter(
                vals,
                cov_names,
                label=pair,
                color=pair_colors.get(pair, colors[0]),
                marker=marker,
                s=50,  # Make markers slightly larger for visibility
            )
            after_vals.append(vals.to_numpy())
        ax0.axvline(0.1, ls="--", color="gray")
        ax0.set_title("ASMD After Matching")
        ax0.set_xlabel("ASMD")

        # Row-0 bar of ASMD before (ref vs each)
        ax_b0 = axes[0, 0]
        before_vals: list[np.ndarray] = []
        before_handles = []
        before_labels = []
        for i, g in enumerate(other_codes):
            m0 = g_vec == ref_code
            m1 = g_vec == g
            vals = _asmd(X[m0], X[m1])
            marker = markers[i % len(markers)]
            handle = ax_b0.scatter(
                vals,
                cov_names,
                label=f"{groups_unique[g]} vs {groups_unique[ref_code]}",
                color=colors[g],
                marker=marker,
                s=50,  # Make markers slightly larger for visibility
            )
            before_handles.append(handle)
            before_labels.append(f"{groups_unique[g]} vs {groups_unique[ref_code]}")
            before_vals.append(vals)
        ax_b0.axvline(0.1, ls="--", color="gray")
        ax_b0.set_title("ASMD Before Matching")
        ax_b0.set_xlabel("ASMD")

        # Use identical x-limits for before & after plots
        if after_vals or before_vals:
            all_vals = np.concatenate(after_vals + before_vals)
            xmin = 0.0
            xmax = float(np.nanmax(all_vals)) if all_vals.size else 1.0
            ax0.set_xlim(xmin, xmax)
            ax_b0.set_xlim(xmin, xmax)

        # -----------------------------------------------------------------
        # Density rows — weight every unit by its matching frequency
        # -----------------------------------------------------------------
        freq = matched_mask.sum(1).astype(float)  # 0‥n_draws for each row

        for i, name in enumerate(cov_names, start=1):
            before_xs: list[np.ndarray] = []
            after_xs: list[np.ndarray] = []

            # BEFORE densities (unmatched sample, unweighted)
            axL = axes[i, 0]
            for g in range(G):
                xs = X[g_vec == g, i - 1]
                before_xs.append(xs)
                if xs.size > 1:
                    kde = gaussian_kde(xs)
                    grid = np.linspace(xs.min(), xs.max(), 200)
                    axL.plot(
                        grid, kde(grid), color=colors[g], label=str(groups_unique[g])
                    )
            axL.set_title(f"Before: {name}")
            axL.set_xlabel(name)

            # AFTER densities (matched sample, weighted by freq)
            axR = axes[i, 1]
            for g in range(G):
                mask_g = g_vec == g
                xs_all = X[mask_g, i - 1]
                w_all = freq[mask_g]

                keep = w_all > 0  # appeared in ≥1 draw
                xs, w = xs_all[keep], w_all[keep]
                after_xs.append(xs)

                if xs.size > 1 and np.any(w):
                    kde = gaussian_kde(xs, weights=w)
                    grid = np.linspace(xs.min(), xs.max(), 200)
                    axR.plot(
                        grid, kde(grid), color=colors[g], label=str(groups_unique[g])
                    )
            axR.set_title(f"After: {name}")
            axR.set_xlabel(name)

            # Align x-limits across before/after panels
            if before_xs or after_xs:
                all_vals = np.concatenate(before_xs + after_xs)
                xmin = float(np.nanmin(all_vals)) if all_vals.size else 0.0
                xmax = float(np.nanmax(all_vals)) if all_vals.size else 1.0
                axL.set_xlim(xmin, xmax)
                axR.set_xlim(xmin, xmax)

        # Get handles and labels for the density plot legend (group colors)
        handles, labels = axL.get_legend_handles_labels()
        
        # Position ASMD legend at the top right
        # Use single legend for treatment groups (applies to both before and after plots)
        fig.legend(before_handles, before_labels, 
                  loc="upper right", title="ASMD Comparisons", 
                  bbox_to_anchor=(0.98, 0.98), fontsize="small")
        
        # Position the density plot legend below the ASMD legend
        fig.legend(handles, labels, loc="center right", title="Group", bbox_to_anchor=(0.98, 0.7))
        
        plt.tight_layout(rect=(0, 0, 0.82, 1))  # Leave more space on the right for legends

    return BalanceTablesMulti(
        ess=ess_dict,
        pre_match=pre_match,
        per_sample=per_sample,
        summary=summary,
        fig=fig,
    )
