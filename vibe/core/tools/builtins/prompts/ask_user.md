Use the `ask_user` tool to ask the user clarifying questions during execution.

## When to Use This Tool

Use this tool when you need to:
1. **Clarify any doubts or uncertainties** - When your understanding is incomplete or ambiguous.
2. **Confirm critical details** - Before making significant decisions or changes.
3. **Choose between approaches** - Multiple valid solutions exist.
4. **Validate assumptions** - To ensure alignment with user expectations.
5. **Get preferences** - User input needed on implementation details or style.

## When NOT to Use This Tool

Skip this tool when:
- You can find the answer by reading code or files
- The task is straightforward with an obvious approach
- You're just confirming something trivial

## Best Practices

- Ask ONE clear question at a time
- Provide 2-4 options when applicable
- Keep questions concise and actionable
- Prefer investigating with other tools first

## Examples

**Example 1: Clarifying approach**
```json
{
  "question": "Should I use async/await or callbacks for this API?",
  "options": ["async/await", "callbacks", "let me decide based on existing code"]
}
```

**Example 2: Requirements clarification**
```json
{
  "question": "The function can return null or throw an exception on error. Which do you prefer?",
  "options": ["return null", "throw exception"]
}
```

**Example 3: Open question**
```json
{
  "question": "What should be the default timeout value in seconds?"
}
```

**Example 4: Plan Validation**
```json
{
  "question": "I have created a plan to refactor the database layer. It involves 5 steps including schema migration. Do you want to proceed?",
  "options": ["Yes, proceed", "No, let's review the plan", "Abort"]
}
```
