# trn: CLI tool for translating text using LLMs

## Features

- Multiple input sources: command line arguments, stdin, clipboard, URLs, or files
- OpenAI, Anthropic, and Gemini models
- Configurable via command line arguments or environment variables

## Installation

With [uv](https://docs.astral.sh/uv/) installed, you may skip the installation: `uvx trn`
will always run the latest version of command. You can also install it the usual way:

```bash
uv tool install trn
# or
pip install trn
```

## Usage

First, [set the key](https://llm.datasette.io/en/stable/help.html#llm-keys-help) for your LLM
provider. Example for Google Gemini:

    uvx --with llm-gemini llm keys set gemini

Second, specify your target language via the `TRN_TO_LANGUAGE` environment variable or `-t` argument.
The `-t` argument takes priority when both are set.

Third, provide text to translate in one of these ways:

- command line arguments
- standard input
- clipboard

The tool checks for arguments first, then standard input, then the clipboard.

You can also translate web pages or local PDF/image files by providing a URL or file path.

### Basic Usage

```bash
# Translate from clipboard to default language
trn

# Translate command line text into French
trn -t french Hello world

# Translate from stdin
echo "Hello world" | trn

# Translate a file
trn document.pdf

# Translate from URL
trn https://example.com/article

# Use custom LLM
trn -m gpt-4o-mini
```

### Configuration

Set environment variables for convenience:

    export TRN_TO_LANGUAGE=spanish
    # optionally:
    export TRN_MODEL=gpt-4o-mini

### Options

```
> trn --help
usage: trn [-h] -t TO_LANGUAGE [-m MODEL] [-p PROMPT] [-a PROMPT_ADD] [-v] [-d]
           [text ...]

positional arguments:
  text                  Text to translate, or URL, or path to file (default:
                        None)

options:
  -h, --help            show this help message and exit
  -t, --to-language TO_LANGUAGE
                        Target language for translation [env var:
                        TRN_TO_LANGUAGE] (default: None)
  -m, --model MODEL     LLM to use (run 'uvx llm models' for available models)
                        [env var: TRN_MODEL] (default: gemini-2.5-flash)
  -p, --prompt PROMPT   Custom prompt for translation [env var: TRN_PROMPT]
                        (default: Translate the text (it can be in any language)
                        into {to_language}. Don't explaint that the output is a
                        translation. Tell me in case if you don't know about
                        '{to_language}' language. If there is a file attached,
                        translate the contents of the file. {prompt_add})
  -a, --prompt-add PROMPT_ADD
                        Custom prompt for translation [env var: TRN_PROMPT_ADD]
                        (default: )
  -v, --verbose         Enable verbose output [env var: TRN_VERBOSE] (default:
                        False)
  -d, --debug           Enable debug output [env var: TRN_DEBUG] (default:
                        False)

 In general, command-line values override environment variables which override
defaults.
```

## Requirements

- Python 3.12+
- LLM API key configured
- UV installed (optional, but highly recommended)
