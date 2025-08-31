import marimo

__generated_with = "0.11.6"
app = marimo.App(width="full")


@app.cell
def _():
    import graph_widget
    import marimo as mo
    return graph_widget, mo


@app.cell
def _():
    data2 = {'nodes':
            [{"id": 1, "kind": "sample"},
            {"id": 2, "kind": "sample"},
            {"id": 3, "kind": "OTU", "degree": 3},
            {"id": 4, "kind": "OTU", "degree": 2},
            {"id": 5, "kind": "OTU", "degree": 3}],
            "links": [
                {"source": 1, "target": 3},
                {"source": 1, "target": 4},
                {"source": 1, "target": 5},
                {"source": 2, "target": 3},
                {"source": 1, "target": 4},
                {"source": 1, "target": 5},
                {"source": 2, "target": 3},
                {"source": 2, "target": 5},
            ]}
    return (data2,)


@app.cell
def _(data2, mo):
    repulsion_slider2 = mo.ui.slider(
        start=-100, stop=500, step=10, value=1, debounce=False, label="Repulsion"
    )
    node_scale_slider2 = mo.ui.slider(
        start=1, stop=20, step=1, value=3, debounce=True, label="Node scale"
    )
    colour_feature_dropdown2 = mo.ui.dropdown(
        options=list(data2["nodes"][3].keys()), value="kind", label="Colour by"
    )
    return colour_feature_dropdown2, node_scale_slider2, repulsion_slider2


@app.cell
def _(
    colour_feature_dropdown2,
    data2,
    graph_widget,
    mo,
    node_scale_slider2,
    repulsion_slider2,
):
    data_graph2 = mo.ui.anywidget(
        graph_widget.ForceGraphWidget(
            data=data2,
            repulsion=repulsion_slider2.value,
            node_scale=node_scale_slider2.value,
            colour_feature=colour_feature_dropdown2.value
        )
    )
    return (data_graph2,)


@app.cell
def _(
    colour_feature_dropdown2,
    data_graph2,
    mo,
    node_scale_slider2,
    repulsion_slider2,
):
    plot2 = mo.hstack([data_graph2,
                mo.vstack([
                    repulsion_slider2,
                    node_scale_slider2,
                    colour_feature_dropdown2])], justify="start")
    return (plot2,)


@app.cell
def _(plot2):
    plot2
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
