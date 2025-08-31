# What is `scilayout`?

> [!WARNING]  
> This package is in beta.

`pip install scilayout`

Scilayout is a Python package to make creating multi-panel scientific figures easier, faster, and maybe a little bit more fun. The core idea is to build figures using coordinates in **centimetres from the top left** using interactive plotting. This approach has a few main benefits:

1. The iterative process of building figures up from scratch is easier.
2. Complex layouts can be interchanged more easily.
3. Exported figure sizes are explicitly stated (in centimetres) for seamless embedding in documents.

There are many guides for Matplotlib styling for scientific publication, and there are a number of packages that make this process easier (e.g. [SciencePlots](https://github.com/garrettj403/SciencePlots)), but this `scilayout` supports the creation of figures which are 100% ready for embedding in documents.

```python
import scilayout
fig = scilayout.figure()  # it's a matplotlib figure like plt.figure()

myax = fig.add_panel((1, 1, 5, 5))  # creates a panel with position specified in cm

# %%
myax.set_location((2, 10, 5, 3), method='size')  # move the panel after it's been created and set it's location and dimensions based on size (5x3cm dimensions from 2cm down and 10 cm left)

```

This package is designed for people with:
- A basic understanding of `matplotlib`'s `Axes` object and how to work with it (rather than only using `plt`, the differences described [here](https://matplotlib.org/matplotblog/posts/pyplot-vs-object-oriented-interface/))
- A desire to produce figures entirely in code (example approaches described in blogposts from [brushingupscience.com](https://brushingupscience.com/2021/11/02/a-better-way-to-code-up-scientific-figures/#more-6299) and [dendwrite.substack](https://dendwrite.substack.com/p/a-complete-ish-guide-to-making-scientific))

Detailed documentation is under construction.
<!-- For more documentation, please see https://scilayout.readthedocs.io -->