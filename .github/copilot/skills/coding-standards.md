# Coding Standards

- Use type hints throughout the code.
- Use Pydantic for DTOs.
- Use SQLAlchemy ORM.
- Never access the database directly within routes.
- All business logic belongs in services.
- All database queries belong in repositories.
- Use dependency injection with FastAPI's `Depends`.
- Use English names.
- Functions must have a single responsibility.