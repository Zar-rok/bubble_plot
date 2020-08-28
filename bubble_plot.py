"""
Module to generate the Latex source files for bubble plots.

A plot has three facets, one as the y axis and two on the x axis.
"""

import csv
from itertools import zip_longest
from operator import attrgetter, itemgetter
from typing import Dict, NamedTuple, Sequence, Set, Tuple


class Facets(NamedTuple):
    """
    Describe the name of the facets of a bubble plot.

    Attributes
    ----------
    y: str
        Name of the facet on the y axis.
    x_left: str
        Name of the facet on the left part of the x axis.
    x_right: str
        Name of the facet on the right part of the x axis.
    """

    y: str
    x_left: str
    x_right: str


class Config(NamedTuple):
    """
    Describe custom settings for the bubble plot.

    Attributes
    ----------
    x_left_offset: int
        Define the offset at which the first x tick near the left of the y axis is placed.
    x_right_offset: int
        Define the offset at which the first x tick near the right of the y axis is placed.
    class_year: str
        Label representing the publication year.
    field_names: Sequence[str]
        Name of the columns for the ouput file of the bubble plot.
    """

    x_left_offset: int
    x_right_offset: int
    class_year: str
    field_names: Sequence[str]


class Occurence:
    """
    Compute the occurence of a bubble.

    Attributes
    ----------
    occurence: int
        Occurence of a bubble.
    year: str
        Earliest year from entries related to the bubble.
    """

    __slots__ = ("occurence", "year")

    def __init__(self, year: str):
        """
        Parameters
        ----------
        year: str
            Year of the first entry related to the bubble.
        """
        self.occurence: int = 1
        self.year: str = year

    def update(self, new_year: str):
        """
        Update the occurences and save the earliest publish year.

        Parameters
        ----------
        new_year: str
            New publish year to update `year` with if it's less than the current year.
        """
        self.occurence += 1
        self.year = min(self.year, new_year)

    def __str__(self):
        return f"Occurence: {self.occurence}, Year: {self.year}"

    def __repr__(self):
        return f"{self.__class__.__name__}{(self.occurence, self.year)}"


class Bubble(NamedTuple):
    """
    Bubble label on the x axis and y axis.

    Attributes
    ----------
    label_x: str
        Label displayed as a x tick label.
    label_y: str
        Label displayed as a y tick label.

    Notes
    -----
    The x and y tick label are keys from the Latex
    `pgfplots <https://ctan.org/pkg/pgfplots>`_ package.
    """

    label_x: str
    label_y: str


class SplitXAxis(NamedTuple):
    """
    Facet on one side of the splited x axis.

    Attributes
    ----------
    facet: str
        Name of the facet.
    bubbles: Dict[Bubble, Occurence]
        Bubbles related to the facet
    """

    facet: str
    bubbles: Dict[Bubble, Occurence]

    def update(self, entry: Dict[str, str], year: str, y_axis: str) -> None:
        """
        Update the bubble occurences related to the side of the x axis.

        Parameters
        ----------
        entry: Dict[str, str]
            Entries to take as input for the occurence computation.
        year: str
            Publication year of the entry.
        y_axis: str
            Name of the facet of the y axis.
        """
        try:
            label_x = entry[self.facet]
        except KeyError as error:
            raise KeyError(
                f"Unkown facet named: {error} on the x axis") from error
        try:
            label_y = entry[y_axis]
        except KeyError as error:
            raise KeyError(
                f"Unkown facet named: {error} on the y axis") from error

        bubble = Bubble(label_x=label_x, label_y=label_y)
        if bubble in self.bubbles:
            self.bubbles[bubble].update(year)
        else:
            self.bubbles[bubble] = Occurence(year)


class XAxis(NamedTuple):
    """
    Facets of the x axis.

    Attributes
    ----------
    left: SplitXAxis
        Left facet of a bubble plot.
    right: SplitXAxis
        Right facet of a bubble plot.
    """

    left: SplitXAxis
    right: SplitXAxis


class BubblePlot:
    """
    Describe a bubble plot with 3 facets.

    Attributes
    ----------
    x_axis: XAxis
        Facets on the x axis. One to the left of the y axis and the other to the right.
    y_axis: str
        Facet on the y axis.
    """

    __slots__ = ("x_axis", "y_axis")

    def __init__(self, facets: Facets):
        """
        Parameters
        ----------
        facets: Facets
            Describe the facets label of the bubble plot.
        """
        y_axis, x_left_axis, x_right_axis = facets
        self.x_axis: XAxis = XAxis(
            left=SplitXAxis(facet=x_left_axis, bubbles={}),
            right=SplitXAxis(facet=x_right_axis, bubbles={}),
        )
        self.y_axis: str = y_axis

    def __str__(self):
        """
        Returns
        -------
        str
            The name of the left facet on the x axis,
            the name of the facet on the y axis, and
            the name of the right facet on the x axis.
        """
        return f"{self.x_axis.left.facet}_{self.y_axis}_{self.x_axis.right.facet}"

    def __repr__(self):
        return f"{self.__class__.__name__}{(self.x_axis, self.y_axis)}"

    def update(self, entry: Dict[str, str], year: str) -> None:
        """
        Update the bubbles occurences of the plot.

        Parameters
        ----------
        entry: Dict[str, str]
            Label and value to use as input for a bubble.
        year: str
            Publication year of the entry.
        conf: Config
            Describe custom settings for the plots.
        """
        self.x_axis.left.update(entry, year, self.y_axis)
        self.x_axis.right.update(entry, year, self.y_axis)


class CSVWriter(NamedTuple):
    """
    Save a bubble plot as a CSV file.

    Attributes
    ----------
    plot: BubblePlot
        Plot to prepare and format.
    years: Set[str]
        Publication years.
    conf: Config
        Describe custom settings for the plots.
    """

    plot: BubblePlot
    years: Set[str]
    conf: Config

    def compute_year_score_mapping(self) -> Dict[str, int]:
        """
        Compute the mapping between years and color map scores. The scores are mapped in
        chronological order of the years.

        Returns
        -------
        Dict[str, str]
            Mapping between a year and a score.

        Notes
        -----
        The color map score is in the interval [0-1000].
        See paragraph ``Colormap Input Format Reference`` in Section 4.7.6 of the
        Latex `pgfplots <https://ctan.org/pkg/pgfplots>`_ package.
        """
        idx = 0
        incr = 1000 // (len(self.years) - 1)
        year_score = {}
        for year in sorted(self.years):
            year_score[year] = idx
            idx += incr
        return year_score

    def compute_labels_indices_mapping(
            self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Compute the mapping between labels and their indices.

        Returns
        -------
        Tuple[Dict[str, int], Dict[str, int]]
            The mapping between:
                - the x tick labels and their indices.
                - the y tick labels and their indices.
        """

        labels_x_left = sorted(
            set(map(attrgetter("label_x"), self.plot.x_axis.left.bubbles)))
        labels_x_left_len = len(labels_x_left)
        # From -N to -conf.x_left_offset
        x_left_mapping = {
            label: -(labels_x_left_len - i + self.conf.x_left_offset)
            for i, label in enumerate(labels_x_left)
        }

        labels_x_right = sorted(
            set(map(attrgetter("label_x"), self.plot.x_axis.right.bubbles)))
        # From conf.x_left_offset to N
        x_right_mapping = {
            label: i + self.conf.x_right_offset
            for i, label in enumerate(labels_x_right)
        }

        labels_y = sorted(
            set(
                map(
                    attrgetter("label_y"),
                    list(self.plot.x_axis.right.bubbles) +
                    list(self.plot.x_axis.left.bubbles),
                )))
        # From 0 to N-1
        y_mapping = {label: i for i, label in enumerate(labels_y)}

        x_mapping = {**x_left_mapping, **x_right_mapping}

        return x_mapping, y_mapping

    def prepared_bubbles_data(
        self,
        x_mapping: Dict[str, int],
        y_mapping: Dict[str, int],
        year_mapping: Dict[str, int],
    ) -> Sequence[Tuple[int, int, int, int]]:
        """
        Prepare bubbles data.

        Parameters
        ----------
        x_mapping: Dict[str, int]
            The x tick labels and their indices.
        y_mapping: Dict[str, int]
            The y tick labels and their indices.
        year_mapping: Dict[str, int]
            The publication years and their score.

        Returns
        -------
        Sequence[Tuple[int, int, int, int]]
            Lines of the CSV file representing each bubble.
            The columns are, in order:
            - The index of the y tick label related to the bubble.
            - The index of the x tick label related to the bubble.
            - The number of occurence of the bubble.
            - The earliest publication year related to the bubble.
        """
        bubbles = {
            **self.plot.x_axis.left.bubbles,
            **self.plot.x_axis.right.bubbles
        }
        return tuple((
            y_mapping[bubble.label_y],
            x_mapping[bubble.label_x],
            occurence.occurence,
            year_mapping[occurence.year],
        ) for bubble, occurence in bubbles.items())

    def write(
        self,
        data: Sequence[Tuple[int, int, int, int]],
        labels_y: Sequence[str],
        labels_x: Sequence[str],
    ) -> None:
        """
        Save bubble plot as a CVS file.

        Parameters
        ----------
        data: Sequence[Tuple[int, int, int, int]]
             Bubble plot data prepared.
        labels_y: Sequence[str]
            Labels of the facet on the y axis.
        labels_x: Sequence[str]
            Labels of the facets on the x axis.
        """

        # TODO: Ugly
        y_indices = []
        x_indices = []
        occurences = []
        year_scores = []
        for y_idx, x_idx, occ, y_s in data:
            y_indices.append(y_idx)
            x_indices.append(x_idx)
            occurences.append(occ)
            year_scores.append(y_s)

        with open(f"{self.plot}.csv", "w") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(self.conf.field_names)
            writer.writerows(
                zip_longest(y_indices, x_indices, occurences, year_scores,
                            labels_y, labels_x))

    def save_plot(self) -> None:
        """
        Compute the mapping between labels and their indices; year and their scores.

        Prepared bubble plot data for the CSV file. And write data and
        labels into a file.
        """
        x_mapping, y_mapping = self.compute_labels_indices_mapping()
        year_score = self.compute_year_score_mapping()
        bubbles_data = self.prepared_bubbles_data(x_mapping, y_mapping,
                                                  year_score)
        sorted_bubbles_data = sorted(bubbles_data, key=itemgetter(1))
        self.write(sorted_bubbles_data, list(y_mapping.keys()),
                   list(x_mapping.keys()))


def compute_occurences_from(entries: Sequence[Dict[str,
                                                   str]], plot_plan: Facets,
                            conf: Config) -> Tuple[BubblePlot, Set[str]]:
    """
    Compute the occurences of each value for the given labels.

    Parameters
    ----------
    entries: Sequence[Dict[str, str]]
        Labels and values to use as input for the bubble plot.
    plot_plan: Facets
        Describe the labels used for the facets of the plot.
    conf: Config
        Describe custom settings for the plots.

    Returns
    -------
    Tuple[BubblePlot, Set[str]]
        - The initialised bubble plot described by `plot_plan`.
        - The years related to each entry.
    """
    years = set()
    plot = BubblePlot(plot_plan)
    for entry in entries:
        year = entry[conf.class_year]
        plot.update(entry, year)
        years.add(year)
    return plot, years


def build_and_save_plots(entries: Sequence[Dict[str, str]],
                         plot_plans: Sequence[Facets], conf: Config) -> None:
    """
    Build and save bubble plots as CSV files.

    Parameters
    ----------
    entries: Sequence[Dict[str, str]]
        Labels and values to use as input for the bubble plot.
    plot_plan: Facets
        Describe the labels used for the facets of the plot.
    conf: Config
        Describe custom settings for the plots.
    """
    for plot_plan in plot_plans:
        plot, years = compute_occurences_from(entries, plot_plan, conf)
        writer_csv = CSVWriter(plot, years, conf)
        writer_csv.save_plot()
