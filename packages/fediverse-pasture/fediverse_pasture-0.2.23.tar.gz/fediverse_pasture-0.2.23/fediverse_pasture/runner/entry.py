# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import json
import textwrap
from dataclasses import dataclass, field
from typing import Dict, Set, List, Callable
import logging

logger = logging.getLogger(__name__)


@dataclass
class Entry:
    """Represents an entry to generate support tables from."""

    entry: Dict[str, Dict] = field(
        metadata={
            "description": "Dictionary indexed by application with values the result"
        }
    )

    @property
    def applications(self) -> Set[str]:
        """Returns the set of application names"""
        return set(self.entry.keys())

    @property
    def activity(self) -> Dict:
        result = self.entry.get("activity")
        if result is None:
            raise ValueError("No activity data found in entry")
        return result

    @property
    def object(self):
        activity = self.activity
        obj = activity.get("object", {})
        return {"@context": activity["@context"], **obj}

    def present_for(self, application):
        return application in self.entry

    def as_tabs(self, apps: List[str]) -> List[str]:
        """Renders the data for each application as tabbed markdown.

        If no data is present "no result" is shown.

        :param apps: List of applications to display"""
        lines = []
        for application_name in apps:
            lines.append(f"""=== "{application_name}"\n""")

            if application_name in self.entry:
                text = f"""```json title="{application_name}"\n"""
                text += json.dumps(self.entry[application_name], indent=2)
                text += "\n```\n"
                lines += textwrap.indent(text, " " * 4).split("\n")
            else:
                lines.append("    no result")

            lines += [""]

        return [x + "\n" for x in lines]

    def as_grid(self, apps: List[str]) -> List[str]:
        """Renders the data for each application as a grid.

        If no data is present "no result" is shown.

        :param apps: List of applications to display"""
        lines = ["""<div class="grid" markdown>\n"""]
        for application_name in apps:
            if application_name in self.entry:
                text = f"""```json title="{application_name}"\n"""
                text += json.dumps(self.entry[application_name], indent=2)
                text += "\n```\n"
                lines += textwrap.indent(text, " " * 0).split("\n")
            else:
                lines.append("no result")

            lines += [""]

        lines.append("</div>")

        return [x + "\n" for x in lines]

    def apply_to(
        self, application: str, function: Callable[[Dict], List[str]]
    ) -> List[str]:
        """Applies the function to the entry for the given application.

        :param application: The application name
        :param function: extractor for the desired data"""
        try:
            data = self.entry.get(application)
            if data is None:
                logger.warning(f"No data found for application {application}")
                return ["-"]

            return function(data)
        except Exception as e:
            logger.exception(e)
            return ["-"]

    @staticmethod
    def from_result_list(result):
        val = {x["application_name"]: x for x in result}
        for x in val:
            del val[x]["application_name"]
        return Entry(val)
