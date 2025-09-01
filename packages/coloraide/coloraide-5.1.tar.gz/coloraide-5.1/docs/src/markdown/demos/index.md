# ColorAide Demos

## Online Color Picker

![Color Picker](../images/colorpicker.png)

Use ColorAide to pick a color in any of the color spaces available. ACES color spaces have been arbitrarily limited
has they have ginormous headroom.

All results, from any color space, are gamut mapped to the detected display gamut (sRGB, Display P3, or Rec. 2020), but
you can force lower gamuts that fit inside your detected gamut as well. Larger gamuts than the detected gamut will be
unavailable.

[Try it out](./colorpicker.html)

## Interactive 3D Color Space Models

![3D Color Models](../images/3d_models.png)

Generate interactive 3D color models in the browser using ColorAide and [Plotly](https://plotly.github.io/)! Most color
spaces are supported, but color spaces with more than 3 color components (not including alpha) are not supported. Colors
can be generated in a number of color gamuts, though a few models are restricted to their own color space for practical
reasons.

[Try it out](./3d_models.html)
