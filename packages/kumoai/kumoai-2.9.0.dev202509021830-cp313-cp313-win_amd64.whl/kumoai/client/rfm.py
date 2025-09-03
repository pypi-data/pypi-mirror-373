from kumoapi.json_serde import to_json_dict
from kumoapi.rfm import (
    RFMEvaluateResponse,
    RFMPredictResponse,
    RFMValidateQueryRequest,
    RFMValidateQueryResponse,
)

from kumoai.client import KumoClient
from kumoai.client.endpoints import RFMEndpoints
from kumoai.client.utils import parse_response, raise_on_error


class RFMAPI:
    r"""Typed API definition for Kumo RFM (Relational Foundation Model)."""
    def __init__(self, client: KumoClient) -> None:
        self._client = client

    def predict(self, request: bytes) -> RFMPredictResponse:
        """Make predictions using the RFM model.

        Args:
            request: The predict request as serialized protobuf.

        Returns:
            RFMPredictResponse containing the predictions
        """
        # Send binary data to the predict endpoint
        response = self._client._request(
            RFMEndpoints.predict, data=request,
            headers={'Content-Type': 'application/x-protobuf'})
        raise_on_error(response)
        return parse_response(RFMPredictResponse, response)

    def explain(self, request: bytes) -> RFMPredictResponse:
        """Explain the RFM model on the given context.

        Args:
            request: The predict request as serialized protobuf.

        Returns:
            RFMPredictResponse containing the explanations
        """
        # Send binary data to the explain endpoint
        response = self._client._request(
            RFMEndpoints.explain, data=request,
            headers={'Content-Type': 'application/x-protobuf'})
        raise_on_error(response)
        return parse_response(RFMPredictResponse, response)

    def evaluate(self, request: bytes) -> RFMEvaluateResponse:
        """Evaluate the RFM model on the given context.

        Args:
            request: The evaluate request as serialized protobuf.

        Returns:
            RFMEvaluateResponse containing the computed metrics
        """
        # Send binary data to the evaluate endpoint
        response = self._client._request(
            RFMEndpoints.evaluate, data=request,
            headers={'Content-Type': 'application/x-protobuf'})
        raise_on_error(response)
        return parse_response(RFMEvaluateResponse, response)

    def validate_query(
        self,
        request: RFMValidateQueryRequest,
    ) -> RFMValidateQueryResponse:
        """Validate a predictive query against a graph.

        Args:
            request: The request object containing
                the query and graph definition

        Returns:
            RFMValidateQueryResponse containing the QueryDefinition
        """
        response = self._client._request(RFMEndpoints.validate_query,
                                         json=to_json_dict(request))
        raise_on_error(response)
        return parse_response(RFMValidateQueryResponse, response)
