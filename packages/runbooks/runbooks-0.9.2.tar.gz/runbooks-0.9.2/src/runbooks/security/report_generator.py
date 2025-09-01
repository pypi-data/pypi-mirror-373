import datetime
import os
from pathlib import Path
from string import Template

from jinja2 import Template

from runbooks.common.rich_utils import (
    console,
    create_panel,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from runbooks.utils.logger import configure_logger

from .utils import language, level_const

## ✅ Configure Logger
logger = configure_logger(__name__)


class ReportGenerator:
    def __init__(self, account_id, results, language_code):
        self.account_id = account_id
        self.results = results
        self.language = language_code
        self.generated_at = datetime.datetime.now().strftime("(UTC) %Y-%m-%d %H:%M:%S")

    def create_html_report(self):
        template = self._load_template()
        context = self._prepare_context()
        return template.render(context)

    def _load_template(self):
        """
        Load the appropriate HTML template based on self.language.

        Supported languages: KR, JP, VN, EN (default).
        Falls back to English template if self.language is unrecognized.
        """
        ## Normalize user input like "en", "En", "EN" -> "EN"
        lang = self.language.upper() if self.language else "EN"

        ## Map language codes to template filenames
        template_map = {
            "KR": "report_template_kr.html",
            "JP": "report_template_jp.html",
            "VN": "report_template_vn.html",
            "EN": "report_template_en.html",
        }

        ## Fall back to English if language code not recognized
        template_filename = template_map.get(lang, "report_template_en.html")

        # Always resolve paths relative to this file’s directory
        script_dir = Path(__file__).resolve().parent
        template_path = script_dir / template_filename

        ## Attempt to read the template file
        if not template_path.is_file():
            error_msg = f"Template file '{template_filename}' for language '{lang}' not found at {template_path}"
            print_error(error_msg)
            logger.error(
                "Template file '%s' for language '%s' not found at %s",
                template_filename,
                lang,
                template_path,
            )
            raise FileNotFoundError(f"Could not find the template '{template_filename}' for language '{lang}'.")

        with template_path.open("r", encoding="utf-8") as file:
            return Template(file.read())

        # if self.language == "KR":
        #     with open("report_template_kr.html", "r") as file:
        #         return Template(file.read())
        # elif self.language == "JP":
        #     with open("report_template_jp.html", "r") as file:
        #         return Template(file.read())
        # elif self.language == "VN":
        #     with open("report_template_vn.html", "r") as file:
        #         return Template(file.read())
        # else:
        #     ## Get the absolute directory where *this script* is located
        #     report_dir = os.path.dirname(os.path.abspath(__file__))
        #     report_path = os.path.join(report_dir, "report_template_en.html")
        #     ## with open("report_template_en.html", "r") as file:
        #     with open(report_path, "r") as file:
        #         return Template(file.read())

    def _prepare_context(self):
        return {
            "account_id": self.account_id,
            "generated_at": self.generated_at,
            "overview": self._generate_overview(),
            "result_sections": self._generate_result_sections(),
            "language": self.language,
        }

    def _generate_overview(self):
        filtered_results = {level: len(results) for level, results in self.results.items() if isinstance(results, list)}
        desired_levels = ["Danger", "Warning", "Success", "Info", "Error"]
        sorted_result = [(level, filtered_results[level]) for level in desired_levels]

        return sorted_result

    def _generate_result_sections(self):
        sections = []
        for level, results in self.results.items():
            if isinstance(results, list):
                if len(results) == 0:
                    ## This condition only applies when there are no 'Error' items at all.
                    formatted_results = [
                        {
                            "title": "All inspection items were successfully checked.",
                            "message": "No results available for this section. All checks were successful.",
                            "table": [],
                        }
                    ]
                else:
                    formatted_results = self._format_results(results, level)

                sections.append({"level": level, "result_items": formatted_results})

        sort_order = {"Danger": 0, "Warning": 1, "Success": 2, "Info": 3, "Error": 4}

        sections.sort(key=lambda x: sort_order.get(x["level"], len(sort_order)))
        return sections

    def _format_results(self, results, level):
        formatted_results = []
        for result in results:
            if isinstance(result, dict):  # if type(result) is dict
                formatted_result = {
                    "title": result.get("title", "Unknown"),
                    "message": result.get("msg", "No message"),
                    "table": self._format_table(result.get("result_cols", []), result.get("result_rows", [])),
                }
                if level == level_const.error:
                    formatted_result["error_message"] = result.get("error_message", "Unknown error")
                formatted_results.append(formatted_result)
            elif hasattr(result, "to_dict"):  # if the result object has 'to_dict' attribute
                result_dict = result.to_dict()
                formatted_result = {
                    "title": result_dict.get("title", "Unknown"),
                    "message": result_dict.get("msg", "No message"),
                    "table": self._format_table(
                        result_dict.get("result_cols", []),
                        result_dict.get("result_rows", []),
                    ),
                }
                if level == level_const.error:
                    formatted_result["error_message"] = result_dict.get("error_message", "Unknown error")
                formatted_results.append(formatted_result)

        return formatted_results

    def _format_table(self, cols, rows):
        if not rows:
            return None
        return {"headers": cols, "rows": rows}


def generate_html_report(account_id_str, result_sort_by_level, language_code):
    generator = ReportGenerator(account_id_str, result_sort_by_level, language_code)
    return generator.create_html_report()
