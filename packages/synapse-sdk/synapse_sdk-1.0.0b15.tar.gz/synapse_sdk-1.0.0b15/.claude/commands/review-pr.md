---
name: review-pr
description: Comprehensive PR review using GitHub MCP with P1-P4 Code Review Rules
---

Please perform a comprehensive review of PR using the GitHub MCP server.

**Arguments:**
- First argument: PR number (required)
- Second argument: Language for review comments - "en" for English, "ko" for Korean (optional, defaults to "en")

**Usage Examples:**
- `/review-pr 123` - Review PR #123 with English comments
- `/review-pr 123 en` - Review PR #123 with English comments  
- `/review-pr 123 ko` - Review PR #123 with Korean comments

**Parse Arguments:**
Extract PR number from first argument and language preference from second argument (if provided). If second argument is not "ko", default to English ("en").

**IMPORTANT Review Decision Logic:**
1. **Track all P1, P2, P3 violations found during review**
2. **If ANY P1, P2, or P3 violations are found** → Use `--request-changes`
3. **If ONLY P4 violations or no violations found** → Use `--approve`
4. **Never use `--comment` as the main review action** - always choose between approve or request-changes

**Review Process:**
1. Read and load P1-P4 Code Review Rules from the following files:
   - P1_rules.md (Critical - Security and Stability)
   - P2_rules.md (High Priority - Core functionality and architecture)
   - P3_rules.md (Medium Priority - Best practices and maintainability)
   - P4_rules.md (Low Priority - Code style and formatting)
2. Fetch PR details and file changes
3. Apply P1-P4 Code Review Rules systematically against the changes
4. Analyze code quality, security, and performance
5. Check for test coverage and documentation
6. Look for potential bugs or issues
7. Provide specific, actionable feedback with priority levels
8. Create review comments directly on the PR for each issue found

**P1-P4 Code Review Rules Application:**

IMPORTANT: Before starting the review, read the complete rule sets from these files:
- `P1_rules.md`
- `P2_rules.md`
- `P3_rules.md`
- `P4_rules.md`

Apply ALL rules from these files during the review process. The rules cover:

**P1 Rules (Critical - MUST FIX):**
- Security and database integrity issues
- Critical Django/DRF patterns
- System stability concerns

**P2 Rules (High Priority):**
- Core Django/DRF best practices
- Architecture and design patterns
- Performance considerations

**P3 Rules (Medium Priority):**
- Code maintainability
- Best practices and conventions
- Safety and error handling

**P4 Rules (Low Priority - Style):**
- Code formatting and style
- Naming conventions
- Consistency standards

**Review Output Format:**
For each violation found:
1. **Report to user** with this format:
   - **Rule Category:** P1/P2/P3/P4
   - **Specific Rule:** Quote the exact rule from the files
   - **Location:** File and line number
   - **Issue:** What violates the rule
   - **Recommendation:** How to fix it based on the rule guidance
   - **Impact:** Why this matters (reference rule explanation)

2. **Create PR review comment** using GitHub CLI:
   - Use `gh pr review {PR_NUMBER} --comment-body "comment text"` for general review comments
   - Use `gh pr comment {PR_NUMBER} --body "comment text"` for specific line comments when applicable
   - Format comments with clear priority indicators: [P1], [P2], [P3], [P4]
   - Include rule reference and actionable guidance in each comment
   - **IMPORTANT:** Write all comments in the selected language (English or Korean)

**Review Actions:**
1. **Submit overall review** with summary using: `gh pr review {PR_NUMBER} --approve/--request-changes --body "overall review summary"`
2. **Add individual comments** for each rule violation found
3. **Use appropriate review status:**
   - `--request-changes` if any P1, P2, or P3 violations are found
   - `--approve` if only P4 violations or no issues found
   - `--comment` for informational feedback only (no rule violations)
4. **Language Requirements:**
   - Write ALL review comments and summary in the selected language
   - Use appropriate technical terminology for the chosen language
   - Maintain professional tone in both languages

**Focus Areas:**
- **Priority 1 (P1):** Critical security and stability issues (MUST FIX) → REQUEST CHANGES
- **Priority 2 (P2):** Core functionality and architecture (SHOULD FIX) → REQUEST CHANGES  
- **Priority 3 (P3):** Best practices and maintainability (SHOULD FIX) → REQUEST CHANGES
- **Priority 4 (P4):** Code style and formatting (OPTIONAL) → APPROVE WITH COMMENTS
- Test coverage and documentation completeness
- Breaking changes and backward compatibility

**GitHub CLI Commands to Use:**
- `gh pr view {PR_NUMBER} --json title,body,state,author,files,commits`
- `gh pr diff {PR_NUMBER}`
- `gh pr review {PR_NUMBER} --comment-body "review summary"`
- `gh pr comment {PR_NUMBER} --body "specific comment"`

**Language-Specific Comment Templates:**

**English Template:**
```
[P{LEVEL}] **{TITLE}**

{DESCRIPTION}

**Location:** {FILE}:{LINE}
**Issue:** {ISSUE_DESCRIPTION}
**Recommendation:** {RECOMMENDATION}
**Rule Reference:** {RULE_QUOTE}
```

**Korean Template:**
```
[P{LEVEL}] **{TITLE}**

{DESCRIPTION}

**위치:** {FILE}:{LINE}  
**문제점:** {ISSUE_DESCRIPTION}
**권장사항:** {RECOMMENDATION}
**규칙 참조:** {RULE_QUOTE}
```