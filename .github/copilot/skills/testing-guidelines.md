# Testing Guidelines

## General principles

- Use pytest for automated tests.
- Follow the AAA pattern: Arrange, Act, Assert.
- Keep tests focused on behavior, not implementation details.
- Prefer small, deterministic tests.

## Project-specific guidance

- For FastAPI routes, test the public HTTP behavior and expected status codes.
- For services, test business rules and error handling in isolation.
- For repositories and database access, use an isolated test database or transactional fixtures.
- For document validation logic, cover valid and invalid CPF/CNPJ and NF-e access key cases.
- For async code, use pytest-asyncio patterns or async test helpers when needed.

## Mocking and dependencies

- Mock external integrations such as Redis, Celery workers, and third-party validators when the goal is unit isolation.
- Avoid over-mocking; mock only boundaries that are external or non-deterministic.
- For integration-style tests, use real database and HTTP layer where practical.

## Naming and structure

- Name tests by behavior, for example: test_upload_returns_201_for_valid_invoice.
- Group related tests by module or feature.
- Keep fixtures reusable and scoped appropriately.

## Quality expectations

- Tests should be fast and reliable.
- Prefer clear failure messages over broad assertions.
- When changing behavior, add or update tests alongside the implementation.