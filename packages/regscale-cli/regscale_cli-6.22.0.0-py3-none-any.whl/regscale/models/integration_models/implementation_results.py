#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""standard python imports"""
from rich.console import Console
from rich.table import Table


class ImplementationResults:
    """
    Stores results related to STIG (Security Technical Implementation Guide) files.

    :param str stig_file_name: The name of the STIG file.
    :param Console console: The console object to print with.
    """

    def __init__(self, stig_file_name: str, console: Console):
        self.stig_file_name = stig_file_name
        self.failed_implementations = 0
        self.passed_implementations = 0
        self.console = console

    def add_result(self, status: str):
        """
        Adds a result to the STIG file.

        :param str status: The status of the implementation.
        """
        if status == "Fully Implemented":
            self.record_passed_implementation()
        else:
            self.record_failed_implementation()

    def record_failed_implementation(self):
        """
        Records a failed implementation in the STIG file.
        """
        self.failed_implementations += 1

    def record_passed_implementation(self):
        """
        Records a passed implementation in the STIG file.
        """
        self.passed_implementations += 1

    def get_total_implementations(self) -> int:
        """
        Get the total number of implementations (both passed and failed).

        :return: The total number of implementations.
        :rtype: int
        """
        return self.failed_implementations + self.passed_implementations

    def report_log(self) -> None:
        """
        Log report of the results with colors and formatting.

        :rtype: None
        """
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("STIG File", style="cyan")
        table.add_column("Total Implementations")
        table.add_column("Passed Implementations", style="green")
        table.add_column("Failed Implementations", style="red")
        table.add_column("Success Rate (%)")
        table.add_row(
            self.stig_file_name,
            str(self.get_total_implementations()),
            str(self.passed_implementations),
            str(self.failed_implementations),
            f"{self.get_success_rate() * 100:.2f}",
        )

        self.console.print(table)

    def get_success_rate(self) -> float:
        """
        Calculate the success rate of implementations in the STIG file.

        :return: The success rate as a percentage.
        :rtype: float
        """
        if self.get_total_implementations() > 0:
            return self.passed_implementations / self.get_total_implementations()
        return 0.0
