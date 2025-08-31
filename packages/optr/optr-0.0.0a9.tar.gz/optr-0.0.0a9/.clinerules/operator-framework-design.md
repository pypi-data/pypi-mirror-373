## Brief overview
Guidelines for developing a functional-first operator automation framework that provides toolkit utilities for GUI tasks and robotic workflows, emphasizing simplicity and composability over complex inheritance hierarchies.

## Architectural philosophy
- Design as a toolkit (like lodash/jquery) rather than a prescriptive framework (like React)
- Provide composable utilities that users can combine flexibly
- Focus on simplifying operator creation rather than enforcing specific patterns
- Enable users to build automation workflows with minimal boilerplate

## Functional programming approach
- Prefer pure functions over stateful classes when appropriate
- Use function composition to build complex behaviors from simple parts
- Minimize side effects and make them explicit when necessary
- Design APIs that work well with functional programming patterns

## Inheritance avoidance
- Favor composition over inheritance for extending functionality
- Use mixins, traits, or functional composition instead of deep class hierarchies
- Design interfaces that can be implemented through simple function signatures
- Prefer dependency injection over inheritance for customization points

## Operator automation focus
- Design APIs specifically for GUI task automation and robotic workflows
- Provide clear abstractions for common automation patterns (scanning, acting, validating)
- Support both desktop GUI automation and robotic control use cases
- Enable seamless integration between different automation domains

## Code organization
- Structure modules around capabilities rather than object hierarchies
- Group related functions and utilities together logically
- Keep interfaces minimal and focused on specific automation tasks
- Design for easy discoverability of available utilities and functions
