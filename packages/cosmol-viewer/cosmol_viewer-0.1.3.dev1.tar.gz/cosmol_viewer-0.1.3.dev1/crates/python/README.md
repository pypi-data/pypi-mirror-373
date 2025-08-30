# COSMol-viewer

<div align="center">
  <a href="https://crates.io/crates/cosmol_viewer">
    <img src="https://img.shields.io/crates/v/cosmol_viewer.svg" alt="crates.io Latest Release"/>
  </a>
  <a href="https://pypi.org/project/cosmol_viewer/">
    <img src="https://img.shields.io/pypi/v/cosmol_viewer.svg" alt="PyPi Latest Release"/>
  </a>
    <a href="https://cosmol-repl.github.io/COSMol-viewer">
    <img src="https://img.shields.io/badge/docs-latest-blue.svg" alt="Documentation Status"/>
  </a>
</div>

A high-performance molecular visualization library built with Rust and WebGPU, designed for seamless integration into Python workflows.

- ⚡ Fast: Native-speed rendering powered by Rust and GPU acceleration

- 🧬 Flexible: Load molecules from .sdf, .pdb, and dynamically update 3D structures

- 📓 Notebook-friendly: Fully supports Jupyter and Google Colab — ideal for education, research, and live demos

- 🔁 Real-time updates: Update molecular coordinates on-the-fly for simulations or animations

- 🎨 Customizable: Control styles, camera, and rendering settings programmatically

# Installation

```sh
pip install cosmol-viewer
```

# Examples

See examples in [Google Colab](https://colab.research.google.com/drive/1Sw72QWjQh_sbbY43jGyBOfF1AQCycmIx?usp=sharing).

# Usage

```python
from cosmol_viewer import Scene, Viewer, parse_sdf, Molecules

# === Step 1: Load and render a molecule ===
with open("molecule.sdf", "r") as f:
    sdf = f.read()
    mol = Molecules(parse_sdf(sdf)).centered()

scene = Scene()
scene.scale(0.1)
scene.add_shape(mol, "mol")

viewer = Viewer.render(scene)  # Launch the viewer

# === Step 2: Update the same molecule dynamically ===
import time

for i in range(1, 10):  # Simulate multiple frames
    with open(f"frames/frame_{i}.sdf", "r") as f:
        sdf = f.read()
        updated_mol = Molecules(parse_sdf(sdf)).centered()

    scene.update_shape("mol", updated_mol)
    viewer.update(scene)

    time.sleep(0.033)  # ~30 FPS
```