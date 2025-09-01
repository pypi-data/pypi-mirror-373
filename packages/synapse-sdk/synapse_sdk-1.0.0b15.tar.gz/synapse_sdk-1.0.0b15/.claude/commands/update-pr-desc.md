# Update PR Description Command

You will help the user update a PR description with various options.

## Available Options:
- `--pr <number>`: Specify PR number (optional - uses current branch if not provided)
- `--lang <language>`: Description language (korean/english, default: korean)

## Examples:
- `/update-pr-desc --pr 123 --lang ko`: Update PR #123 with Korean description
- `/update-pr-desc --lang eng`: Update current branch PR with English description
- `/update-pr-desc`: Update current branch PR with Korean description (default)

## Implementation:
1. If PR number not provided, find PR for current branch
2. Generate commit diff analysis
3. Create appropriate PR description in specified language
4. Update the PR description

Please provide the PR number and desired language, or use defaults for current branch and Korean