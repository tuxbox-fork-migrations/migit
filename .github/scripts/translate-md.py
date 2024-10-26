#!/usr/bin/env python3
"""
Markdown File Translation Script

This script translates a Markdown template file into multiple languages, handling specific placeholders
and ensuring that important content like code blocks, anchors, headers, URLs, images, HTML elements,
inline code, tables, and LaTeX formulas are preserved throughout the translation process.

It uses Google Translate to automatically translate content while keeping specific sections intact.
It also updates language links in all translated markdown files to allow easy navigation between different
language versions.

Features:
- Detects the source language automatically and translates the content into specified target languages,
  including the source language.
- Handles placeholders for code blocks, anchors, headers, URLs, images, HTML elements, inline code,
  tables, and LaTeX formulas to ensure the consistency of formatting.
- Updates or adds language links to navigate between different language versions.
- Allows specifying the output directory, file prefix, main document file name, and configuration file.

Usage:
- Run the script from the command line, specifying the Markdown template file using the `-t` argument.
- Optionally, specify the output directory with `-o`, the file prefix with `-p`, the main document file name
  with `-m`, and the configuration file with `-c`.
- Example: `python translate_readme.py -t template.md -o translated_readmes -p DOC_ -m MAIN_DOC.md -c config.json`
- Use also argument --help or take a look at README file.

Dependencies:
- googletrans (to install: `pip install googletrans==3.1.0a0`)
  **NOTE:** Version >= 4 may not work stably or may cause problems!

License:
- GPL2

Author:
- Copyright (C) Thilo Graf 2024 https://github.com/dbt1/translate-md
"""

import os
import re
import sys
import json
import logging
import argparse

# Version of the script
VERSION = "1.0"

# Set version of googletrans
GOOGLETRANS_VERSION = "3.1.0a0"

try:
    from importlib.metadata import version as get_version, PackageNotFoundError  # Python 3.8+
except ImportError:
    from importlib_metadata import version as get_version, PackageNotFoundError  # For older Python versions (< 3.8)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable for target languages
TARGET_LANGUAGES = {}

def check_googletrans_version(required_version=GOOGLETRANS_VERSION):
    """
    Checks if the installed version of googletrans matches the required version.
    """
    try:
        installed_version = get_version('googletrans')
        if installed_version != required_version:
            logging.warning(
                f"Warning: The installed version of googletrans is {installed_version}, but {required_version} is required. "
                f"Please install the correct version with 'pip install googletrans=={required_version}'."
            )
    except PackageNotFoundError:
        logging.error(f"The module 'googletrans' is not installed. Install it with 'pip install googletrans=={GOOGLETRANS_VERSION}'.")
        sys.exit(1)

# Define the function before calling it
check_googletrans_version(GOOGLETRANS_VERSION)

# Import googletrans after checking the version
try:
    from googletrans import Translator, LANGUAGES
except ImportError:
    logging.error(f"The module 'googletrans' is not installed. Install it with 'pip install googletrans=={GOOGLETRANS_VERSION}'.")
    sys.exit(1)

# Default source languages with flag emojis
DEFAULT_TARGET_LANGUAGES = {
    "de": ["German", "🇩🇪"],  # Default language
}

# Placeholder templates marked with '@' for easier recognition
CODE_PLACEHOLDER = "@CODE_BLOCK_{}@"
ANCHOR_PLACEHOLDER = "@ANCHOR_{}@"
HEADER_PLACEHOLDER = "@HEADER_PLACEHOLDER_{}@"
URL_PLACEHOLDER = "@URL_PLACEHOLDER_{}@"
IMAGE_PLACEHOLDER = "@IMAGE_{}@"
HTML_PLACEHOLDER = "@HTML_{}@"
INLINE_CODE_PLACEHOLDER = "@INLINE_CODE_{}@"
TABLE_PLACEHOLDER = "@TABLE_{}@"
LATEX_PLACEHOLDER = "@LATEX_{}@"

# Markers for the section containing language links
LANGUAGE_LINKS_START = "<!-- LANGUAGE_LINKS_START -->"
LANGUAGE_LINKS_END = "<!-- LANGUAGE_LINKS_END -->"

def detect_language(text, translator):
    """
    Detects the language of the given text.

    Args:
        text (str): Text to detect the language of.
        translator (Translator): An instance of googletrans Translator.

    Returns:
        str: Detected language code.

    Raises:
        SystemExit: If any error occurs.
    """
    try:
        detection = translator.detect(text)
        detected_lang = detection.lang.lower()
        return detected_lang
    except Exception as e:
        logging.exception(f"Error during language detection: {e}")
        sys.exit(1)

def load_template(template_file, target_filenames):
    """
    Loads the template from the specified file.
    Checks if the template file is not among the target files to avoid overwriting.

    Args:
        template_file (str): Path to the template file.
        target_filenames (list): List of target filenames.

    Returns:
        str: Content of the template file.

    Raises:
        SystemExit: If any error occurs.
    """
    if not os.path.exists(template_file):
        logging.error(f"Error: The template file '{template_file}' was not found.")
        sys.exit(1)
    if os.path.getsize(template_file) == 0:
        logging.error(f"Error: The template file '{template_file}' is empty.")
        sys.exit(1)
    if not template_file.lower().endswith('.md'):
        logging.error(f"Error: The template file '{template_file}' is not a Markdown file.")
        sys.exit(1)
    if os.path.abspath(template_file) in [os.path.abspath(f) for f in target_filenames]:
        logging.error("Error: The template file must not have the same name as any of the target files.")
        sys.exit(1)
    try:
        with open(template_file, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.exception(f"Error reading the template file '{template_file}': {e}")
        sys.exit(1)

def extract_placeholders(content):
    """
    Extracts code blocks, anchors, headers, URLs, images, HTML elements, inline code, tables,
    and LaTeX formulas, and replaces them with placeholders.

    Args:
        content (str): The content to process.

    Returns:
        Tuple containing:
            - content (str): Content with placeholders.
            - code_blocks (list): List of code blocks.
            - anchor_placeholders (dict): Mapping of placeholders to anchors.
            - headers (list): List of tuples (header_level, header_text).
            - url_placeholders (dict): Mapping of placeholders to URLs.
            - images (list): List of images.
            - html_elements (list): List of HTML elements.
            - inline_codes (list): List of inline code segments.
            - tables (list): List of tables.
            - latex_formulas (list): List of LaTeX formulas.
    """
    code_blocks = []
    anchor_placeholders = {}
    headers = []
    url_placeholders = {}
    images = []
    html_elements = []
    inline_codes = []
    tables = []
    latex_formulas = []

    # Replace code blocks
    def replace_code_block(match):
        code_block = match.group(0)
        code_blocks.append(code_block)
        index = len(code_blocks) - 1
        placeholder = CODE_PLACEHOLDER.format(index)
        return placeholder

    content = re.sub(r'```[\s\S]*?```', replace_code_block, content, flags=re.DOTALL)

    # Replace anchors
    def replace_anchor(match):
        anchor = match.group(1)
        index = len(anchor_placeholders)
        placeholder = ANCHOR_PLACEHOLDER.format(index)
        anchor_placeholders[placeholder] = anchor
        return f"({placeholder})"

    content = re.sub(r'\(#([^)]+)\)', replace_anchor, content)

    # Replace headers and capture header level and text
    def replace_header(match):
        header_marks = match.group(1)  # e.g., '##'
        header_text = match.group(2)   # e.g., 'Header Text'
        header_level = len(header_marks)
        headers.append((header_level, header_text))
        placeholder = HEADER_PLACEHOLDER.format(len(headers)-1)
        return placeholder

    content = re.sub(r'^(#+)\s+(.*)', replace_header, content, flags=re.MULTILINE)

    # Replace URLs within links
    def replace_url(match):
        url = match.group(1)
        index = len(url_placeholders)
        placeholder = URL_PLACEHOLDER.format(index)
        url_placeholders[placeholder] = url
        return f"({placeholder})"

    content = re.sub(r'\((https?://[^\s)]+)\)', replace_url, content)

    # Replace images
    def replace_image(match):
        image = match.group(0)
        images.append(image)
        index = len(images) - 1
        placeholder = IMAGE_PLACEHOLDER.format(index)
        return placeholder

    content = re.sub(r'!\[.*?\]\(.*?\)', replace_image, content)

    # Replace HTML elements
    def replace_html(match):
        html_element = match.group(0)
        html_elements.append(html_element)
        index = len(html_elements) - 1
        placeholder = HTML_PLACEHOLDER.format(index)
        return placeholder

    content = re.sub(r'<[^>]+>', replace_html, content)

    # Replace inline code
    def replace_inline_code(match):
        inline_code = match.group(0)
        inline_codes.append(inline_code)
        index = len(inline_codes) - 1
        placeholder = INLINE_CODE_PLACEHOLDER.format(index)
        return placeholder

    content = re.sub(r'`[^`]+`', replace_inline_code, content)

    # Replace LaTeX formulas
    def replace_latex(match):
        latex = match.group(0)
        latex_formulas.append(latex)
        index = len(latex_formulas) - 1
        placeholder = LATEX_PLACEHOLDER.format(index)
        return placeholder

    content = re.sub(r'\$\$.*?\$\$|\$.*?\$', replace_latex, content, flags=re.DOTALL)

    # Replace tables
    def replace_table(match):
        table = match.group(0)
        tables.append(table)
        index = len(tables) - 1
        placeholder = TABLE_PLACEHOLDER.format(index)
        return placeholder

    # A simple regex to match tables
    content = re.sub(r'((?:\|.*?\|(?:\n|$))+)', replace_table, content)

    return (content, code_blocks, anchor_placeholders, headers, url_placeholders,
            images, html_elements, inline_codes, tables, latex_formulas)

def translate_content(content, translator, src_lang, dest_lang):
    """
    Translates content from the source to the target language.

    Args:
        content (str): Content to translate.
        translator (Translator): An instance of googletrans Translator.
        src_lang (str): Source language code.
        dest_lang (str): Destination language code.

    Returns:
        str: Translated content.

    Raises:
        SystemExit: If any error occurs.
    """
    try:
        translation = translator.translate(content, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        logging.exception(f"Error during translation to '{dest_lang}': {e}")
        sys.exit(1)

def generate_anchor(text):
    """
    Generates an anchor from the given text.

    Args:
        text (str): Text to generate the anchor from.

    Returns:
        str: Generated anchor.
    """
    anchor = re.sub(r'[^\w\s-]', '', text).strip().lower()
    anchor = re.sub(r'[\s]+', '-', anchor)
    return anchor

def restore_placeholders(translated_content, code_blocks, anchor_placeholders, headers, url_placeholders,
                         images, html_elements, inline_codes, tables, latex_formulas,
                         translator, src_lang, dest_lang):
    """
    Restores placeholders with the original or translated content.

    Args:
        translated_content (str): Content with placeholders.
        code_blocks (list): List of code blocks.
        anchor_placeholders (dict): Mapping of placeholders to anchors.
        headers (list): List of tuples (header_level, header_text).
        url_placeholders (dict): Mapping of placeholders to URLs.
        images (list): List of images.
        html_elements (list): List of HTML elements.
        inline_codes (list): List of inline code segments.
        tables (list): List of tables.
        latex_formulas (list): List of LaTeX formulas.
        translator (Translator): An instance of googletrans Translator.
        src_lang (str): Source language code.
        dest_lang (str): Destination language code.

    Returns:
        str: Content with placeholders restored.
    """
    # Restore headers and generate new anchors
    new_anchors = {}
    for i, (header_level, header_text) in enumerate(headers):
        placeholder = HEADER_PLACEHOLDER.format(i)
        # Translate header
        try:
            header_translation = translator.translate(header_text, src=src_lang, dest=dest_lang)
            translated_header_text = header_translation.text.strip()
        except Exception as e:
            logging.exception(f"Error translating header '{header_text}': {e}")
            translated_header_text = header_text
        # Re-add '#' symbols based on original header level
        translated_header = f"{'#' * header_level} {translated_header_text}"
        # Generate new anchor
        new_anchor = generate_anchor(translated_header_text)
        new_anchors[placeholder] = (translated_header, new_anchor)

    # Replace header placeholders
    for placeholder, (translated_header, _) in new_anchors.items():
        translated_content = translated_content.replace(placeholder, translated_header)

    # Replace anchor placeholders
    for placeholder, original_anchor in anchor_placeholders.items():
        # Find the corresponding header to get the new anchor
        header_index = None
        for idx, (header_level, header_text) in enumerate(headers):
            # Generate original anchor
            original_anchor_generated = generate_anchor(header_text)
            if original_anchor_generated == original_anchor:
                header_index = idx
                break
        if header_index is not None:
            new_anchor = new_anchors[HEADER_PLACEHOLDER.format(header_index)][1]
        else:
            new_anchor = original_anchor  # Fallback if no matching header is found
        translated_content = translated_content.replace(placeholder, f"#{new_anchor}")

    # Restore code blocks
    for i, code_block in enumerate(code_blocks):
        placeholder = CODE_PLACEHOLDER.format(i)
        translated_content = translated_content.replace(placeholder, code_block)

    # Restore URLs
    for placeholder, url in url_placeholders.items():
        translated_content = translated_content.replace(placeholder, url)

    # Restore images
    for i, image in enumerate(images):
        placeholder = IMAGE_PLACEHOLDER.format(i)
        translated_content = translated_content.replace(placeholder, image)

    # Restore HTML elements
    for i, html_element in enumerate(html_elements):
        placeholder = HTML_PLACEHOLDER.format(i)
        translated_content = translated_content.replace(placeholder, html_element)

    # Restore inline code
    for i, inline_code in enumerate(inline_codes):
        placeholder = INLINE_CODE_PLACEHOLDER.format(i)
        translated_content = translated_content.replace(placeholder, inline_code)

    # Restore tables
    for i, table in enumerate(tables):
        placeholder = TABLE_PLACEHOLDER.format(i)
        translated_content = translated_content.replace(placeholder, table)

    # Restore LaTeX formulas
    for i, latex in enumerate(latex_formulas):
        placeholder = LATEX_PLACEHOLDER.format(i)
        translated_content = translated_content.replace(placeholder, latex)

    # Fix links that have a space between ] and ( in links
    # This addresses cases where the translator inserted spaces between ] and (
    translated_content = re.sub(r'\]\s*\(', '](', translated_content)

    return translated_content

def is_filename_in_namespace(main_doc, prefix):
    """
    Checks if the main_doc filename starts with the prefix or matches the base name of the prefix.

    Args:
        main_doc (str): Name of the main readme file.
        prefix (str): Prefix for the translated readme files.

    Returns:
        bool: True if there is a conflict, False otherwise.
    """
    # Extract the base name without extension
    main_base = os.path.splitext(main_doc)[0].lower()

    # Extract the expected base name from the prefix
    if prefix.endswith('_'):
        expected_base = prefix[:-1].lower()
    else:
        expected_base = prefix.lower()

    # Check if main_base equals expected_base or starts with expected_base + '_'
    if main_base == expected_base or main_base.startswith(expected_base + '_'):
        return True  # Conflict
    else:
        return False  # No conflict

def add_or_update_language_links(content, translated_files, main_doc, prefix, current_lang_code=None):
    """
    Adds or updates language links in the content.
    - If current_lang_code is provided, the corresponding language link is greyed out.
    - main_doc is the name of the main readme file.
    - translated_files is a dict mapping language codes to their respective filenames.

    Args:
        content (str): The content to add language links to.
        translated_files (dict): Dictionary of language codes to filenames.
        main_doc (str): Name of the main readme file.
        prefix (str): Prefix used for translated files.
        current_lang_code (str): The language code of the current content.

    Returns:
        str: Content with language links added or updated.
    """
    language_links = []
    for code, (lang_name, flag) in sorted(TARGET_LANGUAGES.items()):
        if code == current_lang_code:
            # Grey out the current language link
            link = f"<span style=\"color: grey;\">{flag} {lang_name}</span>"
        else:
            # Link to the language-specific readme files
            link = f"[{flag} {lang_name}]({translated_files[code]})"
        language_links.append(link)
    language_links_block = f"{LANGUAGE_LINKS_START}\n{' | '.join(language_links)}\n{LANGUAGE_LINKS_END}"

    # Check if the language links block already exists
    if LANGUAGE_LINKS_START in content and LANGUAGE_LINKS_END in content:
        # Replace existing block
        pattern = re.compile(f"{re.escape(LANGUAGE_LINKS_START)}.*?{re.escape(LANGUAGE_LINKS_END)}", re.DOTALL)
        content = pattern.sub(language_links_block, content)
    else:
        # Add language links at the beginning
        content = f"{language_links_block}\n\n{content}"

    return content

def create_main_doc(output_dir, main_doc, translated_files, prefix):
    """
    Creates or updates the main readme file with only language links.

    Args:
        output_dir (str): Directory to save the main readme file.
        main_doc (str): Name of the main readme file.
        translated_files (dict): Dictionary of language codes to filenames.
        prefix (str): Prefix used for translated files.
    """
    main_output_file = os.path.join(output_dir, main_doc)
    logging.info(f"Creating/updating main document at '{main_output_file}'")

    language_links = []
    for code, (lang_name, flag) in sorted(TARGET_LANGUAGES.items()):
        link = f"[{flag} {lang_name}]({translated_files[code]})"
        language_links.append(link)
    language_links_block = f"{LANGUAGE_LINKS_START}\n{' | '.join(language_links)}\n{LANGUAGE_LINKS_END}"

    # Create main readme content with only language links
    main_content = (
        f"# Documentation\n\n"
        f"This document is available in the following languages:\n\n"
        f"{language_links_block}\n\n"
        f"Please choose your preferred language by clicking on the links above."
    )

    # Save the main readme file
    try:
        with open(main_output_file, 'w', encoding='utf-8') as file:
            file.write(main_content)
        logging.info(f"Main document saved to '{main_output_file}'")
    except Exception as e:
        logging.exception(f"Error writing to '{main_output_file}': {e}")
        sys.exit(1)

def prepare_target_files(output_dir, translated_files, source_lang_code, source_lang_name):
    """
    Prepares all target files by writing placeholder for translated content.

    Args:
        output_dir (str): Directory where the translated files are saved.
        translated_files (dict): Mapping of language codes to filenames.
        source_lang_code (str): Language code of the source document.
        source_lang_name (str): Name of the source language.
    """
    for code, filename in translated_files.items():
        target_lang_name, target_lang_flag = TARGET_LANGUAGES[code]
        translated_file_path = os.path.join(output_dir, filename)

        # Initialize content with placeholder only
        content = "<!-- TRANSLATED_CONTENT -->\n"

        # **Always overwrite the target file**
        try:
            with open(translated_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logging.info(f"Prepared target file '{translated_file_path}'.")
        except Exception as e:
            logging.exception(f"Error preparing target file '{translated_file_path}': {e}")
            sys.exit(1)

def insert_translated_content(translated_file_path, translated_content):
    """
    Inserts the translated content at the placeholder position in the target file.

    Args:
        translated_file_path (str): Path to the translated file.
        translated_content (str): The translated Markdown content.
    """
    try:
        with open(translated_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if '<!-- TRANSLATED_CONTENT -->' not in content:
            logging.error(
                f"Placeholder '<!-- TRANSLATED_CONTENT -->' not found in '{translated_file_path}'. Insertion skipped."
            )
            return

        # Replace the placeholder with the translated content
        updated_content = content.replace('<!-- TRANSLATED_CONTENT -->', translated_content)

        with open(translated_file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        logging.info(f"Inserted translated content into '{translated_file_path}'.")
    except Exception as e:
        logging.exception(f"Error inserting translated content into '{translated_file_path}': {e}")

def get_flag_emoji(country_code):
    """
    Converts a two-letter country code into a corresponding flag emoji.

    Args:
        country_code (str): Two-letter country or language code.

    Returns:
        str: Corresponding flag emoji.
    """
    if len(country_code) != 2:
        return ''  # Return empty string if input is not a valid two-letter code

    # Convert the country code to uppercase
    country_code = country_code.upper()

    # Convert the country code into flag emoji
    flag_emoji = ''.join(chr(0x1F1E6 + ord(char) - ord('A')) for char in country_code)

    return flag_emoji

def main():
    """
    Main function of the script.
    """
    # Argument parser for command line arguments with custom help formatter
    parser = argparse.ArgumentParser(
        description=f'%(prog)s v{VERSION}, Translates a Markdown template into multiple languages.',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40, width=100)
    )

    # Define default values
    default_template_file = 'template.md'
    default_output_dir = '.'
    default_prefix = 'DOC_'
    default_main_doc = 'DOC.md'
    default_config_file = None

    parser.add_argument(
        '-t', '--template-md',
        metavar='TEMPLATE_FILE',
        default=default_template_file,
        help=f'Path to the template file (default: {default_template_file})'
    )
    parser.add_argument(
        '-o', '--output-dir',
        metavar='OUTPUT_DIR',
        default=default_output_dir,
        help=f'Directory to save the translated files (default: {default_output_dir})'
    )
    parser.add_argument(
        '-p', '--prefix',
        metavar='PREFIX',
        default=default_prefix,
        help=f'Prefix for the translated file names (default: {default_prefix})'
    )
    parser.add_argument(
        '-m', '--main-doc',
        metavar='MAIN_DOC',
        default=default_main_doc,
        help=f'Name of the main document file (default: {default_main_doc})'
    )
    parser.add_argument(
        '-c', '--config-file',
        metavar='CONFIG_FILE',
        default=default_config_file,
        help='Path to configuration file (optional)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s v{VERSION}'
    )
    args = parser.parse_args()

    # Load configuration from config file if specified
    config = {}
    if args.config_file:
        if not os.path.exists(args.config_file):
            logging.error(f"Configuration file '{args.config_file}' not found.")
            sys.exit(1)
        try:
            with open(args.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Log the usage of external config file
            logging.info(f"Using external configuration file: {os.path.abspath(args.config_file)}")
        except Exception as e:
            logging.exception(f"Error loading configuration file '{args.config_file}': {e}")
            sys.exit(1)

    # Override default parameters with config values
    template_file = config.get('template_md', args.template_md)
    output_dir = config.get('output_dir', args.output_dir)
    prefix = config.get('prefix', args.prefix)
    main_doc = config.get('main_doc', args.main_doc)
    target_languages_config = config.get('target_languages', None)

    # Prepare target languages
    global TARGET_LANGUAGES
    if target_languages_config:
        if isinstance(target_languages_config, dict):
            # Ensure all language entries are lists or tuples with (language name, flag)
            valid = True
            for code, value in target_languages_config.items():
                if not (isinstance(value, list) or isinstance(value, tuple)) or len(value) != 2:
                    logging.error(f"Invalid format for language '{code}': {value}. Must be a list or tuple of [name, flag].")
                    valid = False
            if not valid:
                logging.error("Invalid 'target_languages' format in configuration. Each language must have a name and a flag.")
                sys.exit(1)
            TARGET_LANGUAGES = target_languages_config
        else:
            logging.error("Invalid format for 'target_languages' in configuration. It should be a dictionary.")
            sys.exit(1)
    else:
        TARGET_LANGUAGES = DEFAULT_TARGET_LANGUAGES

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logging.info(f"Created output directory '{output_dir}'.")
        except Exception as e:
            logging.exception(f"Error creating output directory '{output_dir}': {e}")
            sys.exit(1)

    # Load the template content first to detect the source language
    content = load_template(template_file, [os.path.join(output_dir, f"{prefix}{code}.md") for code in TARGET_LANGUAGES])

    translator = Translator()

    # Detect source language
    source_lang_code = detect_language(content, translator)
    if source_lang_code not in TARGET_LANGUAGES:
        # Add source language to TARGET_LANGUAGES if not present
        source_lang_name = LANGUAGES.get(source_lang_code, source_lang_code).capitalize()
        source_lang_flag = get_flag_emoji(source_lang_code)
        TARGET_LANGUAGES[source_lang_code] = (source_lang_name, source_lang_flag)
    else:
        source_lang_name, source_lang_flag = TARGET_LANGUAGES[source_lang_code]
    logging.info(f"Detected source language: {source_lang_name} ({source_lang_code})")

    # Now, prepare translated_files after updating TARGET_LANGUAGES
    translated_files = {code: f"{prefix}{code}.md" for code in TARGET_LANGUAGES}

    # Check that the template file is not among the target files
    target_filenames = [os.path.join(output_dir, filename) for filename in translated_files.values()]
    template_file_path = os.path.abspath(template_file)

    if os.path.abspath(template_file_path) in [os.path.abspath(f) for f in target_filenames]:
        logging.error("Error: The template file must not have the same name as any of the target files.")
        sys.exit(1)

    # Log potential conflict
    if not is_filename_in_namespace(main_doc, prefix):
        logging.warning(
            f"The main document file name '{main_doc}' starts not with the namespace'{prefix}'s. Use the '-m' parameter to set another main file or set '-p' parameter for another prefix."
        )

    # Create or update the main readme file with only language links
    create_main_doc(output_dir, main_doc, translated_files, prefix)

    # Prepare all target files with placeholder only (always overwrite)
    prepare_target_files(output_dir, translated_files, source_lang_code, source_lang_name)

    # Translate content for all languages, including the source language
    for dest_lang in TARGET_LANGUAGES:
        target_lang_name, target_lang_flag = TARGET_LANGUAGES[dest_lang]
        translated_file = os.path.join(output_dir, translated_files[dest_lang])
        logging.info(f"Translating '{template_file}' from {source_lang_name} to {target_lang_name}")

        # Extract placeholders
        (content_placeholder, code_blocks, anchor_placeholders, headers, url_placeholders,
         images, html_elements, inline_codes, tables, latex_formulas) = extract_placeholders(content)

        # Translate content
        translated_content = translate_content(content_placeholder, translator, source_lang_code, dest_lang)

        # Restore placeholders
        translated_content = restore_placeholders(
            translated_content, code_blocks, anchor_placeholders, headers, url_placeholders,
            images, html_elements, inline_codes, tables, latex_formulas,
            translator, source_lang_code, dest_lang
        )

        # Add or update language links with the current language highlighted (greyed out)
        translated_content = add_or_update_language_links(
            translated_content, translated_files, main_doc, prefix, current_lang_code=dest_lang
        )

        # Insert the translated content at the placeholder position
        insert_translated_content(translated_file, translated_content)

    # Check consistency of language links in the main readme file
    main_doc_path = os.path.join(output_dir, main_doc)
    try:
        with open(main_doc_path, 'r', encoding='utf-8') as file:
            main_doc_content = file.read()
    except Exception as e:
        logging.exception(f"Error reading '{main_doc_path}': {e}")
        sys.exit(1)

    # Verify that all expected links are present
    missing_links = [
        f"[{TARGET_LANGUAGES[code][1]} {TARGET_LANGUAGES[code][0]}]({translated_files[code]})"
        for code in TARGET_LANGUAGES
        if f"[{TARGET_LANGUAGES[code][1]} {TARGET_LANGUAGES[code][0]}]({translated_files[code]})" not in main_doc_content
    ]
    if missing_links:
        logging.warning(
            f"The main document '{main_doc}' is missing links to the following translated files: {', '.join(missing_links)}. "
            f"Please verify that the links correctly point to the translated files with prefix '{prefix}'."
        )

    logging.info("Translation process completed successfully.")

if __name__ == "__main__":
    main()

