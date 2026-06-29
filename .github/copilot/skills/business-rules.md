# Business Rules

## NF-e

- Every received XML must have a valid access key.
- Duplicate XMLs must not be processed again.
- The XML hash (access key) must be unique.
- If validation fails, the status must be FAILED.
- All processing must be auditable.

## DANFE

- The PDF may only be generated after successful validation.
- PDFs may be stored in the database or in external storage.

## Reprocessing

- Invoices with FAILED status may be reprocessed (the error that caused the failure must be exposed).