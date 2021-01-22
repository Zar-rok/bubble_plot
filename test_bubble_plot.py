from secrets import token_urlsafe
from unittest import TestCase
from unittest.mock import mock_open, patch

from bubble_plot import (
    Bubble,
    BubblePlot,
    Config,
    CSVWriter,
    Facets,
    LatexBubblePlotWriter,
    Occurrence,
    SplitXAxis,
    build_and_save_plots,
    compute_occurences_from,
    compute_color_map,
)


class TestOccurence(TestCase):
    def setUp(self):
        self.year = "2020"
        self.occu = Occurrence(self.year)

    def test_init(self):
        self.assertEqual(self.year, self.occu.year)
        self.assertEqual(1, self.occu.occurrence)

    def test_update(self):
        self.occu.update("2019")
        self.assertEqual("2019", self.occu.year)
        self.assertEqual(2, self.occu.occurrence)

        self.occu.update("2021")
        self.assertNotEqual("2021", self.occu.year)
        self.assertEqual(3, self.occu.occurrence)


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
        regex = "Unknown facet named: 'X' on the x axis"
        self.assertRaisesRegex(
            KeyError, regex, self.x_axis.update, entry, "2020", "Y"
        )

        entry = {"X": "pouet", "Z": "hoho"}
        regex = "Unknown facet named: 'Y' on the y axis"
        self.assertRaisesRegex(
            KeyError, regex, self.x_axis.update, entry, "2020", "Y"
        )


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
        self.output_dir = "output_dir"
        self.conf = Config(
            1,
            2,
            "year",
            ["iy", "ix", "nbr", "year", "y", "x"],
            "template.tex",
            self.output_dir,
            [],
        )
        self.years = {"2018", "2019", "2020"}
        self.entries = [
            {"Y": "0", "X_left": "1", "X_right": "2", "year": "2018"},
            {"Y": "3", "X_left": "4", "X_right": "4", "year": "2020"},
            {"Y": "6", "X_left": "7", "X_right": "7", "year": "2019"},
        ]
        self.year_mapping = {"2018": 0, "2019": 500, "2020": 1000}
        self.x_left_mapping = {"1": -4, "4": -3, "7": -2}
        self.x_right_mapping = {"2": 2, "4": 3, "7": 4}
        self.y_mapping = {"0": 0, "3": 1, "6": 2}
        self.data = [
            (0, -4, 1, 0),
            (1, -3, 1, 1000),
            (2, -2, 1, 500),
            (0, 2, 1, 0),
            (1, 3, 1, 1000),
            (2, 4, 1, 500),
        ]
        self.facets = Facets("Y", "X_left", "X_right")
        self.bubble_plot = BubblePlot(self.facets)
        for entry in self.entries:
            self.bubble_plot.update(entry, entry[self.conf.class_year])
        self.writer = CSVWriter(self.bubble_plot, self.years, self.conf)

    def test_compute_year_score_mapping(self):
        mapping = self.writer.compute_year_score_mapping()
        self.assertEqual(self.year_mapping, mapping)

    def test_compute_labels_indices_mapping(self):
        (
            x_left_mapping,
            x_right_mapping,
            y_mapping,
        ) = self.writer.compute_labels_indices_mapping()
        self.assertEqual(self.y_mapping, y_mapping)
        self.assertEqual(self.x_left_mapping, x_left_mapping)
        self.assertEqual(self.x_right_mapping, x_right_mapping)

    def test_prepared_bubbles_data(self):
        prepared_data = self.writer.prepared_bubbles_data(
            self.x_left_mapping,
            self.x_right_mapping,
            self.y_mapping,
            self.year_mapping,
        )
        self.assertEqual(self.data, prepared_data)

    def test_write(self):
        mock = mock_open()
        with patch("bubble_plot.open", mock):
            self.writer.write(
                self.data,
                list(self.x_left_mapping.keys())
                + list(self.x_right_mapping.keys()),
                list(self.y_mapping.keys()),
            )
        mock.assert_called_once_with(
            f"{self.output_dir}/{self.bubble_plot}.csv", "w"
        )

        exps = [
            ("iy,ix,nbr,year,y,x\r\n"),
            ("0,-4,1,0,1,0\r\n"),
            ("1,-3,1,1000,4,3\r\n"),
            ("2,-2,1,500,7,6\r\n"),
            ("0,2,1,0,2,\r\n"),
            ("1,3,1,1000,4,\r\n"),
            ("2,4,1,500,7,\r\n"),
        ]
        handle = mock()
        for expected, (args, _) in zip(exps, handle.write.call_args_list):
            self.assertEqual(expected, args[0])


class TestLatexBubblePlotWriter(TestCase):
    def setUp(self):
        self.output_dir = "output_dir"
        self.conf = Config(
            1,
            2,
            "year",
            ["iy", "ix", "nbr", "year", "y", "x"],
            "template.tex",
            self.output_dir,
            [],
        )
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

        mock = mock_open(
            read_data="ix\n" + "\n".join(map(str, self.x_mapping.values()))
        )
        with patch("bubble_plot.open", mock):
            self.writer = LatexBubblePlotWriter(
                self.bubble_plot, self.years, self.conf
            )
        self.writer.x_indices = tuple(x for (_, x, _, _) in self.data)

    def test_init(self):
        mock = mock_open(
            read_data="ix\n" + "\n".join(map(str, self.x_mapping.values()))
        )
        with patch("bubble_plot.open", mock):
            LatexBubblePlotWriter(self.bubble_plot, self.years, self.conf)
        self.assertEqual(
            (f"{self.output_dir}/{self.bubble_plot}.csv", "r"),
            mock.call_args_list[0][0],
        )

    def test_year_color(self):
        years_len = len(self.years)
        year_color = compute_color_map(len(list(self.years)))
        self.assertEqual(years_len, len(set(year_color)))

    def test_prepare_values(self):
        expect = (
            "defineColorsYear",
            "setColorsYear",
            "xMin",
            "xMax",
            "yLabel",
            "meta",
            "xField",
            "xIndexField",
            "yField",
            "yIndexField",
            "yearField",
            "xLeftLabel",
            "xRightLabel",
            "CSVDataFile",
            "colorsYear",
        )
        year_color = {
            "2017": (0, 0, 1),
            "2018": (0, 1, 0),
            "2019": (1, 0, 0),
            "2020": (1, 1, 1),
        }
        self.assertEqual(
            expect, tuple(self.writer.prepare_values(year_color).keys())
        )

    def test_write(self):
        template_values = {
            "defineColorsYear": [token_urlsafe(5) for _ in self.years],
            "setColorsYear": [token_urlsafe(5) for _ in self.years],
            "xMin": token_urlsafe(5),
            "xMax": token_urlsafe(5),
            "yLabel": token_urlsafe(5),
            "meta": token_urlsafe(5),
            "xField": token_urlsafe(5),
            "xIndexField": token_urlsafe(5),
            "yField": token_urlsafe(5),
            "yIndexField": token_urlsafe(5),
            "yearField": token_urlsafe(5),
            "xLeftLabel": token_urlsafe(5),
            "xRightLabel": token_urlsafe(5),
            "CSVDataFile": token_urlsafe(5),
            "colorsYear": [token_urlsafe(5) for _ in self.years],
        }
        mock = mock_open()
        with patch("bubble_plot.open", mock):
            self.writer.write(template_values)
        self.assertEqual(
            (f"{self.conf.latex_template}", "r"), mock.call_args_list[0][0]
        )
        self.assertEqual(
            (f"{self.conf.output_dir}/{self.writer.plot}.tex", "w"),
            mock.call_args_list[1][0],
        )


class TestAPI(TestCase):
    def setUp(self):
        self.entries = [
            {"Y": "0", "X_left": "1", "X_right": "2", "year": "2018"},
            {"Y": "3", "X_left": "4", "X_right": "5", "year": "2020"},
            {"Y": "6", "X_left": "7", "X_right": "8", "year": "2019"},
        ]

        self.output_dir = "output_dir"
        self.conf = Config(
            1,
            2,
            "year",
            ["iy", "ix", "nbr", "year", "y", "x"],
            "template.tex",
            self.output_dir,
            [],
        )

        self.plot_plan = Facets("Y", "X_left", "X_right")

    def test_compute_occurences_from(self):
        plot, years = compute_occurences_from(
            self.entries, self.plot_plan, self.conf
        )

        entries_len = len(self.entries)
        self.assertEqual(entries_len, len(plot.x_axis.left.bubbles))
        self.assertEqual(entries_len, len(plot.x_axis.right.bubbles))
        self.assertEqual({"2018", "2019", "2020"}, years)

    def test_build_and_save_plots(self):
        number_plot = 3
        mock = mock_open(read_data="ix\n-1\n0\n1")
        with patch("bubble_plot.open", mock):
            build_and_save_plots(
                self.entries, [self.plot_plan] * number_plot, self.conf
            )
        self.assertEqual(number_plot * 4, len(mock.call_args_list))
