#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A class for generating simple CLI reports"""
import csv
from typing import List, TypeVar

import rich.errors
from pathlib import Path
from rich.console import Console
from rich.table import Table

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import error_and_exit, get_current_datetime, check_file_path
from regscale.models.regscale_models.file import File

T = TypeVar("T")


class ReportGenerator:
    """
    A class for generating simple CLI reports
    """

    def __init__(self, objects: List[T], to_file: bool = False, report_name: str = "", **kwargs):
        self.console = Console()
        self.objects = objects
        self.to_file = to_file
        self.report_name = report_name
        self.regscale_id = kwargs.get("regscale_id")
        self.regscale_module = kwargs.get("regscale_module")
        reportable_attrs = []
        if objects:
            # Basic attributes for a generic report
            reportable_attrs = [
                "id",
                "dateCreated",
                "lastUpdatedById",
                "dateLastUpdated",
                "name",
                "title",
                "description",
                "created_at",
                "updated_at",
                "parent_id",
                "parent_module",
                "status",
            ]
        self.attributes = reportable_attrs
        self.generate_report()

    def report_data(self):
        """
        Return the data for the report
        """
        return self.objects

    def generate_report(self):
        """
        Generate a report for the objects in the list
        """
        if not self.objects:
            return
        report_data = []
        class_name = self.objects[0].__class__.__name__
        report_name = f"{class_name} Report" if not self.report_name else self.report_name
        table = Table(title=report_name)
        valid_attr = []
        for attribute in self.attributes:
            try:
                if getattr(self.objects[0], attribute):
                    table.add_column(attribute)
                    valid_attr.append(attribute)
            except rich.errors.NotRenderableError:
                self.console.print(f"[bold red]Attribute {attribute} is not renderable[/bold red]")
            except AttributeError:
                pass
        for obj in self.objects:
            row = []
            for attr in valid_attr:
                row.append(str(getattr(obj, attr)))
            table.add_row(*row)
            report_data.append(",".join(row))
        if self.to_file:
            self.save_report(report_name, valid_attr, report_data)
        else:
            self.console.print(table)

    def save_report(self, report_name: str, valid_attr: list, report_data: list):
        """
        Save the report to a file

        :param str report_name: The name of the report
        :param list valid_attr: The valid attributes for the report
        :param list report_data: The data for the report
        """
        try:
            posix_name = report_name.lower() + "_" + get_current_datetime()
            file_name = (f"{posix_name}.csv").lower().replace(" ", "_").replace(":", "_")
            file_path = Path("./artifacts") / file_name
            check_file_path("artifacts", False)
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(valid_attr)
                for row in report_data:
                    # write a comma delimited row to csv
                    writer.writerow(row.split(","))
        except IOError as e:
            error_and_exit(f"An error occurred while opening the file: {str(e)}")
        except csv.Error as e:
            error_and_exit(f"An error occurred while writing to the file: {str(e)}")

        if self.regscale_id and self.regscale_module:
            api = Api()
            File.upload_file_to_regscale(
                file_name=file_path.absolute(),
                parent_id=self.regscale_id,
                parent_module=self.regscale_module,
                api=api,
            )
