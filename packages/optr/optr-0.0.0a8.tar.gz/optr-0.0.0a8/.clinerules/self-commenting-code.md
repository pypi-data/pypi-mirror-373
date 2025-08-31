## Brief overview
Guidelines for writing clean, self-documenting code that eliminates unnecessary comments by using clear naming conventions and readable code structure.

## Code commenting philosophy
- Write self-explanatory code that doesn't require comments to understand
- Use descriptive variable and function names that reveal intent
- Avoid redundant comments that simply restate what the code does
- Only add comments for complex business logic or non-obvious implementation decisions

## Naming conventions
- Choose names that clearly express purpose and intent within their context
- Infer meaning from file/module context - avoid redundant prefixes (e.g., `create` not `create_action` in `action.py`)
- Use full words rather than abbreviations when clarity benefits
- Make function names verb-based to indicate actions
- Use noun-based names for variables and classes
- Users can rename imports using `import as` if context-specific names conflict

## Code structure
- Write small, focused functions that do one thing well
- Use early returns to reduce nesting and improve readability
- Group related functionality together logically
- Extract complex expressions into well-named variables
- Structure code flow to read naturally from top to bottom

## Self-documenting practices
- Use meaningful constants instead of magic numbers
- Choose clear conditional expressions over complex boolean logic
- Break down complex operations into smaller, named steps
- Use type hints and annotations where supported by the language
- Organize imports and dependencies clearly at the top of files
