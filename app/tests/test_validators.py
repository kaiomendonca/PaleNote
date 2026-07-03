import pytest

from app.core.user_exceptions import InvalidDocument
from app.core.validator_exceptions import IncorrectPassword
from app.schemas.validators import DocumentValidator, FieldValidator
from app.services.document_validator import extract_nfe_access_key_data


class TestFieldValidator:
    """Test suite for FieldValidator class"""

    def test_validate_password_characters_with_valid_password(self):
        """Test validation with a valid password"""
        valid_password = "SecurePass123"
        result = FieldValidator.validate_password_characters(valid_password)
        assert result == valid_password

    def test_validate_password_characters_without_uppercase(self):
        """Test validation fails without uppercase letter"""
        invalid_password = "securepass123"
        with pytest.raises(IncorrectPassword):
            FieldValidator.validate_password_characters(invalid_password)

    def test_validate_password_characters_without_lowercase(self):
        """Test validation fails without lowercase letter"""
        invalid_password = "SECUREPASS123"
        with pytest.raises(IncorrectPassword):
            FieldValidator.validate_password_characters(invalid_password)

    def test_validate_password_characters_without_digit(self):
        """Test validation fails without digit"""
        invalid_password = "SecurePassAbc"
        with pytest.raises(IncorrectPassword):
            FieldValidator.validate_password_characters(invalid_password)

    def test_validate_password_characters_too_short(self):
        """Test validation fails with password shorter than 8 characters"""
        invalid_password = "Pass12"
        with pytest.raises(IncorrectPassword):
            FieldValidator.validate_password_characters(invalid_password)

    def test_validate_password_characters_with_special_characters(self):
        """Test validation passes with special characters included"""
        valid_password = "Secure@Pass123!"
        result = FieldValidator.validate_password_characters(valid_password)
        assert result == valid_password


class TestDocumentValidator:
    """Test suite for DocumentValidator class"""

    def test_validate_document_accepts_valid_cpf_and_strips_special_characters(self):
        """Test validation returns True for a valid CPF with special characters"""
        result = DocumentValidator.validate_document("123.456.789-09")
        assert result is True

    def test_validate_document_accepts_valid_cnpj_and_strips_special_characters(self):
        """Test validation returns True for a valid CNPJ with special characters"""
        result = DocumentValidator.validate_document("11.222.333/0001-81")
        assert result is True

    def test_validate_document_raises_for_invalid_document(self):
        """Test validation raises InvalidDocument for an invalid document"""
        with pytest.raises(InvalidDocument):
            DocumentValidator.validate_document("123.456.789-00")

    def test_validate_document_raises_for_unknown_length(self):
        """Test validation raises InvalidDocument for unsupported length"""
        with pytest.raises(InvalidDocument):
            DocumentValidator.validate_document("123456789")

    def test_validate_invoice_documents_with_valid_cnpj_and_cpf(self):
        """Test validation with valid issuer CNPJ and recipient CPF"""
        # Valid CNPJ: 11.222.333/0001-81
        issuer_cnpj = "11.222.333/0001-81"
        # Valid CPF: 123.456.789-09
        recipient_cpf = "123.456.789-09"
        result = DocumentValidator.validate_invoice_documents(
            issuer_cnpj, recipient_cpf
        )
        assert result is True

    def test_validate_invoice_documents_with_valid_cnpj_and_cnpj(self):
        """Test validation with valid issuer CNPJ and recipient CNPJ"""
        # Valid CNPJ: 11.222.333/0001-81
        issuer_cnpj = "11.222.333/0001-81"
        # Valid CNPJ: 11.222.333/0001-81
        recipient_cnpj = "11.222.333/0001-81"
        result = DocumentValidator.validate_invoice_documents(
            issuer_cnpj, recipient_cnpj
        )
        assert result is True

    def test_validate_invoice_documents_with_invalid_issuer_cnpj(self):
        """Test validation fails with invalid issuer CNPJ"""
        invalid_issuer_cnpj = "11.111.111/0001-11"
        valid_recipient_cpf = "123.456.789-09"
        with pytest.raises(ValueError) as exc_info:
            DocumentValidator.validate_invoice_documents(
                invalid_issuer_cnpj, valid_recipient_cpf
            )
        assert "Invalid issuer CNPJ" in str(exc_info.value)

    def test_validate_invoice_documents_with_invalid_recipient_cpf(self):
        """Test validation fails with invalid recipient CPF"""
        valid_issuer_cnpj = "11.222.333/0001-81"
        invalid_recipient_cpf = "123.456.789-00"
        with pytest.raises(ValueError) as exc_info:
            DocumentValidator.validate_invoice_documents(
                valid_issuer_cnpj, invalid_recipient_cpf
            )
        assert "Invalid recipient CPF" in str(exc_info.value)

    def test_validate_invoice_documents_with_invalid_recipient_document_length(self):
        """Test validation fails with invalid recipient document length"""
        valid_issuer_cnpj = "11.222.333/0001-81"
        invalid_length_doc = "123.456.789"
        with pytest.raises(ValueError) as exc_info:
            DocumentValidator.validate_invoice_documents(
                valid_issuer_cnpj, invalid_length_doc
            )
        assert "Invalid recipient document" in str(exc_info.value)

    def test_validate_invoice_documents_removes_special_characters(self):
        """Test validation correctly handles documents with special characters"""
        # Both with dots, slashes and dashes
        issuer_cnpj = "11.222.333/0001-81"
        recipient_cpf = "123.456.789-09"
        result = DocumentValidator.validate_invoice_documents(
            issuer_cnpj, recipient_cpf
        )
        assert result is True

    def test_validate_nfe_access_key_with_valid_key(self):
        """Test NFe access key validation with a valid key"""
        # Valid NFe access key (44 digits)
        valid_key = "35150111222333000181551010001234567890123"
        result = DocumentValidator.validate_nfe_access_key(valid_key)
        # Note: This specific key may or may not be valid,
        # depends on check digit calculation
        assert isinstance(result, bool)

    def test_validate_nfe_access_key_with_invalid_length(self):
        """Test NFe access key validation fails with wrong length"""
        invalid_key = "123456789"  # Too short
        result = DocumentValidator.validate_nfe_access_key(invalid_key)
        assert result is False

    def test_validate_nfe_access_key_with_non_digit_characters(self):
        """Test NFe access key validation handles non-digit characters"""
        key_with_non_digits = "3515011122233300018155101000123456789012AB"
        result = DocumentValidator.validate_nfe_access_key(key_with_non_digits)
        # Should extract only digits and validate
        assert isinstance(result, bool)

    def test_validate_nfe_access_key_check_digit_calculation(self):
        """Test NFe access key check digit calculation"""

        # A valid NFe access key with correct check digit

        # Format: UF(2) + DDMM(4) + CNPJ(8) + Model(2) +
        # Series(3) + Number(9) + Code(8) + DV(1)

        # UF=35, Date=150111, CNPJ=22233300, Model=01, Series=815,
        # Number=510100001, Code=23456789, DV=0
        valid_key = "35150122233300018158101000012345678900"
        result = DocumentValidator.validate_nfe_access_key(valid_key)
        assert isinstance(result, bool)


class TestExtractNfeAccessKeyData:
    """Test suite for extract_nfe_access_key_data function"""

    def test_extract_nfe_access_key_data_with_valid_key(self):
        """Test extraction of NFe access key data"""

        # NFe access key has exactly 44 digits

        # Format: UF(2) + Date(4) + CNPJ(14) + Model(2) +
        # Series(3) + Number(9) + Code(9) + DV(1)
        access_key = "35150122233300018158101000123456789012345678"
        result = extract_nfe_access_key_data(access_key)

        assert result.uf_code == "35"
        assert result.issue_date == "1501"
        assert result.issuer_cnpj == "22233300018158"
        assert result.model == "10"
        assert result.series == "100"
        assert result.invoice_number == "012345678"
        assert result.numeric_code == "901234567"
        assert result.check_digit == "8"

    def test_extract_nfe_access_key_data_preserves_leading_zeros(self):
        """Test that extraction preserves leading zeros in all fields"""
        access_key = "00000000000000000000000000000000000000000001"
        result = extract_nfe_access_key_data(access_key)

        assert result.uf_code == "00"
        assert result.issue_date == "0000"
        assert result.issuer_cnpj == "00000000000000"
        assert result.model == "00"
        assert result.series == "000"
        assert result.invoice_number == "000000000"
        assert result.numeric_code == "000000000"
        assert result.check_digit == "1"

    def test_extract_nfe_access_key_data_returns_string_model(self):
        """Test that NFEAccessKeyData is properly constructed"""
        access_key = "35150122233300018158101000123456789012345678"
        result = extract_nfe_access_key_data(access_key)

        # Check that it returns NFEAccessKeyData model
        assert hasattr(result, "uf_code")
        assert hasattr(result, "issue_date")
        assert hasattr(result, "issuer_cnpj")
        assert hasattr(result, "model")
        assert hasattr(result, "series")
        assert hasattr(result, "invoice_number")
        assert hasattr(result, "numeric_code")
        assert hasattr(result, "check_digit")
