import json

from qwak.clients.administration.eco_system.client import EcosystemClient
from qwak.exceptions import QwakException, QwakHTTPException
from qwak.vector_store.rest_helpers import RestSession


class VectorStoreInferenceClient:
    def __init__(
        self,
        model_id: str,
    ):
        """
        :param model_id: The model id to invoke against.
        """

        self.r_session = RestSession()
        self.ecosystem_client = EcosystemClient()

        authenticated_user_context = (
            self.ecosystem_client.get_authenticated_user_context()
        )
        account_details = authenticated_user_context.user.account_details
        default_environment_id = account_details.default_environment_id
        model_url_prefix = account_details.environment_by_id[
            default_environment_id
        ].configuration.model_api_url

        self.model_id = model_id
        self.content_type = "application/json; format=pandas-split"
        self.model_api = _get_model_url(
            model_id=model_id, model_url_prefix=model_url_prefix
        )

    def predict(
        self,
        feature_vectors,
    ):
        """
        Perform a prediction request against a Qwak based model

        :param feature_vectors: A list of feature vectors to predict against. Each feature vector is modeled as a python
         dictionary
        :return: Prediction response from the model
        """

        if feature_vectors.__class__.__name__ == "DataFrame":
            feature_vectors = feature_vectors.to_json(orient="split")

        if isinstance(feature_vectors, dict) or isinstance(feature_vectors, list):
            feature_vectors = json.dumps(feature_vectors)

        try:
            response = self.r_session.post(
                self.model_api, data=feature_vectors, headers={}
            )

            if response.status_code >= 400:
                exception_class_name = response.headers.get("X-Exception-Class")
                msg = f"{response.status_code}: {response.text}"
                raise QwakHTTPException(response.status_code, msg, exception_class_name)

            elif response.status_code != 200:
                raise QwakHTTPException(response.status_code, response.content)

            dict_response = json.loads(response.content)
            return dict_response
        except QwakHTTPException as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Failed to make a prediction request. Error is: {e}")

    def get_embedding(self, natural_input: str):
        feature_vector = [
            {
                "input": natural_input,
            }
        ]
        try:
            result_list = self.predict(feature_vector)
        except Exception as e:
            raise QwakException(
                f"Vectorizer {self.model_id} failed to transform input {feature_vector} to vectors. Error is: {str(e)}"
            )
        try:
            vector = result_list[0]["embeddings"]
        except Exception:
            raise QwakException(
                f"Vectorizer {self.model_id} must return a dataframe containing an 'embeddings' column"
            )
        if not vector:
            raise QwakException(
                f"Vectorizer {self.model_id} did not return embeddings for the given natural input. Unable to continue with the query."
            )
        return vector


def _get_model_url(model_id: str, model_url_prefix: str) -> str:
    scheme = "http" if model_url_prefix.startswith("localhost") else "https"
    effective_model_id = model_id.replace("-", "_")
    return (
        f"{scheme}://{model_url_prefix}/v1/{effective_model_id}/predict"  # noqa: E231
    )
