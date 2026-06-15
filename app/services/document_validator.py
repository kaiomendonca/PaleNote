from validate_docbr import CNPJ, CPF

cpf = CPF()
cnpj = CNPJ()


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
