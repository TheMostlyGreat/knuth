# Code Improvement Tool

**Note: This is an early, experimental version of the tool. The code is currently in a very preliminary state and may be unstable or incomplete.**

This tool analyzes Python code, suggests improvements based on a given standard, and can automatically apply these suggestions to create a pull request.

## Features

- Analyzes Python code against a specified coding standard
- Generates improvement suggestions with explanations and priorities
- Applies suggestions automatically to the code
- Creates a new Git branch and pushes changes
- Prepares for pull request creation

## Requirements

- Python 3.7+
- Anthropic API key
- Git

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install required packages:
   ```
   pip install anthropic
   ```

3. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

1. Modify the `project_path` variable in the script to point to your project directory.

2. Run the script:
   ```
   python __main__.py
   ```

3. The script will analyze the code in `story_llm.py`, apply suggestions, and create a new branch with the changes.

4. Create a pull request manually using the information provided in the console output.

## Configuration

- `ANTHROPIC_MODEL`: The Anthropic model to use for code analysis (default: "claude-3-5-sonnet-20240620")
- `priority_filter`: The maximum priority level of suggestions to apply (default: 2)

## Functions

- `assess_code(code: str, code_standard: str) -> List[Suggestion]`: Analyzes the code and returns a list of suggestions.
- `apply_suggestions_and_create_pr(file_path: str, suggestions: List[Suggestion], priority_filter: int=2) -> None`: Applies suggestions and creates a pull request.
- `apply_suggestion(content: str, suggestion: Suggestion) -> str`: Applies a single suggestion to the code content.

## Customization

To add new types of suggestions or modify the behavior of existing ones, edit the `apply_suggestion` function in the script.

## Note

This tool uses the Anthropic API to analyze code. Ensure you have sufficient API credits and comply with Anthropic's usage terms.