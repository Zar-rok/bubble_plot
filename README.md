# Bubble Plot

The purpose of this Python module is to automate the generation of the CSV file and the preparation of the Latex source file for the [bubbleplot](https://github.com/Zar-rok/bubbleplot) Latex package.

## How to use the `bubble_plot` module?

Please follow the instructions of the [Jupyter](https://jupyter.org/) notebook [usage_example.ipynb](example/usage_example.ipynb).

## WIP

- [X] Implement, document, and test the bubble plot data generation.
- [X] Generate the Latex source code parametrised for a given bubble plot.
- [X] Provide an example of interaction with the `bubble_plot` module.
- [X] Document the Latex template variable & keys to manually define.
- [X] Add support to custom colour scheme for the bubbles (e.g. using `seaborn`).

To think about:
- [ ] The field `years` is in the `.sty`. How to extract it to be configurable?
- [ ] Remove all IO interactions from the `bubble_plot` module?

## Python module documentation

First install `sphinx`. For example via: `pip3 install sphinx`.

Then, from [docs/](docs/) run: `make html && open _build/html/index.html`

## Run tests

Run `python3 -m unittest test_bubble_plot.py`
