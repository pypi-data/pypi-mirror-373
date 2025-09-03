from typing import BinaryIO

import requests
import requests_pkcs12


def get_session_with_mtls(
    cert: str | None = None,
    pvk: str | None = None,
    cert_pfx: str | bytes | BinaryIO | None = None,
    pwd_pfx: str | None = None,
    sandbox_mode: bool = False,
) -> requests.Session:
    session = requests.Session()

    if not sandbox_mode:
        if cert_pfx and pwd_pfx:
            # Configura autenticação com PFX
            pkcs12_adapter = requests_pkcs12.Pkcs12Adapter(
                pkcs12_data=cert_pfx if isinstance(cert_pfx, bytes) else None,
                pkcs12_filename=cert_pfx if isinstance(cert_pfx, str) else None,
                pkcs12_password=pwd_pfx,
            )
            session.mount('https://', pkcs12_adapter)
        elif cert and pvk:
            # Configura autenticação com PEM (manter compatibilidade)
            session.cert = (cert, pvk)
        else:
            raise ValueError(
                'É necessário fornecer certificado e chave privada (PEM) '
                'ou certificado PFX e senha'
            )

    return session
