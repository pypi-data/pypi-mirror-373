import httpx
from sagemaker import PartnerAppAuthProvider


class SigV4Auth(httpx.Auth):
    def __init__(self):
        self._auth_provider = PartnerAppAuthProvider()

    def auth_flow(self, request):
        url, signed_headers = self._auth_provider.get_signed_request(url=str(request.url),
                                                                     method=request.method,
                                                                     headers=request.headers,
                                                                     body=request.content)

        # Update the URL, since PartnerAppAuthProvider encodes spaces (e.g. ' ' or '+') as %20
        request.url = httpx.URL(url)

        # Update existing headers to include the signed headers:
        # Authorization: SigV4 signature
        # X-Amz-Partner-App-Authorization: Customer API key
        # X-Amz-Content-SHA256: Hash of request content
        # X-Amz-Target: IAM Action for App API requests, for authz purposes
        # X-Mlapp-Sm-App-Server-Arn: App Instance ARN
        request.headers.update(signed_headers)

        yield request
