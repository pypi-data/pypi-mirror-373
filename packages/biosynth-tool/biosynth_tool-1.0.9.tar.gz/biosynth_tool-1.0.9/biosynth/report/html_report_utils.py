import os

import jinja2

# Application-specific data and utilities
from biosynth.data.app_data import InputData, EliminationData, OutputData
from biosynth.utils.display_utils import SequenceUtils
from biosynth.utils.file_utils import create_dir, resource_path, save_file
from biosynth.utils.info_utils import (
    get_elimination_process_description,
    get_coding_region_cost_description,
    get_non_coding_region_cost_description,
)
from biosynth.utils.output_utils import Logger


# Convert plain text with dash-prefixed lines into HTML <ul>/<ol> + paragraphs
def convert_to_html_list(text: str, ordered=False) -> str:
    lines = text.strip().split("\n")
    list_items = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("-"):
            content = stripped[1:].strip()
            list_items.append(f"<li>{content}</li>")
        else:
            list_items.append(f"<p>{stripped}</p>")  # treat non-list lines as paragraphs

    tag = "ol" if ordered else "ul"
    html = f"<{tag}>\n" + "\n".join(li for li in list_items if li.startswith("<li>")) + f"\n</{tag}>"
    preamble = "\n".join(li for li in list_items if li.startswith("<p>"))
    return preamble + "\n" + html


class ReportController:
    # Controller responsible for constructing and saving the final HTML report
    def __init__(self, updated_coding_positions):
        # Save input DNA sequence and visually highlight coding regions
        self.input_seq = InputData.dna_sequence
        self.highlight_input = SequenceUtils.highlight_sequences_to_html(
            InputData.dna_sequence,
            InputData.coding_indexes,
            line_length=85
        )

        # Store optimized DNA sequence from backend
        self.optimized_seq = OutputData.optimized_sequence

        # Mark character-level differences between input and optimized sequences
        self.index_seq_str, self.marked_input_seq, self.marked_optimized_seq = \
            SequenceUtils.mark_non_equal_characters(
                InputData.dna_sequence,
                OutputData.optimized_sequence,
                updated_coding_positions
            )

        # Format other user input and results
        self.unwanted_patterns = ', '.join(InputData.unwanted_patterns)
        self.num_of_coding_regions = len(InputData.coding_indexes)
        self.detailed_changes = '<br>'.join(
            EliminationData.detailed_changes) if EliminationData.detailed_changes else None

        # These are generated during report creation
        self.output_text = None
        self.report_filename = None

        # Highlight regions excluded from optimization
        self.highlight_selected = SequenceUtils.highlight_sequences_to_html(
            InputData.dna_sequence,
            InputData.excluded_coding_indexes,
            line_length=85
        )

        # Format cost with good numerical precision
        self.min_cost = f"{EliminationData.min_cost:.10g}"

    def create_report(self, file_date):
        # Build the context dictionary to render the Jinja2 HTML template
        context = {
            'today_date': file_date,
            'input': self.input_seq,
            'patterns': self.unwanted_patterns,
            'highlight_input': self.highlight_input,
            'highlight_selected': self.highlight_selected,
            'num_of_coding_regions': self.num_of_coding_regions,
            'regions_list': (InputData.coding_regions_list or {}).items(),
            'excluded_regions_list': (InputData.excluded_regions_list or {}).items(),
            'elimination_process_description': convert_to_html_list(get_elimination_process_description()),
            'coding_region_cost_description': convert_to_html_list(get_coding_region_cost_description()),
            'non_coding_region_cost_description': convert_to_html_list(get_non_coding_region_cost_description()),
            'cost': self.min_cost,
            'index_seq_str': self.index_seq_str,
            'marked_input_seq': self.marked_input_seq,
            'marked_optimized_seq': self.marked_optimized_seq,
            'optimized_seq': self.optimized_seq,
            'detailed_changes': self.detailed_changes
        }

        try:
            # Load the HTML template using absolute path
            template_path = resource_path('biosynth/report/report.html')
            template_loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(template_path))
            template_env = jinja2.Environment(loader=template_loader)
            template = template_env.get_template(os.path.basename(template_path))

            # Render the HTML using the context dictionary
            self.output_text = template.render(context)

            # Save report to 'output' folder
            create_dir('output')
            self.report_filename = f"BioSynth Report - {file_date}.html"
            report_local_path = f'output/{self.report_filename}'

            with open(report_local_path, 'w', encoding="utf-8") as file:
                file.write(self.output_text)

            return report_local_path

        except jinja2.exceptions.TemplateNotFound as e:
            Logger.error(f"Template not found - {e}")
        except Exception as e:
            Logger.error(f"{e}")

        return None

    def download_report(self, path=None):
        # Allow external module (e.g., UI) to download/export the report
        return save_file(self.output_text, self.report_filename, path)
