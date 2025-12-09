# Adversarial LLM PoC

A command-line interface (CLI) tool that uses the Gemini API with leetspeak encoding to create a unique conversational experience. 

## Overview

adversarial-llm-poc implements a leetspeak transformation layer between the user and the Gemini API. It converts user queries into leetspeak before sending them to the API and then decodes the responses back into normal text. 

This project is based on the research published by HiddenLayer on the ["Policy Puppetry" prompt injection technique](https://hiddenlayer.com/innovation-hub/novel-universal-bypass-for-all-major-llms/), which demonstrated how certain prompt structures could bypass AI models' safety guardrails. This implementation uses a combination of XML-based policy format and leetspeak encoding as described in the research.

This tool is designed for educational purposes to explore creative interaction patterns with language models and to better understand how prompt formatting affects AI responses.

## Features

- Conversion of text to and from Basic Leet (vowel-to-number substitution)
- Integration with Google's Gemini API
- Engaging CLI interface with Rich text formatting
- Debug mode for viewing the behind-the-scenes processing
- Rate limiting to respect API constraints

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Setup

1. Clone the repository:

```bash
git clone https://github.com/Iskandeur/adversarial-llm-poc.git
cd adversarial-llm-poc
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

You can obtain an API key from the [Google AI Studio](https://aistudio.google.com).

## Usage

Run the main script to start the interactive CLI:

```bash
python main.py
```

### Basic Commands

- Type any question or statement to get a response
- Use `exit`, `quit`, or `bye` to exit the application
- Use `debug on` and `debug off` to toggle debug mode

### Examples

```
adversarial-llm-poc> What is machine learning?
```

The application will convert your query to leetspeak, send it to the Gemini API, and then decode and display the response.

### Debug Mode

Debug mode provides detailed information about the processing steps:
- Original and leetspeak versions of your query
- The prompt sent to the Gemini API
- The raw response received
- Extraction and decoding details

Enable it with:

```
adversarial-llm-poc> debug on
```

Disable it with:

```
adversarial-llm-poc> debug off
```

## Configuration

The `config.json` file contains various settings:

- Gemini API configuration (model, base URL, rate limits)
- CLI settings (prompt, welcome message, commands)
- Debug mode toggle

## Project Structure

```
adversarial-llm-poc/
├── main.py             # Main CLI application
├── translator.py       # Leetspeak translation utilities
├── api_client.py       # Gemini API interface
├── config.json         # Configuration settings
├── prompt_template.xml # Prompt template for Gemini
├── translation_table.json # Basic Leet character mappings
├── env.example         # Example environment variables
├── .env                # Your API key (not committed to git)
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
├── screenshots/        # Screenshots for documentation
└── README.md           # This file
```

## Technical Details

### Leetspeak Translation

adversarial-llm-poc uses Basic Leet encoding which primarily focuses on vowel substitutions:

- A → 4
- E → 3
- I → 1
- O → 0
- T → 7
- Spaces → underscores

### Response Processing

The application implements a multi-strategy approach to extract and process responses:
1. Extract dialogue segments from script-formatted responses
2. Identify and extract bullet-pointed content
3. Parse code blocks and other structured content
4. Clean and normalize the extracted text
5. Decode leetspeak characters back to normal text

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

**IMPORTANT**: This tool is created for educational purposes only. It should be used responsibly and ethically.

The author(s) of this tool:
- Are NOT responsible for any misuse or consequences resulting from the use of this tool
- Are NOT liable if your API account gets banned or suspended due to usage of this tool
- Do NOT endorse using this tool to bypass AI safety measures for harmful purposes
- Provide NO warranty or guarantee regarding the tool's functionality or effects

By using this tool, you assume full responsibility for your actions and any consequences that may result from them. Use at your own risk.

This tool implements techniques described in academic research to explore the boundaries of AI systems. It is not intended to facilitate harmful content generation or to compromise AI safety measures for malicious purposes.

## Acknowledgments

- [HiddenLayer Research](https://hiddenlayer.com/innovation-hub/novel-universal-bypass-for-all-major-llms/) for the Policy Puppetry technique research
- [Google Gemini](https://ai.google.dev/) for providing the API
- [Rich](https://github.com/Textualize/rich) for beautiful terminal formatting
- [Python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management 
