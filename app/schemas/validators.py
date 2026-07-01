import re

from validate_docbr import CNPJ, CPF

from app.core.validator_exceptions import IncorrectPassword

cpf = CPF()
cnpj = CNPJ()


class FieldValidator:
    @staticmethod
    def validate_password_characters(value: str) -> str:
        if (
            len(value) < 8
            or not re.search(r"[A-Z]", value)
            or not re.search(r"[a-z]", value)
            or not re.search(r"\d", value)
        ):
            raise IncorrectPassword()

        return value


class DocumentValidator:
    @staticmethod
    def validate_invoice_documents(issuer_cnpj: str, recipient_document: str) -> bool:
        errors = []

        clean_issuer_cnpj = "".join(char for char in issuer_cnpj if char.isdigit())
        clean_recipient_document = "".join(
            char for char in recipient_document if char.isdigit()
        )

        if not cnpj.validate(clean_issuer_cnpj):
            errors.append("Invalid issuer CNPJ")

        if len(clean_recipient_document) == 11:
            if not cpf.validate(clean_recipient_document):
                errors.append("Invalid recipient CPF")
        elif len(clean_recipient_document) == 14:
            if not cnpj.validate(clean_recipient_document):
                errors.append("Invalid recipient CNPJ")
        else:
            errors.append("Invalid recipient document length")

        if errors:
            raise ValueError("Invalid documents: " + " | ".join(errors))

        return True

    @staticmethod
    def validate_nfe_access_key(access_key: str) -> bool:
        if len(access_key) != 44:
            return False

        clean_key = "".join(char for char in access_key if char.isdigit())
        body = clean_key[:43]
        provided_dv = int(clean_key[43])

        weight = 2
        total = 0

        for digit in reversed(body):
            total += int(digit) * weight

            weight += 1

            if weight > 9:
                weight = 2

        remainder = total % 11

        calculated_dv = 0 if remainder in (0, 1) else 11 - remainder

        return calculated_dv == provided_dv
