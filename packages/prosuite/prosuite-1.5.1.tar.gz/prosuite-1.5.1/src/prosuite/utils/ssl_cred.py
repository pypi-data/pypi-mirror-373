import ssl

import grpc


def get_ssl_channel_credentials() -> grpc.ChannelCredentials:
    """
    Creates an ssl channel credentials object for use with an SSL-enabled channel for the
    authentication with a server that requires TLS/SSL. The appropriate root certificates
    for server authentication are loaded from the windows certificate store.

    :return: A ChannelCredentials object
    """
    ctx = ssl.create_default_context()
    ca_certs = ctx.get_ca_certs(binary_form=True)
    ctx.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)

    root_certificates_pem = ''

    for cert in ca_certs:
        pem = ssl.DER_cert_to_PEM_cert(cert)
        root_certificates_pem += pem

    return grpc.ssl_channel_credentials(root_certificates=str.encode(root_certificates_pem, 'utf-8'))
