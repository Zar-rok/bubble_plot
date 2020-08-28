from unittest import TestCase
from unittest.mock import mock_open, patch

from bubble_plot import (
    Bubble,
    BubblePlot,
    Config,
    CSVWriter,
    Facets,
    LatexBubblePlotWriter,
    Occurence,
    SplitXAxis,
    build_and_save_plots,
    compute_occurences_from,
)


class TestOccurence(TestCase):
    def setUp(self):
        self.year = "2020"
        self.occu = Occurence(self.year)

    def test_init(self):
        self.assertEqual(self.year, self.occu.year)
        self.assertEqual(1, self.occu.occurence)

    def test_update(self):
        self.occu.update("2019")
        self.assertEqual("2019", self.occu.year)
        self.assertEqual(2, self.occu.occurence)

        self.occu.update("2021")
        self.assertNotEqual("2021", self.occu.year)
        self.assertEqual(3, self.occu.occurence)


class TestSplitXAxis(TestCase):
    def setUp(self):
        self.x_axis = SplitXAxis("X", {})

    def test_update(self):
        entry = {"X": "pouet", "Y": "hoho"}
        bubble = Bubble(label_x=entry["X"], label_y=entry["Y"])

        self.x_axis.update(entry, "2020", "Y")
        self.assertTrue(bubble in self.x_axis.bubbles)

    def test_update_unkown_facet(self):
        entry = {"Z": "pouet", "Y": "hoho"}
        regex = "Unkown facet named: 'X' on the x axis"
        self.assertRaisesRegex(KeyError, regex, self.x_axis.update, entry, "2020", "Y")

        entry = {"X": "pouet", "Z": "hoho"}
        regex = "Unkown facet named: 'Y' on the y axis"
        self.assertRaisesRegex(KeyError, regex, self.x_axis.update, entry, "2020", "Y")


class TestBubblePlot(TestCase):
    def setUp(self):
        self.bubble_plot = BubblePlot(Facets("Y", "X_left", "X_right"))

    def test_init(self):
        self.assertEqual("Y", self.bubble_plot.y_axis)
        self.assertEqual("X_left", self.bubble_plot.x_axis.left.facet)
        self.assertEqual("X_right", self.bubble_plot.x_axis.right.facet)

    def test_update(self):
        entry = {"X_left": "pouet", "X_right": "teuop", "Y": "hoho"}
        bubble_left = Bubble(label_x=entry["X_left"], label_y=entry["Y"])
        bubble_right = Bubble(label_x=entry["X_right"], label_y=entry["Y"])

        self.bubble_plot.update(entry, "2020")
        self.assertTrue(bubble_left in self.bubble_plot.x_axis.left.bubbles)
        self.assertTrue(bubble_right in self.bubble_plot.x_axis.right.bubbles)


class TestCSVWriter(TestCase):
    def setUp(self):
        self.conf = Config(1, 2, "year", ["iy", "ix", "nbr", "year", "y", "x"])
        self.years = {"2018", "2019", "2020"}
        self.entries = [
            {"Y": "0", "X_left": "1", "X_right": "2", "year": "2018"},
            {"Y": "3", "X_left": "4", "X_right": "5", "year": "2020"},
            {"Y": "6", "X_left": "7", "X_right": "8", "year": "2019"},
        ]
        self.year_mapping = {"2018": 0, "2019": 500, "2020": 1000}
        self.x_mapping = {"1": -4, "4": -3, "7": -2, "2": 2, "5": 3, "8": 4}
        self.y_mapping = {"0": 0, "3": 1, "6": 2}
        self.data = (
            (0, -4, 1, 0),
            (1, -3, 1, 1000),
            (2, -2, 1, 500),
            (0, 2, 1, 0),
            (1, 3, 1, 1000),
            (2, 4, 1, 500),
        )
        self.facets = Facets("Y", "X_left", "X_right")
        self.bubble_plot = BubblePlot(self.facets)
        for entry in self.entries:
            self.bubble_plot.update(entry, entry[self.conf.class_year])
        self.writer = CSVWriter(self.bubble_plot, self.years, self.conf)

    def test_compute_year_score_mapping(self):
        mapping = self.writer.compute_year_score_mapping()
        self.assertEqual(self.year_mapping, mapping)

    def test_compute_labels_indices_mapping(self):
        x_mapping, y_mapping = self.writer.compute_labels_indices_mapping()
        self.assertEqual(self.y_mapping, y_mapping)
        self.assertEqual(self.x_mapping, x_mapping)

    def test_prepared_bubbles_data(self):
        prepared_data = self.writer.prepared_bubbles_data(
            self.x_mapping, self.y_mapping, self.year_mapping
        )
        self.assertEqual(self.data, prepared_data)

    def test_write(self):
        mock = mock_open()
        with patch("bubble_plot.open", mock):
            self.writer.write(self.data, list(self.x_mapping.keys()), list(self.y_mapping.keys()))
        mock.assert_called_once_with(f"{self.bubble_plot}.csv", "w")

        exps = [
            ("iy,ix,nbr,year,y,x\r\n"),
            ("0,-4,1,0,1,0\r\n"),
            ("1,-3,1,1000,4,3\r\n"),
            ("2,-2,1,500,7,6\r\n"),
            ("0,2,1,0,2,\r\n"),
            ("1,3,1,1000,5,\r\n"),
            ("2,4,1,500,8,\r\n"),
        ]
        handle = mock()
        for expected, (args, _) in zip(exps, handle.write.call_args_list):
            self.assertEqual(expected, args[0])


class TestLatexBubblePlotWriter(TestCase):
    def setUp(self):
        self.conf = Config(1, 2, "year", ["iy", "ix", "nbr", "year", "y", "x"])
        self.years = {"2018", "2019", "2020", "2021", "2022"}
        self.entries = [
            {"Y": "0", "X_left": "1", "X_right": "2", "year": "2021"},
            {"Y": "3", "X_left": "4", "X_right": "5", "year": "2020"},
            {"Y": "6", "X_left": "7", "X_right": "8", "year": "2019"},
            {"Y": "0", "X_left": "1", "X_right": "2", "year": "2022"},
            {"Y": "3", "X_left": "4", "X_right": "5", "year": "2020"},
            {"Y": "6", "X_left": "7", "X_right": "8", "year": "2019"},
        ]
        self.year_mapping = {"2018": 0, "2019": 200, "2020": 400, "2021": 800, "2022": 1000}
        self.x_mapping = {"1": -4, "4": -3, "7": -2, "2": 2, "5": 3, "8": 4}
        self.y_mapping = {"0": 0, "3": 1, "6": 2}
        self.data = (
            (0, -4, 1, 0),
            (1, -3, 1, 200),
            (2, -2, 1, 400),
            (0, 2, 1, 200),
            (1, 3, 1, 800),
            (2, 4, 1, 1000),
        )
        self.facets = Facets("Y", "X_left", "X_right")
        self.bubble_plot = BubblePlot(self.facets)
        for entry in self.entries:
            self.bubble_plot.update(entry, entry[self.conf.class_year])
        self.writer = LatexBubblePlotWriter(self.bubble_plot, self.years, self.conf)

    def test_save_plot(self):
        self.writer.save_plot({key: key for key in self.facets})


class TestAPI(TestCase):
    def setUp(self):
        self.entries = [
            {"Y": "0", "X_left": "1", "X_right": "2", "year": "2018"},
            {"Y": "3", "X_left": "4", "X_right": "5", "year": "2020"},
            {"Y": "6", "X_left": "7", "X_right": "8", "year": "2019"},
        ]

        self.conf = Config(1, 2, "year", ["iy", "ix", "nbr", "year", "y", "x"])

        self.plot_plan = Facets("Y", "X_left", "X_right")

    def test_compute_occurences_from(self):

        plot, years = compute_occurences_from(self.entries, self.plot_plan, self.conf)

        entries_len = len(self.entries)
        self.assertEqual(entries_len, len(plot.x_axis.left.bubbles))
        self.assertEqual(entries_len, len(plot.x_axis.right.bubbles))
        self.assertEqual({"2018", "2019", "2020"}, years)

    def test_build_and_save_plots(self):
        number_plot = 3
        mock = mock_open()
        with patch("bubble_plot.open", mock):
            build_and_save_plots(self.entries, [self.plot_plan] * number_plot, self.conf)
        self.assertEqual(number_plot, len(mock.call_args_list))
