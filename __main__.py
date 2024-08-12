import json
import os
from dataclasses import dataclass
from anthropic import Anthropic
import subprocess
from typing import List, Dict

ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
priority_filter = 2
project_path = "/Users/alex/Library/CloudStorage/GoogleDrive-alex@alexsalazar.com/My Drive/Projects/kunth/test-project"

@dataclass
class Suggestion:
    explanation: str
    priority: int
    reasoning: str
    suggested_changes: str

def assess_code(code: str, code_standard: str) -> List[Suggestion]:

    prompt = f"""
    Analyze the following code snippet and provide suggestions for improvement based on the given standard. 
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
                "suggested_changes": "Specific code changes or guidelines"
            }},
            ...
        ]
    }}
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
        content = file.read()

    # Apply suggestions
    for suggestion in sorted(suggestions, key=lambda x: x.priority):
        if suggestion.priority <= priority_filter:
            # Apply suggestions with priority equal to or lower than priority_filter
            content = apply_suggestion(content, suggestion)
        else:
            # Skip suggestions with higher priority numbers
            break  # Since the list is sorted, we can break once we hit a higher priority

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

    # Change to the project directory before running Git commands
    os.chdir(project_path)

    # Create a new branch
    branch_name = "code-improvements"
    subprocess.run(["git", "checkout", "-b", branch_name])
    
    # Use relative path for git add
    relative_file_path = os.path.relpath(file_path, project_path)
    subprocess.run(["git", "add", relative_file_path])

    # Commit the changes
    commit_message = "Apply code improvements based on suggestions"
    subprocess.run(["git", "commit", "-m", commit_message])

    # Push the changes to the remote repository
    subprocess.run(["git", "push", "origin", branch_name])

    # Create a pull request (this step might require using a Git hosting platform's API)
    print(f"Changes pushed to branch '{branch_name}'. Please create a pull request manually.")

def apply_suggestion(content: str, suggestion: Suggestion) -> str:
    """
    Apply a single suggestion to the content.

    Args:
    content (str): The current content of the file.
    suggestion (Suggestion): A single Suggestion object.

    Returns:
    str: The modified content after applying the suggestion.
    """
    # This is a placeholder function. You would need to implement the logic
    # for each type of suggestion here. For example:
    if suggestion.explanation == "Use consistent line spacing between functions":
        # Logic to add two blank lines between function definitions
        pass
    elif suggestion.explanation == "Improve import organization":
        # Logic to reorder imports
        pass
    # ... implement other suggestion types ...

    return content

# Example usage
if __name__ == "__main__":

    file_path = "story_llm.py"

    file_path = os.path.join(project_path, file_path)
    
    with open(file_path, "r") as file:
        code_snippet = file.read()
    
    code_standard = "PEP 8"
    result = assess_code(code=code_snippet, code_standard=code_standard)
    for suggestion in result:
        print(f"Suggestion: {suggestion.explanation}")
        print(f"Priority: {suggestion.priority}")
        print(f"Reasoning: {suggestion.reasoning}")
        print(f"Suggested Changes: {suggestion.suggested_changes}")
        print("---")

    apply_suggestions_and_create_pr(file_path=file_path, suggestions=result)



# Example usage:
# file_path = "path/to/your/file.py"
# suggestions = [...]  # Your list of suggestions
# apply_suggestions_and_create_pr(file_path, suggestions)