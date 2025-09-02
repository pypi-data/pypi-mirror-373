from typing import Any

import wtforms
from flask_babel import lazy_gettext

import hawat.forms
from hawat.charts import TableColoring


class SimpleCrossTableSearchForm(hawat.forms.EventSearchFormBase):
    """
    Class representing simple event cross table search form.
    """

    row_agg_column = wtforms.SelectField(
        lazy_gettext("Row aggregation:"),
        validators=[wtforms.validators.DataRequired()],
        description=lazy_gettext("The category by which the events will be grouped in the rows of the cross table."),
    )
    col_agg_column = wtforms.SelectField(
        lazy_gettext("Column aggregation:"),
        validators=[wtforms.validators.DataRequired()],
        description=lazy_gettext("The category by which the events will be grouped in the columns of the cross table."),
    )

    table_coloring = wtforms.SelectField(
        lazy_gettext("Table coloring:"),
        choices=[
            (TableColoring.NUMBER, lazy_gettext("Number")),
            (TableColoring.NUMBER_LOG, lazy_gettext("Log-scaled number")),
            (TableColoring.RESIDUAL_DIVERGING, lazy_gettext("Residual diverging")),
            (TableColoring.RESIDUAL, lazy_gettext("Residual")),
            (TableColoring.NONE, lazy_gettext("No coloring")),
        ],
        validators=[wtforms.validators.DataRequired()],
        default=TableColoring.NUMBER,
        description=lazy_gettext(
            "The coloring of the table cells."
            "<p>The 'Number' coloring is based solely on the numerical values in the table.</p>"
            "<p>The 'Log-scaled number' coloring is based on the logarithm of the numerical values in the table.</p>"
            "<p>The 'Residual diverging' coloring is based on the Pearson residuals of the values in the table. "
            "Values higher than the expected value are represented with darker blue, "
            "while values lower than the expected value are represented with darker red.</p>"
            "<p>The 'Residual' coloring is based on the Pearson residuals of the values in the table. "
            "Values higher than the expected value are represented with darker color, "
            "while values lower than the expected value are represented with lighter color.</p>"
            "<p>Expected value is calculated as the number one would expect if the total number for a "
            "category value would be distributed based on the distribution of total numbers of all the other "
            "categories.</p>"
        ),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.row_agg_column.choices = [("", lazy_gettext("Nothing selected"))] + kwargs["choices_agg_columns"]
        self.col_agg_column.choices = [("", lazy_gettext("Nothing selected"))] + kwargs["choices_agg_columns"]

    @classmethod
    def is_csag_context_excluded(cls, field_name: str) -> bool:
        return field_name in ("table_coloring",) or super().is_csag_context_excluded(field_name)
