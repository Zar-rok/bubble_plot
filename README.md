# Bubble Plot

Generate the Latex source file to generate bubble plot visualisation.

Example of a bubble plot generate with the following [Latex code](example/example.tex) using the following [dummy data](example/test.csv).

![Example of a bubble plot generated on Latex](example/example.pdf)

## WIP

- [X] Implement, document, and test the bubble plot data generation.
- [ ] Provide an example of interaction with the `bubble_plot` module.
- [ ] Generate the Latex source code parametrised for a given bubble plot.

## Documentation generation

First install `sphinx`. For example via: `pip3 install sphinx`.

Then, from `docs/` run: `make html && open _build/html/index.html`

## Run tests

Run `python3 -m unittest test_bubble_plot.py`

## Bubble plot usage

Bubble plot are a type of visualisation used, for example, in a `Systematic Mapping Study`.

See [Petersen, Kai, et al. "Systematic mapping studies in software engineering." Ease. Vol. 8. 2008](https://www.researchgate.net/profile/Michael_Mattsson/publication/228350426_Systematic_Mapping_Studies_in_Software_Engineering/links/54d0a8e90cf20323c218713d/Systematic-Mapping-Studies-in-Software-Engineering.pdf) for a presentation of this methodology.
