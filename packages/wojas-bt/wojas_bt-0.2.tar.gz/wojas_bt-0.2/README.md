# Wojas Beautiful Text (`wojas_bt`)

[![PyPI version](https://img.shields.io/pypi/v/wojas_bt.svg)](https://pypi.org/project/wojas_bt/)
![Python](https://img.shields.io/badge/python-%3E%3D3.7-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/wojase/wojas_bt/python-package.yml?branch=main)](https://github.com/wojase/wojas_bt/actions)

Create beautiful colored text in your terminal easily using Python gradients and rainbow animations! 🌈✨


## Features

- Smooth RGB gradients for 18+ colors
- Bold, italic, and normal styles
- Rainbow animation
- Easy-to-use import for each color/style

## Installation

```bash
pip install wojas_bt
```

## Usage / Example
```bash
from wojas_bt import red_bold, blue_italic, rainbow_animate

# Print gradients
red_bold("🔥 Bold Red Gradient 🔥")
blue_italic("💙 Italic Blue Gradient 💙")

# Rainbow animation
rainbow_animate("🌈 Hello Rainbow! 🌈", duration=5, style="bold", speed=0.05)
```

## Available Colors and Functions
Each color has three styles: normal, bold, and italic. Example for red:

- red_normal

- red_bold

- red_italic

Other colors: green, blue, yellow, orange, pink, purple, cyan, magenta, lime, aqua, gold, silver, brown, teal, indigo, grey, white.

## Authors

- [@Wojase](https://github.com/wojase)

## License
This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License. See the LICENSE file for details.

