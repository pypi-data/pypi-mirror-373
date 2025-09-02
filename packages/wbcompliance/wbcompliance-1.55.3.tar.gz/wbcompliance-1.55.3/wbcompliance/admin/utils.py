from io import StringIO

import pandas as pd
from django.shortcuts import redirect, render
from reversion.errors import RevertError
from wbcore.admin import CsvImportForm, ImportCsvMixin


class CustomImportCsvMixin(ImportCsvMixin):
    def _import_csv(self, request, _sep=";"):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            str_text = ""
            for line in csv_file:
                str_text = str_text + line.decode()
            # Import csv as df
            df = pd.read_csv(StringIO(str_text), sep=_sep)
            # Sanitize dataframe
            df = df.where(pd.notnull(df), None)
            df = df.drop(df.columns.difference(self.get_import_fields()), axis=1)

            # Overide this function if there is foreign key ids in the dataframe
            df = self.manipulate_df(df)
            errors = 0
            revert_errors = 0
            nb_added = 0
            for model in df.to_dict("records"):
                # by default, process the modela as a create request. Can be override to change the behavior
                try:
                    nb_added += self.process_model(model)
                # https://django-reversion.readthedocs.io/en/stable/common-problems.html
                except RevertError:
                    revert_errors += 1
                except Exception as e:
                    print(e)  # noqa: T201
                    errors += 1
            msg = f"""Your csv file has been imported : {df.shape[0] - errors - revert_errors} imported
                 ({nb_added} added, {df.shape[0] - errors - revert_errors - nb_added} updated), {errors} errors,
                 {revert_errors} revert errors found due to failure to restore old versions
            """
            self.message_user(request, msg)
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "wbcore/admin/csv_form.html", payload)
