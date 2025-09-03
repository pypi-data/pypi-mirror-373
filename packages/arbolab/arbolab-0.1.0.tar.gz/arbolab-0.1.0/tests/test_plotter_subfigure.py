import matplotlib.pyplot as plt

from arbolab.plotting import Plotter


def test_to_matplotlib_figure_from_subfigure() -> None:
    plotter = Plotter()
    fig = plt.figure()
    subfig = fig.subfigures(1, 1, squeeze=False)[0][0]
    result = plotter._to_matplotlib_figure(subfig)
    assert result is fig
    plt.close(fig)
