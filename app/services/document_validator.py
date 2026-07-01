from app.schemas.invoice import NFEAccessKeyData


def extract_nfe_access_key_data(access_key: str) -> NFEAccessKeyData:
    return NFEAccessKeyData(
        uf_code=access_key[:2],
        issue_date=access_key[2:6],
        issuer_cnpj=access_key[6:20],
        model=access_key[20:22],
        series=access_key[22:25],
        invoice_number=access_key[25:34],
        numeric_code=access_key[34:43],
        check_digit=access_key[43],
    )
