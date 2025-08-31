import marimo

__generated_with = "0.11.6"
app = marimo.App(width="full")


@app.cell
def _():
    import anywidget
    import traitlets
    return anywidget, traitlets


@app.cell
def _(anywidget, traitlets):
    class CounterWidget(anywidget.AnyWidget):
        _esm = """
        import ForceGraph3D from "https://esm.sh/3d-force-graph";
        const N = 300;
        const gData = {
          nodes: [...Array(N).keys()].map(i => ({ id: i })),
          links: [...Array(N).keys()]
            .filter(id => id)
            .map(id => ({
              source: id,
              target: Math.round(Math.random() * (id-1))
            }))
        };

        function render({ model, el }) {
            const create_plot = () => {
                return ForceGraph3D()(el)
                    .graphData(gData)
                }
            create_plot()
        }
        export default { render };
        """
        _css = """
        .counter-widget button { color: white; font-size: 1.75rem; background-color: #ea580c; padding: 0.5rem 1rem; border: none; border-radius: 0.25rem; }
        .counter-widget button:hover { background-color: #9a3412; }
        """
        value = traitlets.Int(0).tag(sync=True)
    return (CounterWidget,)


@app.cell
def _(CounterWidget):
    CounterWidget()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
