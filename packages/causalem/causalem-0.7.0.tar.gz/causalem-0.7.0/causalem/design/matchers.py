"""
causalem.design.matchers
~~~~~~~~~~~~~~~~~~~~~~~~
Stochastic/deterministic nearest-neighbour matching.

* Binary  (treated vs control) ................... _match_binary()
* Multi-arm “one-of-each” ........................ _match_one_of_each()

The public wrapper ``stochastic_match`` dispatches to the correct helper
based on the number of unique treatment levels.
"""

from __future__ import annotations

from typing import Any, Dict, List, TypeAlias

import numpy as np
from numpy.typing import NDArray

# --------------------------------------------------------------------------- #
# Public type aliases                                                         #
# --------------------------------------------------------------------------- #
Mask: TypeAlias = NDArray[Any]  # bool vector, length n_obs
Weights: TypeAlias = NDArray[Any]  # float vector, length n_obs
ClusterId: TypeAlias = NDArray[Any]  # int   vector, length n_obs


# --------------------------------------------------------------------------- #
# Shared utilities                                                            #
# --------------------------------------------------------------------------- #
def _prepare_distance(
    *,
    score: np.ndarray | None,
    distance: np.ndarray | None,
    n: int,
) -> NDArray[np.floating]:
    """
    Return an n×n symmetric distance matrix.

    Accepted inputs
    ---------------
    • score : 1-D array (n,) ..................... scalar score
              → d_{ij} = |s_i − s_j|
    • score : 2-D array (n, k) ................... k-dim vector (e.g. G−1 logits)
              → d_{ij} = L1-norm  ‖s_i − s_j‖₁
    • distance : pre-computed n×n matrix ........  used verbatim

    Exactly **one** of `score` or `distance` must be supplied.
    """
    # ---- mutual-exclusion check -----------------------------------------
    if (score is None) == (distance is None):
        raise ValueError("Pass exactly one of `score` or `distance`.")

    # ---- build from score -----------------------------------------------
    if score is not None:
        score = np.asarray(score, dtype=float)
        if score.ndim == 1:  # 1-D scalar score
            if score.shape[0] != n:
                raise ValueError("`score` must have length n.")
            return np.abs(score[:, None] - score[None, :])

        if score.ndim == 2:  # 2-D vector score
            if score.shape[0] != n:
                raise ValueError("First dimension of `score` must be n.")
            diff = score[:, None, :] - score[None, :, :]
            return np.abs(diff).sum(axis=2)  # L1 distance

        raise ValueError("`score` must be a 1-D or 2-D array.")

    # ---- check supplied distance ----------------------------------------
    distance = np.asarray(distance, dtype=float)
    if distance.shape != (n, n):
        raise ValueError("`distance` must be square (n×n).")
    return distance


# --------------------------------------------------------------------------- #
# 1.  Binary helper (logic identical to original function)                    #
# --------------------------------------------------------------------------- #
def _match_binary(
    *,
    treatment: np.ndarray,
    dist_mat: NDArray[np.floating],
    caliper: float | None,
    scale: float,
    nsmp: int,
    rng: np.random.Generator,
) -> NDArray[np.int_]:
    t = treatment
    n = t.size

    treated_all = np.where(t == 1)[0]
    control_all = set(np.where(t == 0)[0])

    # ---------------- deterministic ---------------------------------- #
    if nsmp == 0:
        cluster = np.full((n, 1), -1, int)
        controls = set(control_all)
        cid = 0
        for ti in treated_all:  # keep original order
            cand = np.array(sorted(controls))
            if cand.size == 0:
                break
            dists = dist_mat[ti, cand]
            if caliper is not None:
                m = dists <= caliper
                cand, dists = cand[m], dists[m]
            if cand.size == 0:
                continue
            ci = int(cand[np.argmin(dists)])
            cluster[[ti, ci], 0] = cid
            controls.remove(ci)
            cid += 1
        return cluster

    # ---------------- stochastic ------------------------------------- #
    cluster = np.full((n, nsmp), -1, int)
    for s in range(nsmp):
        treated = treated_all.tolist()
        controls = set(control_all)
        cid = 0
        while treated:
            ti = int(rng.choice(treated))
            treated.remove(ti)

            cand = np.array(sorted(controls))
            if cand.size == 0:
                continue
            dists = dist_mat[ti, cand]
            if caliper is not None:
                m = dists <= caliper
                cand, dists = cand[m], dists[m]
            if cand.size == 0:
                continue

            w = np.exp(-(dists - dists.min()) / scale)
            w_sum = w.sum()
            if w_sum <= 0 or not np.isfinite(w_sum):
                ci = int(cand[np.argmin(dists)])
            else:
                w /= w_sum
                ci = int(cand[rng.choice(len(cand), p=w)])
            cluster[[ti, ci], s] = cid
            controls.remove(ci)
            cid += 1
    return cluster


# --------------------------------------------------------------------------- #
# 2.  Multi-arm “one-of-each” helper                                          #
# --------------------------------------------------------------------------- #
def _match_one_of_each(
    *,
    treatment: np.ndarray,
    dist_mat: NDArray[np.floating],
    ref_group,
    caliper: float | None,
    scale: float,
    nsmp: int,
    rng: np.random.Generator,
) -> NDArray[np.int_]:
    t = treatment
    n = t.size
    groups: NDArray[Any] = np.unique(t)
    G = groups.size

    if ref_group not in groups:
        raise ValueError(f"`ref_group` {ref_group!r} not found in treatment labels.")
    ref_code = ref_group

    # index pools
    ref_pool_init = np.where(t == ref_code)[0]
    other_pools_init: Dict[Any, set[int]] = {
        g: set(np.where(t == g)[0]) for g in groups if g != ref_code
    }

    cluster = np.full((n, max(1, nsmp)), -1, int)

    # ------------------------------------------------------------------ #
    for s in range(max(1, nsmp)):
        # make fresh copies of the pools for this draw
        ref_pool = list(ref_pool_init)
        other_pools: Dict[Any, set[int]] = {
            g: set(v) for g, v in other_pools_init.items()
        }
        cid = 0

        while ref_pool:
            # pick anchor in reference group
            ti = ref_pool.pop(0) if nsmp == 0 else int(rng.choice(ref_pool))
            if nsmp != 0:
                ref_pool.remove(ti)

            members: List[int] = [ti]
            abort_cluster = False

            # iterate through the non-ref groups
            for g, pool in other_pools.items():
                if not pool:
                    abort_cluster = True
                    break
                cand = np.array(sorted(pool))
                dists = dist_mat[ti, cand]
                if caliper is not None:
                    m = dists <= caliper
                    cand, dists = cand[m], dists[m]
                if cand.size == 0:
                    abort_cluster = True
                    break

                if nsmp == 0:
                    j = int(cand[np.argmin(dists)])
                else:
                    w = np.exp(-(dists - dists.min()) / scale)
                    w_sum = w.sum()
                    if w_sum <= 0 or not np.isfinite(w_sum):
                        j = int(cand[np.argmin(dists)])
                    else:
                        w /= w_sum
                        j = int(cand[rng.choice(len(cand), p=w)])
                members.append(j)
            # did we get one from every group?
            if abort_cluster or len(members) != G:
                continue

            cluster[members, s] = cid
            cid += 1
            # remove chosen controls from their pools
            for j in members[1:]:
                other_pools[t[j]].remove(j)

    return cluster


# --------------------------------------------------------------------------- #
# 3.  Public dispatcher                                                       #
# --------------------------------------------------------------------------- #
def stochastic_match(
    *,
    treatment: np.ndarray,
    score: np.ndarray | None = None,
    distance: np.ndarray | None = None,
    ref_group: int | str | None = None,
    scale: float = 1.0,
    caliper: float | None = None,
    nsmp: int = 1,
    random_state: int | None = None,
) -> NDArray[np.int_]:
    """Match treated and control units using stochastic nearest neighbours.

    The function works for binary as well as multi-arm treatments.  When the
    treatment vector has exactly two unique labels and ``ref_group`` is
    ``None`` the behaviour reduces to the original 1:1 matching.  If more than
    two labels are present the user must specify ``ref_group`` and each
    resulting cluster will contain exactly one unit from every treatment level
    anchored on the reference arm.

    Parameters
    ----------
    treatment : ndarray of shape (n,)
        Treatment indicator with arbitrary labels.  Must contain at least two
        unique values.
    score : ndarray of shape (n,) or (n, k), optional
        Propensity scores or covariate distance features.  Exactly one of
        ``score`` or ``distance`` must be provided.
    distance : ndarray of shape (n, n), optional
        Pre-computed distance matrix used verbatim.
    ref_group : int or str, optional
        Label of the reference treatment arm for multi-arm matching.  Must be
        ``None`` for binary matching.
    scale : float, default ``1.0``
        Dispersion of the exponential weights used when ``nsmp > 0``.
    caliper : float or None, default ``None``
        Maximum allowable distance for a candidate match.  Pairs exceeding the
        caliper are discarded.
    nsmp : int, default ``1``
        Number of stochastic draws.  ``0`` performs deterministic matching.
    random_state : int or None, optional
        Seed controlling the random draws when ``nsmp > 0``.

    Returns
    -------
    ndarray of shape (n, ``max(nsmp, 1)``)
        Cluster identifiers for each observation.  ``-1`` denotes an unmatched
        unit.
    """
    if nsmp < 0:
        raise ValueError("`nsmp` must be ≥ 0")

    t = np.asarray(treatment)
    uniq = np.unique(t)
    G = uniq.size
    if G < 2:
        raise ValueError("Need at least two treatment levels.")

    n = t.size
    dist_mat = _prepare_distance(score=score, distance=distance, n=n)
    rng = np.random.default_rng(random_state)

    # ---- binary ----------------------------------------------------------- #
    if G == 2 and ref_group is None:
        # map labels to {0,1} to preserve legacy expectation
        t_bin = (t == uniq.max()).astype(int)
        return _match_binary(
            treatment=t_bin,
            dist_mat=dist_mat,
            caliper=caliper,
            scale=scale,
            nsmp=nsmp,
            rng=rng,
        )

    # ---- multi-arm -------------------------------------------------------- #
    if G == 2 and ref_group is not None:
        raise ValueError("`ref_group` given but only two treatment levels detected.")

    if ref_group is None:
        raise ValueError(
            "`ref_group` must be supplied when more than two treatment levels exist."
        )

    return _match_one_of_each(
        treatment=t,
        dist_mat=dist_mat,
        ref_group=ref_group,
        caliper=caliper,
        scale=scale,
        nsmp=nsmp,
        rng=rng,
    )
