# `plotmath`
`plotmath` is a Python package to automatically create textbook graphs of mathematical functions. 

## Basic examples

### Example 1

```python
import plotmath


def f(x):
    return x**2 - x - 2


fix, ax = plotmath.plot(
    functions=[f],
)

plotmath.savefig(
    dirname="../figures",
    fname="example_1.svg",
)

plotmath.show()
```

This will generate the following figure:

![figure 1](https://raw.githubusercontent.com/reneaas/plotmath/refs/heads/main/examples/figures/example_1.svg)

### Example 2

```python
import plotmath
import numpy as np


def f(x):
    return x**2 * np.cos(x)


fix, ax = plotmath.plot(
    functions=[f],
    xmin=-6,
    xmax=6,
    ymin=-12,
    ymax=12,
    xstep=1,
    ystep=2,
)

plotmath.savefig(
    dirname="../figures",
    fname="example_2.svg",
)

plotmath.show()
```

This will generate the following figure:

![figure 2](https://raw.githubusercontent.com/reneaas/plotmath/refs/heads/main/examples/figures/example_2.svg)

### Example 3

```python
import plotmath


def f(x):
    return x**2 - 4


def g(x):
    return x + 2


fix, ax = plotmath.plot(
    functions=[f, g],
    xmin=-6,
    xmax=6,
    ymin=-6,
    ymax=6,
)

plotmath.savefig(
    dirname="../figures",
    fname="example_3.svg",
)

plotmath.show()
```

This will generate the following figure:

![figure 3](https://raw.githubusercontent.com/reneaas/plotmath/refs/heads/main/examples/figures/example_3.svg)

