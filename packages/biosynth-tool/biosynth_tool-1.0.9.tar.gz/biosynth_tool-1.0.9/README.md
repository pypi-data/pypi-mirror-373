[![Build Status](https://github.com/HadarPur/RU-BioSynth/actions/workflows/ci.yml/badge.svg)](https://github.com/hadarpur/RU-BioSynth/actions)
[![Latest Release](https://img.shields.io/pypi/v/biosynth-tool.svg)](https://pypi.org/project/biosynth-tool/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/biosynth-tool.svg)](https://pypi.org/project/biosynth-tool/)
[![License](http://img.shields.io/:license-apache-blue.svg)](https://github.com/HadarPur/RU-BioSynth/blob/main/LICENSE)


[![Python Version](https://img.shields.io/pypi/pyversions/biosynth-tool.svg)](https://www.python.org/)


# Flexible and comprehensive software app for design of synthetic DNA sequences without unwanted patterns

BioSynth is a software application for designing synthetic DNA sequences while eliminating unwanted patterns and considering codon usage bias.

## Installation

Install BioSynth directly from PyPI:

```
pip install biosynth-tool
```

This will automatically install all required dependencies.

### Using a Virtual Environment (Recommended)

To avoid conflicts, create a Python virtual environment before installation:

#### macOS/Linux:

```bash
python3 -m venv biosynth_venv
source biosynth_venv/bin/activate
pip install biosynth-tool
```

#### Windows (Command Prompt):

```cmd
 python -m venv biosynth_venv
 biosynth_venv\Scripts\activate
 pip install biosynth-tool
```

## Pre Processing

To operate the application, the user must provide the following **three input text files**:

1. **Target sequence file** – a plain text file containing a DNA sequence composed exclusively of the characters A, T,
   G, and C. The sequence must be provided on a **single continuous line**. For example:

    ```
    ATAGTACATATC
    ```

2. **Unwanted pattern list** – a plain text file containing DNA patterns (substrings) that should be eliminated from the
   target sequence. Each pattern must appear **on a separate line**, separated by whitespace. For example:

    ```
    TAGTAC
    ATATCA
    ```

3. **Codon usage file** – a plain-text file that defines the relative codon usage frequencies for a specific organism.
   To obtain and prepare this file:

   ### Step 1: Extract Codon Usage Data

    1. Visit the Kazusa Codon Usage Database:  
       https://www.kazusa.or.jp/codon/

    2. Under the **QUERY Box for search with Latin name of organism**, enter the name of the organism. For example:  
       `Marchantia polymorpha`

    3. Click the **Submit** button.

    4. In the search results, locate the desired genome type (e.g., `chloroplast`) and click the corresponding link
       under the `Link` column.

    5. The codon usage table will appear. Ensure to choose a format and then click **submit**. You should see the
       following header:

        ```
        fields: [triplet] [amino acid] [fraction] [frequency: per thousand] ([number])
        ```

    6. Select the entire codon usage table (not including the header), for example:

        ```
        UUU F 0.94 63.5 (  1558)  UCU S 0.40 25.8 (   634)  UAU Y 0.89 33.4 (   820)  UGU C 0.85  8.6 (   212)
        UUC F 0.06  4.4 (   107)  UCC S 0.05  3.0 (    73)  UAC Y 0.11  4.1 (   100)  UGC C 0.15  1.5 (    38)
        ...
        ```

    7. Copy and paste it into a plain text file.

    8. Save the file.

   ### Step 2: Convert to BioSynth Format

    1. Download local script named `convert_kazusa_to_biosynth.py` from the BioSynth repository: https://github.com/HadarPur/RU-BioSynth/blob/main/convert_kazusa_to_biosynth.py

    2. This script reads the codon usage file you just created and outputs a two-column text file in the format required
       by the BioSynth app: each line should contain a codon followed by its usage frequency, separated by whitespace.

    3. Run the script from the command line:

        ```bash
        cd /path/to/script_directory
        python ./convert_kazusa_to_biosynth.py <codon_usage_file_path> -o <output_file>
        ```
      
    4. The output file will consist of lines in the following form:

        ```
        TAC 0.56
        GCT 0.89
        ...
        ```

   This transformation ensures that rare codons have higher substitution costs, reflecting biological codon bias.

   **Note:**  
   If you wish to get the table from another resource, please make sure to write your own converter script to ensure
   that you are in the right format.

## Executing the Command Line Interface (CLI)

To execute the elimination tool via the terminal, use the following command:

```
biosynth -s <seq_file> -p <pattern_file> -c <codon_usage_file> -a <alpha> -b <beta> -w <w>
```

### Examples
For example, you can run the program using short options:

```
biosynth -s s_file_no_coding.txt -p p_file_no_coding.txt -c biosynth_codon_usage.txt -a 1.02 -b 1.98 -w 99.96
```

Or, with the full option names:

```bash
# macOS/Linux (bash, zsh)
biosynth --target_sequence s_file_no_coding.txt \
         --unwanted_patterns p_file_no_coding.txt \
         --codon_usage codon_usage_chloroplast.txt \
         --alpha 1.02 \
         --beta 1.98 \
         --non_synonymous_w 99.96
```

## Executing the Graphical User Interface (GUI)

To launch the graphical user interface of the elimination tool, run:

```
biosynth -g
```

You're all set! 🚀
