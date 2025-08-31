import numpy as np
import pandas as pd

from causalem import summarize_matching


def test_multiarm_diagnostics_runs():
    rng = np.random.default_rng(0)
    n_per = 30
    t = np.repeat([0, 1, 2], n_per)
    # fake covariates
    X = pd.DataFrame(
        {
            "age": rng.integers(10, 60, size=t.size),
            "bmi": rng.normal(25, 3, size=t.size),
        }
    )
    # clusters: deterministic one-of-each id (every consecutive triple)
    cid = -np.ones((t.size, 1), int)
    cid[:, 0] = np.repeat(np.arange(n_per), 3)

    diag = summarize_matching(cid, X, treatment=t, ref_group=0, plot=False)

    assert "combined" in diag.ess
    assert isinstance(diag.ess["combined"], float)
    assert diag.ess["combined"] > 0

    assert "pre_match" in diag.ess
    assert isinstance(diag.ess["pre_match"], dict)
    assert diag.ess["pre_match"][0] == n_per

    assert "per_draw" in diag.ess
    assert isinstance(diag.ess["per_draw"], dict)
    assert diag.ess["per_draw"][1].shape == (1,)

    assert isinstance(diag.pre_match, pd.DataFrame)
    assert "VarRatio" in diag.pre_match.columns
    assert diag.pre_match.index.nlevels == 2  # covariate,pair
    assert diag.per_sample.index.nlevels == 3  # draw,cov,pair
    assert diag.summary.shape[0] == 2  # two covariates


def test_legend_labels_and_order():
    """Test that legend labels use actual reference group names and are in correct order."""
    rng = np.random.default_rng(42)
    n_per = 20
    # Three treatment groups with string names
    t = np.repeat(["Control", "TreatmentA", "TreatmentB"], n_per)
    
    # fake covariates
    X = pd.DataFrame(
        {
            "age": rng.integers(10, 60, size=t.size),
            "bmi": rng.normal(25, 3, size=t.size),
        }
    )
    # clusters: deterministic one-of-each id (every consecutive triple)
    cid = -np.ones((t.size, 1), int)
    cid[:, 0] = np.repeat(np.arange(n_per), 3)

    diag = summarize_matching(cid, X, treatment=t, ref_group="Control", plot=True)

    assert diag.fig is not None, "Figure should be generated when plot=True"
    
    # Check that we have exactly 2 legends
    assert len(diag.fig.legends) == 2, "Should have exactly 2 legends"
    
    # Get legend information
    legends_info = []
    for legend in diag.fig.legends:
        title = legend.get_title().get_text()
        labels = [text.get_text() for text in legend.get_texts()]
        position = legend.get_bbox_to_anchor()
        legends_info.append({
            'title': title,
            'labels': labels,
            'position': position
        })
    
    # Find the ASMD and Group legends
    asmd_legend = next((l for l in legends_info if l['title'] == 'ASMD Comparisons'), None)
    group_legend = next((l for l in legends_info if l['title'] == 'Group'), None)
    
    assert asmd_legend is not None, "ASMD Comparisons legend should exist"
    assert group_legend is not None, "Group legend should exist"
    
    # Test 1: ASMD labels should use actual reference group name, not "ref"
    for label in asmd_legend['labels']:
        assert "vs ref" not in label, f"Label '{label}' should not contain hardcoded 'ref'"
        assert "vs Control" in label, f"Label '{label}' should contain actual reference group name 'Control'"
    
    # Test 2: ASMD legend should be positioned above Group legend (higher y position)
    asmd_y = asmd_legend['position'].y0
    group_y = group_legend['position'].y0
    assert asmd_y > group_y, "ASMD legend should be positioned above Group legend"
    
    # Clean up
    import matplotlib.pyplot as plt
    plt.close(diag.fig)
