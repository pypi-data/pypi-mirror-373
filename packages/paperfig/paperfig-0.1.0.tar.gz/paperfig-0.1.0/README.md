# paperfig: JSON‑driven figure orchestrator
`paperfig` is a small library for building per-figure PDFs from a JSON spec and combining them into a single figures.pdf. The JSON file can mix data and rendering functions, so you can flexibly compose plots and layouts. This makes it handy for generating figures for papers. You provide the renderers (Python functions that draw and save fig{index}.pdf), while paperfig takes care of JSON parsing, dispatching, multi-panel layouts, and concatenation.

## Key features
- Simple JSON spec → figures
- Use your own renderers; paperfig only orchestrates
- Supports both simple figures and multi‑panel grids
- Concatenates everything into a single figures.pdf
- Extensible: register functions, import "module:function", or use entry points

## Install
- Library only: `pip install paperfig`
- With example dependencies: `pip install "paperfig[examples]"`
## Quick start (run the bundled example)
- Clone the source repository
```bash
git clone https://github.com/sekika/paperfig.git
```
- Change into the examples directory and run the script:
```bash
cd paperfig/docs/examples
python fig.py
```
- Outputs:
  - docs/examples/fig/fig1.pdf, fig2.pdf, fig3a.pdf … fig3d.pdf
  - docs/examples/fig/fig3.pdf (2x2 multi panel)
  - docs/examples/fig/figures.pdf (all pages concatenated)

## CLI
- Build: `paperfig build path/to/fig.json -d out -o figures.pdf`
- Validate only: `paperfig validate path/to/fig.json`
- List figures: `paperfig list path/to/fig.json`

## Minimal API example
- Define a renderer that writes fig{index}.pdf into fig_dir. Register and build.

```python
from paperfig.figure import Fig
import matplotlib.pyplot as plt

def render_hello(index, data, verbose=1):
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, f"Hello {index}", ha="center", va="center")
    plt.savefig(f"out/fig{index}.pdf"); plt.close(fig)

fig = Fig("fig.json")
fig.fig_dir = "out"
fig.function = {"hello": render_hello}
fig.create_pdf()
```

JSON spec example (with multi)
```json
{
  "1": { "type": "hello" },
  "2": { "type": "hello" },
  "3": {
    "type": "multi",
    "row": 1,
    "column": 2,
    "figures": {
      "3a": { "type": "hello" },
      "3b": { "type": "hello" }
    }
  }
}
```

## Extensibility
- Register a renderer in code: fig.function["name"] = callable
- Refer to a renderer by string: "module:function" in JSON type
- Plugin system: packages can expose entry points under paperfig.renderers

## Documentation
- See [https://sekika.github.io/paperfig/](https://sekika.github.io/paperfig/) for the full guide.

## License
- MIT License
