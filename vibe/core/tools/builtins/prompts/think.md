Use the `think` tool to delegate complex reasoning to a more capable model.

## When to Use This Tool

Use this tool when you need to:
1. **Architectural decisions** - Designing system structure, choosing patterns
2. **Complex analysis** - Multi-step reasoning, trade-off evaluation
3. **Planning** - Breaking down large tasks into steps
4. **Code review** - Deep analysis of complex code

## When NOT to Use This Tool

Skip this tool when:
- The task is simple (file operations, small edits)
- You can solve it with existing knowledge
- Speed is more important than depth

## Arguments

- `task` (required): Description of what you need help reasoning about
- `context` (optional): Code snippets, requirements, or additional information

## Examples

**Example 1: Architectural decision**
```json
{
  "task": "Design the authentication system for a microservices architecture",
  "context": "We have 5 services: users, orders, payments, inventory, notifications. Need SSO."
}
```

**Example 2: Code analysis**
```json
{
  "task": "Analyze this function for potential performance issues and suggest optimizations",
  "context": "def process(items):\n    result = []\n    for item in items:\n        if validate(item):\n            result.append(transform(item))\n    return result"
}
```

**Example 3: Planning**
```json
{
  "task": "Create a migration plan from REST to GraphQL",
  "context": "Current API has 50 endpoints, 10k daily active users, no breaking changes allowed"
}
```

## Configuration

In `~/.vibe/config.toml`:
```toml
[tools.think]
model = "devstral-2"  # Model to use for deep thinking
timeout = 120.0       # Timeout in seconds
max_tokens = 32768     # Maximum response tokens
```
