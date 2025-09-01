# Update PR Title Command

You will help the user update a PR title with various options.

## Available Options

- `--pr <number>`: Specify PR number (optional - uses current branch if not provided)
- `--lang <language>`: Title language (korean/english, default: korean)

## Examples

- `/update-pr-title --pr 123 --lang ko`: Update PR #123 with Korean title
- `/update-pr-title --lang eng`: Update current branch PR with English title
- `/update-pr-title`: Update current branch PR with Korean title (default)

## Implementation

1. If PR number not provided, find PR for current branch
2. Analyze commit messages and changes to understand the scope
3. Generate a concise, descriptive title in specified language
4. Keep any existing ticket ID (e.g., SYN-XXXX) at the beginning
5. Update the PR title

## Title Guidelines

- Keep titles concise but descriptive (under 72 characters when possible)
- Include the ticket ID if present
- Summarize the main feature/fix/change
- Use appropriate language (Korean/English)
- Follow conventional commit style when applicable

Please provide the PR number and desired language, or use defaults for current branch and Korean
