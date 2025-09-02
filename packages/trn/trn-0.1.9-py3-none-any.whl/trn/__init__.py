import logging
import re
import select
import sys
import textwrap
from pathlib import Path
from typing import Optional

import configargparse
import curl_cffi
import llm
import pyperclip
from html2text import html2text

translate_prompt = "Translate the text (it can be in any language) into {to_language}. Don't explain that the output is a translation. Tell me if you don't recognize '{to_language}' language. If there is a file attached, translate the contents of the file. {prompt_add}"


def translate(
    text: Optional[str] = None,
    file: Optional[str] = None,
    *,
    model: str,
    to_language: str,
    system_prompt: str,
    prompt_add: str,
    width: int = 80,
):
    system_prompt = translate_prompt.format(to_language=to_language.capitalize(), prompt_add=prompt_add)
    attachments = [llm.Attachment(path=file)] if file else []
    logging.debug(f"{text=}, {attachments=}, {model=}, {to_language=}, {system_prompt=}")
    response = llm.get_model(model).prompt(text, attachments=attachments, system=system_prompt)
    if width > 0:
        print_wrapped(response, width=width)
    else:
        print("".join(list(response)))


# the wrapping logic is Claude-generated, beware!
def print_wrapped(generator, width=80):
    buffer = ""
    for chunk in generator:
        buffer += chunk

        # Handle newlines - they reset the line length
        while "\n" in buffer:
            newline_pos = buffer.find("\n")
            line = buffer[:newline_pos]

            # Wrap this line if it's too long
            while len(line) > width:
                wrap_at = line.rfind(" ", 0, width + 1)
                if wrap_at == -1:
                    wrap_at = width
                print(line[:wrap_at])
                line = line[wrap_at:].lstrip()

            if line:
                print(line)
            else:
                print()  # Empty line

            buffer = buffer[newline_pos + 1 :]

        # Handle remaining buffer (no newlines)
        while len(buffer) > width:
            wrap_at = buffer.rfind(" ", 0, width + 1)
            if wrap_at == -1:
                wrap_at = width
            print(buffer[:wrap_at])
            buffer = buffer[wrap_at:].lstrip()

    # Print any remaining buffer
    if buffer.strip():
        print(buffer.strip())


def is_url(text: str) -> bool:
    return re.match(r"^https?://", text) is not None


def is_file(text: str) -> bool:
    return Path(text).exists()


def has_stdin_data() -> bool:
    return bool(select.select([sys.stdin], [], [], 0)[0])


def readability(url: str) -> str:
    return html2text(curl_cffi.get(url, impersonate="chrome").text)


def get_input_data(args) -> tuple[Optional[str], Optional[str]]:
    text = None
    file = None

    if args.text:
        text = " ".join(args.text)
    elif has_stdin_data():
        logging.warning("Using text from standard input.")
        text = sys.stdin.read()
    else:
        logging.warning("Using text from clipboard.")
        text = pyperclip.paste()

    text = text.strip()

    if not text:
        logging.error("Error: empty text! Please give me some text via stdin, command line arguments or in a clipboard.")
        sys.exit(1)

    if args.text and text:
        if is_url(text):
            logging.warning(f"Translating web page {text}")
            text = readability(text)
        elif is_file(text):
            logging.warning(f"Translating file {text}")
            file = text
            text = None

    return text, file


def main():
    parser = configargparse.ArgumentParser(formatter_class=lambda prog: configargparse.ArgumentDefaultsHelpFormatter(prog, width=80))
    parser.add_argument("-t", "--to-language", env_var="TRN_TO_LANGUAGE", required=True, help="Target language for translation")
    parser.add_argument(
        "-m", "--model", env_var="TRN_MODEL", help="LLM to use (run 'uvx llm models' for available models)", default="gemini-2.5-flash"
    )
    parser.add_argument("-p", "--prompt", env_var="TRN_PROMPT", help="Custom prompt for translation", default=translate_prompt)
    parser.add_argument("-a", "--prompt-add", env_var="TRN_PROMPT_ADD", help="Text to append to the prompt", default="")
    parser.add_argument("-w", "--wrap", env_var="TRN_WRAP", type=int, default=80, help="Wrap output at N chars (use 0 to disable wrapping)")
    parser.add_argument("-v", "--verbose", env_var="TRN_VERBOSE", action="store_true", help="Enable verbose output")
    parser.add_argument("-d", "--debug", env_var="TRN_DEBUG", action="store_true", help="Enable debug output")
    parser.add_argument("text", nargs="*", help="Text to translate, or URL, or path to file")
    args = parser.parse_args()

    log_level = logging.ERROR
    if args.verbose:
        log_level = logging.WARNING
    if args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format="%(message)s")

    if not sys.stdout.isatty():
        args.wrap = 0

    logging.debug(f"Started with {args=}")

    text, file = get_input_data(args)
    translate(
        text=text,
        file=file,
        model=args.model,
        to_language=args.to_language,
        system_prompt=args.prompt,
        prompt_add=args.prompt_add,
        width=args.wrap,
    )


if __name__ == "__main__":
    main()
