import json
import logging
import os
import typing as t
from copy import copy

import deepchecks_llm_client
import httpx
import packaging.version
import pandas
from deepchecks_llm_client.data_types import (
    AnnotationType,
    Application,
    ApplicationType,
    ApplicationVersion,
    ApplicationVersionSchema,
    BuiltInInteractionType,
    EnvType,
    InteractionCompleteEvents,
    InteractionUpdate,
    LogInteraction,
    PropertyColumnType,
)
from deepchecks_llm_client.exceptions import DeepchecksLLMClientVersionInNewerError
from deepchecks_llm_client.utils import maybe_raise
from httpx import URL, USE_CLIENT_DEFAULT, Response

__all__ = ["API"]

logger = logging.getLogger(__name__)

TAPI = t.TypeVar("TAPI", bound="API")  # pylint: disable=invalid-name
NULL_STRINGS = {"n/a", "na", "nan", "none"}


class CustomClient(httpx.Client):
    def request(
            self,
            method: str,
            url,
            *,
            content=None,
            data=None,
            files=None,
            json=None,  # pylint: disable=redefined-outer-name
            params=None,
            headers=None,
            cookies=None,
            auth=USE_CLIENT_DEFAULT,
            follow_redirects=USE_CLIENT_DEFAULT,
            timeout=USE_CLIENT_DEFAULT,
            extensions=None,
    ) -> Response:
        json = self._cleanup_json_before_request(json)
        return super().request(
            method,
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    @classmethod
    def _cleanup_json_before_request(cls, json_data: t.Union[dict, list, None]) -> t.Union[dict, list, None]:
        def _replace_invalid_value(value):
            try:
                if pandas.isnull(value):
                    return None
                if isinstance(value, str) and value.lower().strip() in NULL_STRINGS:
                    return None
            except (TypeError, ValueError):
                pass

            return value

        if json_data is None:
            return None

        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, dict):
                    json_data[key] = cls._cleanup_json_before_request(value)
                elif isinstance(value, list):
                    json_data[key] = [
                        cls._cleanup_json_before_request(el)
                        if isinstance(el, (dict, list))
                        else el
                        for el in value if _replace_invalid_value(el) is not None
                    ]
                else:
                    json_data[key] = _replace_invalid_value(value)

        elif isinstance(json_data, list):
            json_data = [
                cls._cleanup_json_before_request(el) if isinstance(el, (dict, list))
                else el
                for el in json_data if _replace_invalid_value(el) is not None
            ]

        return json_data


class API:
    """DeepchecksLLMClient API class."""

    session: httpx.Client
    original_host: URL

    @classmethod
    def instantiate(cls: t.Type[TAPI],
                    host: str,
                    token: t.Optional[str] = None,
                    validate_connection: bool = False) -> TAPI:
        headers = (
            {"Authorization": f"Basic {token}", "x-deepchecks-origin": "SDK"}
            if token
            else {"x-deepchecks-origin": "SDK"}
        )
        session = CustomClient(
            base_url=host,
            headers=headers,
            timeout=60,
            verify=os.getenv("VERIFY_SSL", "True").lower() == "true",
        )
        if os.getenv("AWS_PARTNER_APP_AUTH") is not None:
            from deepchecks_llm_client.hadron_auth import SigV4Auth  # pylint: disable=import-outside-toplevel
            session.auth = SigV4Auth()
        return cls(
            session=session,
            validate_connection=validate_connection
        )

    def __init__(self, session: httpx.Client, validate_connection: bool = False):
        self.session = copy(session)
        self.original_host = self.session.base_url
        self.session.base_url = self.session.base_url.join("/api/v1")

        try:
            backend_version = packaging.version.parse(self.retrieve_backend_version())
            client_version = packaging.version.parse(self.retrieve_client_version())
            self.session.headers.update({"x-sdk-version": str(client_version)})
        except packaging.version.InvalidVersion as ex:
            raise RuntimeError("Not able to compare backend and client versions, "
                               "backend or client use incorrect or legacy versioning schema.") from ex
        except httpx.ConnectError as ex:
            logger.exception(f"Could not connect to backend {self.original_host}, either the server is down or "
                             f"you are using an incorrect host name")
            if validate_connection:
                raise ex

        else:
            self._verify_version_compatability(backend_version, client_version)

    def _verify_version_compatability(self, backend_version, client_version):
        if client_version.major > backend_version.major \
                or (client_version.major == backend_version.major and client_version.minor > backend_version.minor):
            raise DeepchecksLLMClientVersionInNewerError(
                f"SDK version {client_version} is newer and is not compatible with the backend version {backend_version}, "
                f"please downgrade the SDK by using {self.get_pip_install_msg(backend_version)}"
            )
        if backend_version.major != client_version.major:
            logger.error(
                f"SDK version {client_version} is not compatible with backend version {backend_version}, "
                f"please upgrade SDK to the compatible version using {self.get_pip_install_msg(backend_version)}"
            )
        else:
            versions_diff = backend_version.minor - client_version.minor
            if 0 < versions_diff <= 3:
                logger.warning(
                    f"SDK version is {client_version}, while server version is {backend_version}, client version {client_version} "
                    f"will be deprecated in {4 - versions_diff} releases from now, "
                    f"please update you SDK version to the compatible version using {self.get_pip_install_msg(backend_version)}"
                )
            elif versions_diff > 3:
                logger.error(
                    f"SDK version {client_version} is deprecated (backend version is {backend_version}), please upgrade SDK "
                    f"to the compatible version using {self.get_pip_install_msg(backend_version)}"
                )

    @classmethod
    def get_pip_install_msg(cls, backend_version) -> str:
        return f"pip install -U 'deepchecks-llm-client>={backend_version.major}." \
               f"{backend_version.minor},<{backend_version.major}.{backend_version.minor + 1}'"

    def retrieve_backend_version(self) -> str:
        payload = maybe_raise(self.session.get("backend-version")).json()
        return payload["version"]

    def retrieve_client_version(self) -> str:
        return deepchecks_llm_client.__version__

    def get_application(self, app_name: str) -> t.Dict[str, t.Any]:
        payload = maybe_raise(self.session.get("applications", params={"name": [app_name]})).json()
        return payload[0] if len(payload) > 0 else None

    def get_applications(self) -> t.List[Application]:
        applications = maybe_raise(self.session.get("applications", params={"include_extended_data": True})).json()
        return [
            Application(
                id=app["id"],
                name=app["name"],
                kind=app["kind"],
                created_at=app["created_at"],
                updated_at=app["updated_at"],
                in_progress=app["additional_data"]["in_progress"],
                description=app["description"],
                log_latest_insert_time_epoch=app["additional_data"]["log_latest_insert_time_epoch"],
                n_of_llm_properties=app["additional_data"]["n_of_llm_properties"],
                n_of_interactions=app["additional_data"]["n_of_interactions"],
                notifications_enabled=app["additional_data"]["notifications_enabled"],
                interaction_types=[interaction_type["name"] for interaction_type in app["interaction_types"]],
                versions=[
                    ApplicationVersion(
                        id=app_version["id"],
                        name=app_version["name"],
                        ai_model=app_version["ai_model"],
                        created_at=app_version["created_at"],
                        updated_at=app_version["updated_at"],
                        description=app_version["description"],
                        additional_fields=app_version["additional_fields"],
                    ) for app_version in app["versions"]
                ],
            ) for app in applications
        ]

    def get_versions(self, app_name: t.Optional[str] = None) -> t.List[ApplicationVersion]:
        versions = maybe_raise(self.session.get("application-versions", params={"app_name": [app_name] if app_name else []})).json()
        return [
            ApplicationVersion(
                id=app_version["id"],
                name=app_version["name"],
                ai_model=app_version["ai_model"],
                created_at=app_version["created_at"],
                updated_at=app_version["updated_at"],
                description=app_version["description"],
                additional_fields=app_version["additional_fields"],
            ) for app_version in versions
        ]

    def create_application_version(
            self,
            application_id: int,
            version_name: str,
            description: t.Optional[str] = None,
            additional_fields: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        return maybe_raise(
            self.session.post(
                "application-versions",
                json={
                    "application_id": application_id,
                    "name": version_name,
                    "additional_fields": additional_fields,
                    "description": description,
                },
            )
        ).json()

    def create_application(
            self,
            app_name: str,
            app_type: ApplicationType,
            versions: t.Optional[t.List[ApplicationVersionSchema]] = None,
            description: t.Optional[str] = None,
    ):
        return maybe_raise(
            self.session.post(
                "applications",
                json={
                    "name": app_name,
                    "kind": app_type,
                    "versions": [version.to_json() for version in versions] if versions else [],
                    "description": description,
                },
            )
        ).json()

    def annotate(self,
                 user_interaction_id: str,
                 version_id: int,
                 annotation: t.Union[AnnotationType, str] = None,
                 reason: t.Optional[str] = None) \
            -> t.Optional[httpx.Response]:
        # pylint: disable=redefined-builtin
        return maybe_raise(
            self.session.put(
                "annotations",
                json={
                    "user_interaction_id": user_interaction_id,
                    "application_version_id": version_id,
                    "value": (
                        None if annotation is None else
                        annotation.value if isinstance(annotation, AnnotationType)
                        else str(annotation).lower().strip()
                    ),
                    "reason": reason
                }
            )
        )

    def update_interaction(
            self,
            app_version_id: int,
            user_interaction_id: str,
            interaction_update: InteractionUpdate
    ) -> t.Optional[httpx.Response]:
        # pylint: disable=redefined-builtin
        return maybe_raise(
            self.session.put(
                f"application-versions/{app_version_id}/interactions/{user_interaction_id}",
                json=interaction_update.to_json()
            )
        )

    def delete_interactions(self, user_interaction_ids: t.List[str], app_version_id: int):
        return maybe_raise(
            self.session.request(
                method="DELETE",
                url=f"application-versions/{app_version_id}/interactions",
                json={"user_interaction_ids": user_interaction_ids},
            )
        )

    def log_batch(
            self,
            app_name: str,
            version_name: str,
            env_type: t.Union[EnvType, str],
            interactions: t.List[LogInteraction],
            ignore_duplicates: bool = False,
    ):
        return maybe_raise(
            self.session.post(
                "interactions",
                json={
                    "app_name": app_name,
                    "version_name": version_name,
                    "env_type": env_type.value if isinstance(env_type, EnvType) else env_type.upper(),
                    "interactions": [interaction.to_json() for interaction in interactions],
                    "ignore_duplicates": ignore_duplicates,
                },
            ),
            expected=201,
        )

    def log_interaction(
            self,
            app_name: str,
            version_name: str,
            env_type: t.Union[EnvType, str],
            interaction: LogInteraction,
    ) -> t.Optional[httpx.Response]:
        """The log_interaction method is used to log user interactions.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Version name
        env_type : EnvType
            Environment
        interaction : LogInteraction
            Interaction object containing the interaction data
        Returns
        -------
        httpx.Response
            The HTTP response from logging the user interaction

        """
        # pylint: disable=redefined-builtin

        return maybe_raise(
            self.session.post(
                "interactions",
                json={"env_type": env_type.value if isinstance(env_type, EnvType) else env_type.upper(),
                      "app_name": app_name,
                      "version_name": version_name,
                      "interactions": [interaction.to_json()]}
            ),
            expected=201
        )

    def get_interactions(self, application_version_id: int,
                         limit: int, offset: int,
                         env_type: t.Union[EnvType, str],
                         start_time_epoch: t.Union[int, None],
                         end_time_epoch: t.Union[int, None],
                         user_interaction_ids: t.Union[t.List[str], None] = None,
                         include_incomplete: bool = False,
                         session_ids: t.Union[t.List[str], None] = None,
                         interaction_type: t.Union[str, None] = None,
                         ) -> t.List:
        return maybe_raise(
            self.session.post(
                f"application-versions/{application_version_id}/get-interactions-by-filter",
                json={
                    "filter_schema": {
                        "environment": env_type.value if isinstance(env_type, EnvType) else env_type,
                        "start_time_epoch": start_time_epoch,
                        "end_time_epoch": end_time_epoch,
                        "user_interaction_ids": user_interaction_ids,
                        "session_ids": session_ids,
                        "interaction_type": interaction_type,
                    },
                    "pagination_schema": {
                        "limit": limit,
                        "offset": offset,
                    }
                },
                params={"return_topics": True, "include_incomplete": include_incomplete}
            )
        ).json()

    def get_interactions_csv(
            self,
            application_version_id: int,
            return_topics: bool,
            return_annotation_data: bool,
            return_builtin_props: bool,
            return_user_value_properties: bool,
            return_custom_prompt: bool,
            return_similarities: bool,
            env_type: t.Union[EnvType, str],
            start_time_epoch: t.Union[int, None],
            end_time_epoch: t.Union[int, None],
            user_interaction_ids: t.Union[t.List[str], None] = None,
            include_incomplete: bool = False,
            return_steps: bool = True,
            session_ids: t.Union[t.List[str], None] = None,
            interaction_type: t.Union[str, None] = None,
            return_session_related: bool = False,
            return_only_input_output_texts: bool = False,
    ) -> str:
        return maybe_raise(
            self.session.post(
                f"application-versions/{application_version_id}/interactions-download-all-by-filter",
                json={
                    "environment": env_type.value if isinstance(env_type, EnvType) else env_type,
                    "start_time_epoch": start_time_epoch,
                    "end_time_epoch": end_time_epoch,
                    "user_interaction_ids": user_interaction_ids,
                    "session_ids": session_ids,
                    "interaction_type": interaction_type,
                },
                params={"return_topics": return_topics,
                        "return_builtin_props": return_builtin_props,
                        "return_user_value_properties": return_user_value_properties,
                        "return_custom_prompt": return_custom_prompt,
                        "return_annotation_data": return_annotation_data,
                        "return_similarities_data": return_similarities,
                        "include_incomplete": include_incomplete,
                        "return_steps": return_steps,
                        "return_session_related": return_session_related,
                        "return_only_input_output_texts": return_only_input_output_texts,
                        }
            )
        ).text

    def get_interaction_by_user_interaction_id(self, version_id: int, user_interaction_id: str):
        return maybe_raise(self.session.get(
            f"application-versions/{version_id}/interactions/{user_interaction_id}"
        )).json()

    def update_interaction_type_config(self, application_id: int, interaction_type: str, file):
        if isinstance(file, str):
            with open(file, "rb") as f:
                data = {"file": ("filename", f)}
        else:
            data = {"file": ("filename", file)}
        maybe_raise(self.session.put(f"applications/{application_id}/interaction-type-config",
                                     params={"interaction_type": interaction_type}, files=data))

    def get_interaction_type_config(self, application_id: int, interaction_type: str,
                                    file_save_path: t.Union[str, None] = None) -> str:
        text = maybe_raise(self.session.get(f"applications/{application_id}/interaction-type-config",
                                            params={"interaction_type": interaction_type})).text
        if file_save_path:
            with open(file_save_path, "w", encoding="utf-8") as f:
                f.write(text)
        return text

    def get_pentest_prompts(
            self,
            app_id: int,
            probes: t.Optional[t.List[str]] = None,
    ) -> str:
        if probes:
            return maybe_raise(self.session.get("pentest-prompts", params={"probes": probes, "app_id": app_id})).text
        return maybe_raise(self.session.get("pentest-prompts", params={"app_id": app_id})).text

    def get_user_value_properties_definitions(self, application_id: int, interaction_type: t.Optional[str] = None) -> t.List[dict]:
        return maybe_raise(
            self.session.get(
                f"applications/{application_id}/properties-definitions",
                params={"property_types": ["custom"], "interaction_type": interaction_type}
            )
        ).json()

    def create_user_value_property_definition(
            self,
            application_id: int,
            name: str,
            prop_type: t.Union[PropertyColumnType, str],
            description: str = "",
            interaction_type: t.Optional[str] = None,
    ) -> None:
        return maybe_raise(
            self.session.post(
                f"applications/{application_id}/custom-prop-definitions",
                json=[
                    {
                        "display_name": name,
                        "type": prop_type.value if isinstance(prop_type, PropertyColumnType) else prop_type,
                        "description": description,
                        "interaction_type": interaction_type,
                    }]
            )
        )

    def get_interactions_complete_status(
            self,
            app_version_id: int,
            events_to_check: t.List[InteractionCompleteEvents],
            user_interaction_ids: t.List[str],
    ) -> t.Dict[InteractionCompleteEvents, bool]:
        return maybe_raise(
            self.session.post(
                f"application-versions/{app_version_id}/interactions/complete-status",
                json={"events_to_check": events_to_check, "user_interaction_ids": user_interaction_ids}
            )
        ).json()

    def update_application_version(
            self,
            app_version_id: int,
            name: t.Optional[str] = None,
            description: t.Optional[str] = None,
            additional_fields: t.Optional[dict] = None,
    ):
        return maybe_raise(
            self.session.put(
                "application-versions",
                json={
                    "app_version_id": app_version_id,
                    "name": name,
                    "description": description,
                    "additional_fields": additional_fields,
                }
            )
        )

    def create_interaction_type(
            self,
            app_id: int,
            name: str,
            template_name: t.Optional[BuiltInInteractionType] = None
    ):
        return maybe_raise(
            self.session.post(
                f"applications/{app_id}/interaction-types",
                json={
                    "name": name,
                    "type": template_name,
                }
            )
        ).json()

    def get_interaction_types(self, app_id: int):
        return maybe_raise(
            self.session.get(
                f"applications/{app_id}/interaction-types",
            )
        ).json()

    def update_interaction_type(
            self,
            interaction_type_id: int,
            name: str,
    ):
        return maybe_raise(
            self.session.put(
                f"/interaction-types/{interaction_type_id}",
                json={"name": name}
            )
        )

    def delete_interaction_type(self, interaction_type_id: int):
        return maybe_raise(
            self.session.delete(
                f"/interaction-types/{interaction_type_id}",
            )
        )

    def create_interaction_type_version_data(
            self,
            interaction_type_id: int,
            application_version_id: int,
            model: t.Optional[str] = None,
            prompt: t.Optional[str] = None,
            metadata_params: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        """Create interaction type version data.

        Parameters
        ----------
        interaction_type_id : int
            Interaction type id
        application_version_id : int
            Application version id
        model : str, optional
            Model name
        prompt : str, optional
            Prompt template
        metadata_params : dict, optional
            Additional metadata parameters

        Returns
        -------
        dict
            Created interaction type version data
        """
        return maybe_raise(
            self.session.post(
                "interaction-types-version-data",
                json={
                    "interaction_type_id": interaction_type_id,
                    "application_version_id": application_version_id,
                    "model": model,
                    "prompt": prompt,
                    "metadata_params": metadata_params or {},
                },
            )
        ).json()

    def get_interaction_types_version_data(
        self,
        application_version_id: int,
    ):
        """Search interaction type version data.

        Parameters
        ----------
        application_version_id : int
            Application version id

        Returns
        -------
        list
            List of interaction type version data
        """
        return maybe_raise(
            self.session.get(
                "interaction-types-version-data",
                params={"application_version_id": application_version_id},
            )
        ).json()

    def update_interaction_type_version_data(
            self,
            interaction_type_data_id: int,
            model: t.Optional[str] = None,
            prompt: t.Optional[str] = None,
            metadata_params: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        """Update interaction type version data.

        Parameters
        ----------
        interaction_type_data_id : int
            Interaction type version data id
        model : str, optional
            Model name
        prompt : str, optional
            Prompt template
        metadata_params : dict, optional
            Additional metadata parameters

        Returns
        -------
        dict
            Updated interaction type version data
        """
        return maybe_raise(
            self.session.put(
                f"interaction-types-version-data/{interaction_type_data_id}",
                json={
                    "model": model,
                    "prompt": prompt,
                    "metadata_params": metadata_params,
                },
            )
        ).json()

    def delete_interaction_type_version_data(self, interaction_type_data_id: int):
        """Delete interaction type version data.

        Parameters
        ----------
        interaction_type_data_id : int
            Interaction type version data id
        """
        return maybe_raise(
            self.session.delete(
                f"interaction-types-version-data/{interaction_type_data_id}",
            )
        )

    def send_spans(
            self,
            app_name: str,
            version_name: str,
            env_type: t.Union[EnvType, str],
            spans: list,
    ) -> t.Optional[httpx.Response]:
        """Send OpenTelemetry spans to the Deepchecks LLM backend.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of application version
        env_type : EnvType or str
            Environment type, can be an instance of EnvType or a string
        spans : List[ReadableSpan]
            List of OpenTelemetry spans to send

        Returns
        -------
        httpx.Response
            The HTTP response from sending the spans
        """
        return maybe_raise(
            self.session.post(
                "span-interactions",
                json={
                    "app_name": app_name,
                    "version_name": version_name,
                    "env_type": env_type.value if isinstance(env_type, EnvType) else env_type.upper(),
                    "spans": [span if isinstance(span, dict) else json.loads(span.to_json()) for span in spans],
                },
            ),
            expected=(200, 201),
        )
