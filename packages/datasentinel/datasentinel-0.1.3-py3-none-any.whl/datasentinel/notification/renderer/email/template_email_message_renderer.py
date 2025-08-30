from email.message import EmailMessage
from importlib import resources
from io import BytesIO, StringIO
from pathlib import Path
from typing import ClassVar
from zipfile import ZIP_DEFLATED, ZipFile

from jinja2 import Template
from pandas import DataFrame, ExcelWriter

from datasentinel.notification.renderer.core import AbstractRenderer, RendererError
from datasentinel.validation.failed_rows_dataset.core import AbstractFailedRowsDataset
from datasentinel.validation.result import DataValidationResult
from datasentinel.validation.status import Status


class TemplateEmailMessageRenderer(AbstractRenderer[EmailMessage]):
    _MAX_FAILED_ROWS_LIMIT = 100000
    _FAILED_ROWS_FILE_TYPES: ClassVar[set[str]] = {"csv", "excel"}

    def __init__(
        self,
        template_path: str | None = None,
        include_failed_rows: bool = False,
        failed_rows_file_type: str = "excel",
        failed_rows_limit: int = 10,
    ):
        if failed_rows_file_type not in self._FAILED_ROWS_FILE_TYPES:
            raise RendererError(
                f"'{failed_rows_file_type}' is not a valid file type. "
                f"Valid options are: {self._FAILED_ROWS_FILE_TYPES}"
            )
        if not 0 < failed_rows_limit <= self._MAX_FAILED_ROWS_LIMIT:
            raise RendererError(
                f"Failed rows limit must be between 1 and {self._MAX_FAILED_ROWS_LIMIT}."
            )

        try:
            if template_path is None:
                template_content = resources.read_text(
                    "datasentinel.notification.renderer.email.templates", "default.html"
                )
            else:
                path = Path(template_path)
                template_content = path.read_text()

            self._template = Template(template_content)
        except (FileNotFoundError, OSError) as e:
            error_source = (
                "the default location" if template_path is None else f"'{template_path}'"
            )
            raise RendererError(f"Template could not be loaded from {error_source}.") from e

        self._include_failed_records = include_failed_rows
        self._failed_rows_type = failed_rows_file_type
        self._failed_rows_limit = failed_rows_limit

    def render(self, result: DataValidationResult) -> EmailMessage:
        try:
            message = EmailMessage()
            message.set_content(self._render_email_content(result=result), subtype="html")
            message["Subject"] = (
                f"'{result.data_asset}' passed data validation '{result.name}'!"
                if result.status == Status.PASS
                else f"'{result.data_asset}' failed data validation '{result.name}'!"
            )
            if self._include_failed_records and result.status == Status.FAIL:
                message = self._add_failed_rows_attachment(message, result)

            return message
        except Exception as e:
            raise RendererError(f"Error while rendering email message: {e!s}") from e

    def _add_failed_rows_attachment(
        self, message: EmailMessage, result: DataValidationResult
    ) -> EmailMessage:
        if all(
            [
                failed_rule.failed_rows_dataset is None
                for failed_check in result.failed_checks
                for failed_rule in failed_check.failed_rules
            ]
        ):
            return message

        methods_map = {
            "csv": self._add_csv_failed_rows_attachment,
            "excel": self._add_excel_failed_rows_attachment,
        }

        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zip_file:
            methods_map[self._failed_rows_type](result, zip_file)
        zip_buffer.seek(0)
        message.add_attachment(
            zip_buffer.getvalue(),
            maintype="application",
            subtype="zip",
            filename=f"{result.name.replace(' ', '_').lower()}_failed_rows_{result.run_id}.zip",
        )
        return message

    def _render_email_content(self, result: DataValidationResult) -> str:
        return self._template.render(
            result=result,
        )

    def _failed_rows_to_pandas(self, failed_rows_dataset: AbstractFailedRowsDataset) -> DataFrame:  # type: ignore
        return DataFrame(failed_rows_dataset.to_dict(limit=self._failed_rows_limit))

    def _add_excel_failed_rows_attachment(
        self, result: DataValidationResult, zip_file: ZipFile
    ) -> ZipFile:
        for failed_check in result.failed_checks:
            is_excel_empty = True
            excel_filename = f"{failed_check.name}_failed_rows.xlsx".replace(" ", "_").lower()
            excel_buffer = BytesIO()

            rules_with_failed_rows = [
                failed_rule
                for failed_rule in failed_check.failed_rules
                if failed_rule.failed_rows_dataset is not None
            ]

            if not rules_with_failed_rows:
                continue
            with ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                for failed_rule in rules_with_failed_rows:
                    sheet_name = f"(id={failed_rule.id}, rule={failed_rule.rule})"
                    sheet_name = sheet_name[:31]  # Excel sheet name limit is 31

                    df_failed_rows = self._failed_rows_to_pandas(failed_rule.failed_rows_dataset)

                    df_failed_rows.to_excel(writer, sheet_name=sheet_name, index=False)
                    is_excel_empty = False
            excel_buffer.seek(0)

            if is_excel_empty:
                continue
            zip_file.writestr(excel_filename, excel_buffer.read())

        return zip_file

    def _add_csv_failed_rows_attachment(
        self, result: DataValidationResult, zip_file: ZipFile
    ) -> ZipFile:
        for failed_check in result.failed_checks:
            for failed_rule in failed_check.failed_rules:
                if failed_rule.failed_rows_dataset is None:
                    continue

                csv_filename = (
                    (f"{failed_check.name}_{failed_rule.id}_{failed_rule.rule}_failed_rows.csv")
                    .replace(" ", "_")
                    .lower()
                )

                csv_buffer = StringIO()

                df_failed_rows = self._failed_rows_to_pandas(failed_rule.failed_rows_dataset)
                df_failed_rows.to_csv(csv_buffer, index=False)

                csv_buffer.seek(0)

                zip_file.writestr(csv_filename, csv_buffer.getvalue().encode("utf-8"))

        return zip_file
