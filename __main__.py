import json
import os
from dataclasses import dataclass
from anthropic import Anthropic
import subprocess
from typing import List
import tempfile
import shutil

ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
priority_filter = 2
project_path = "/Users/alex/Library/CloudStorage/GoogleDrive-alex@alexsalazar.com/My Drive/Projects/mythos"

@dataclass
class Suggestion:
    explanation: str
    priority: int
    reasoning: str
    suggested_changes: str

def assess_code(code: str, code_standard: str) -> List[Suggestion]:

    prompt = f"""
    Analyze the following code snippet and provide specific, actionable suggestions for improvement based on the given standard. 
    Code:
    ```
    {code}
    ```

   Standard:
    {code_standard}

    Provide your response as a JSON object with the following structure:
    {{
        "suggestions": [
            {{
                "explanation": "Brief explanation of the suggestion",
                "priority": 0-3 (0 being highest priority),
                "reasoning": "Detailed reasoning for the suggestion",
                "suggested_changes": "Provide specific code changes, including exact lines to modify or add. Use line numbers when applicable."
            }},
            ...
        ]
    }}

    Important: In the "suggested_changes" field, always provide concrete code snippets or exact textual changes, not general guidelines. Include line numbers or function names for context when suggesting modifications.
    
    Examples of good suggestions:
    1. {{
        "explanation": "Use f-strings for string formatting",
        "priority": 2,
        "reasoning": "F-strings are more readable and efficient than older string formatting methods.",
        "suggested_changes": "Line 15: Replace 'print('Hello, %s' % name)' with 'print(f'Hello, {{name}}')'"
    }}
    2. {{
        "explanation": "Add type hints to function parameters",
        "priority": 1,
        "reasoning": "Type hints improve code readability and help catch type-related errors early.",
        "suggested_changes": "In the 'process_data' function:\nChange 'def process_data(data):' to 'def process_data(data: List[Dict[str, Any]]) -> None:'"
    }}
    3. {{
        "explanation": "Use a context manager for file operations",
        "priority": 1,
        "reasoning": "Context managers ensure that files are properly closed after use, even if an exception occurs.",
        "suggested_changes": "Replace lines 23-25 with:
        ```python
        with open('output.txt', 'w') as f:
            f.write(processed_data)
        ```"
    }}

    Please provide similarly specific and actionable suggestions for the given code.
    """

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4000,
        temperature=0.2,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.content[0].text
    
    try:
        suggestions_dict = json.loads(content)
        suggestions = [
            Suggestion(**suggestion)
            for suggestion in suggestions_dict['suggestions']
        ]
        return suggestions
    except json.JSONDecodeError:
        return [Suggestion(
            explanation="Failed to parse JSON response",
            priority=0,
            reasoning="The AI response was not valid JSON",
            suggested_changes=content
        )]

def apply_suggestions_and_create_pr(file_path: str, suggestions: List[Suggestion], priority_filter: int=2) -> None:
    """
    Apply code suggestions and create a pull request.

    Args:
    file_path (str): Path to the file to be modified.
    suggestions (List[Suggestion]): List of Suggestion objects.

    Returns:
    None
    """
    # Read the original file content
    with open(file_path, 'r') as file:
        original_content = file.read()

    # Apply suggestions
    for suggestion in sorted(suggestions, key=lambda x: x.priority):
        if suggestion.priority <= priority_filter:
            modified_content = apply_suggestion(original_content, suggestion)
            break # only going to run this once for now
        else:
            break  # Since the list is sorted, we can break once we hit a higher priority

    # Create a temporary directory for the new worktree
    with tempfile.TemporaryDirectory() as temp_dir:
        branch_name = "kunth-code-improvements"
        
        # Create a new worktree
        subprocess.run(["git", "worktree", "add", "-B", branch_name, temp_dir, "origin/main"])
        
        # Copy the modified file to the new worktree
        temp_file_path = os.path.join(temp_dir, os.path.relpath(file_path, project_path))
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        shutil.copy2(file_path, temp_file_path)
        
        # Change to the temporary directory
        os.chdir(temp_dir)
        
        # Stage the changes
        subprocess.run(["git", "add", os.path.relpath(temp_file_path, temp_dir)])
        
        # Commit the changes
        commit_message = "Apply code improvements based on suggestions"
        subprocess.run(["git", "commit", "-m", commit_message])
        
        # Push the changes to the remote repository
        subprocess.run(["git", "push", "origin", branch_name])
        
        # Remove the worktree
        os.chdir(project_path)
        subprocess.run(["git", "worktree", "remove", temp_dir])

    print(f"Changes pushed to branch '{branch_name}'. Please create a pull request manually.")

def apply_suggestion(content: str, suggestion: Suggestion) -> str:
    """
    Apply a single suggestion to the content using Anthropic API.

    Args:
    content (str): The current content of the file.
    suggestion (Suggestion): A single Suggestion object.

    Returns:
    str: The modified content after applying the suggestion.
    """
    prompt = f"""
    Given the following file content and a suggestion for improvement, please provide an updated version of the file with the suggestion applied.

    Current file content:
    ```
    {content}
    ```

    Suggestion:
    Explanation: {suggestion.explanation}
    Reasoning: {suggestion.reasoning}
    Suggested Changes: {suggestion.suggested_changes}

    Please provide the entire updated file content, applying only this specific suggestion. Maintain the original structure and formatting of the file where possible, only making changes related to the given suggestion.
    
    Example:
    If the current content is:
    ```python
    def greet(name):
        print("Hello, %s" % name)

    greet("Alice")
    ```
    And the suggestion is:
    Explanation: Use f-strings for string formatting
    Reasoning: F-strings are more readable and efficient than older string formatting methods.
    Suggested Changes: Line 2: Replace 'print("Hello, %s" % name)' with 'print(f"Hello, {{name}}")'

    The response should be:
    ```python
    def greet(name):
        print(f"Hello, {{name}}")

    greet("Alice")
    ```

    Now, please apply the given suggestion to the provided file content.
    """
    print(f"This is the prompt to edit the file:\n{prompt}\n")
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4000,
        temperature=0.2,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    updated_content = response.content[0].text
    
    print(f"This is the updated file from the LLM:\n{updated_content}\n")
    # Extract the code block from the response
    start = updated_content.find("```")
    end = updated_content.rfind("```")
    if start != -1 and end != -1:
        # Move past the opening backticks and any language identifier
        code_start = updated_content.find("\n", start) + 1
        updated_content = updated_content[code_start:end].strip()

    return updated_content

# Example usage
if __name__ == "__main__":
    file_path = "code/mythos/story_llm.py"
    file_path = os.path.join(project_path, file_path)
    
    with open(file_path, "r") as file:
        code_snippet = file.read()
    
    # Update the standards_folder to be local to the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    standards_folder = os.path.join(current_dir, "standards", "python")
    all_suggestions = []

    for standard_file in os.listdir(standards_folder):
        if standard_file.endswith(".md"):
            standard_path = os.path.join(standards_folder, standard_file)
            with open(standard_path, "r") as f:
                code_standard = f.read()
            
            print(f"Assessing code against standard: {standard_file}")
            result = assess_code(code=code_snippet, code_standard=code_standard)
            all_suggestions.extend(result)

            for suggestion in result:
                print(f"Suggestion: {suggestion.explanation}")
                print(f"Priority: {suggestion.priority}")
                print(f"Reasoning: {suggestion.reasoning}")
                print(f"Suggested Changes: {suggestion.suggested_changes}")
                print("---")

    apply_suggestions_and_create_pr(file_path=file_path, suggestions=all_suggestions)