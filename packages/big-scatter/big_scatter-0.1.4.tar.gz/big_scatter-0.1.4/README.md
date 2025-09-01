# big_scatter

Simple jupyter widget to draw and explore a large set of 2D datapoints.

## Installation

```bash
pip install big_scatter
```

## Example usage

```python
import big_scatter
import numpy as np

X = np.random.randn(200000, 2)
Y = np.arange(X.shape[0])

import big_scatter

big_scatter.draw(X, Y)
```

## Arguments to draw()

```
points                point coordinates as a numpy array of shape (N, 2)
labels                point labels as a list or numpy array of size N
width='50%'           width of widget in jupyter
color='blue'          point color as a list of size N or a single string
size=1                point size as list or number
shape='square'        point shape as list or string (square or circle)
pick_radius=15        radius when searching for points closest to the cursor
pick_limit=20         number of closest labels to show
html_labels=False     set to True to interpret labels as HTML
```
