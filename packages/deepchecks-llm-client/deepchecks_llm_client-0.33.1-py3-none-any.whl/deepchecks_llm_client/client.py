"""Module containing all the client functionality for the Deepchecks LLM Client."""
import io
import logging
import os
import time
import typing as t
from datetime import datetime

import pandas as pd
from deepchecks_llm_client.api import API
from deepchecks_llm_client.data_types import (
    AnnotationType,
    ApplicationType,
    ApplicationVersionSchema,
    BuiltInInteractionType,
    EnvType,
    Interaction,
    InteractionCompleteEvents,
    InteractionType,
    InteractionTypeVersionData,
    InteractionUpdate,
    LogInteraction,
    PropertyColumnType,
    Step,
    UserValueProperty,
    UserValuePropertyType,
)
from deepchecks_llm_client.exceptions import DeepchecksLLMClientError
from deepchecks_llm_client.utils import HandleExceptions, HandleGeneratorExceptions, get_timestamp

logging.basicConfig()
logger = logging.getLogger(__name__)
init_logger = logging.Logger(__name__ + ".init")

DEFAULT_ENV_TYPE = EnvType.PROD
DEFAULT_DC_HOST = "https://app.llm.deepchecks.com"


class DeepchecksLLMClient:
    """DeepchecksLLMClient is the class through which you can interact with the Deepchecks LLM API."""

    def __init__(self,
                 host: str = None,
                 api_token: str = None,
                 log_level: int = logging.WARNING,
                 silent_mode: bool = False):
        """Init Deepchecks LLM Client. Connect to the server and perform a simple handshake with the API.

        Parameters
        ==========
        host : str
            The URL of the Deepchecks server to communicate with. By default,
            it's set to the Deepchecks LLM host (https://app.llm.deepchecks.com),
            but you can override it by providing a custom URL.
            If not provided, the value is read from the environment variable DEEPCHECKS_LLM_HOST.
        api_token : str
            Deepchecks API Token (can be generated from the UI).
            If not provided, the value is read from the environment variable DEEPCHECKS_LLM_API_TOKEN.
        silent_mode: bool, default=False
            If True, the SDK will print logs upon encountering errors rather than raising them
        log_level: int, default=logging.WARNING
            Set SDK loggers logging level

        Returns
        =======
        None
        """
        self._api: API = None
        self._host = host or os.environ.get("DEEPCHECKS_LLM_HOST", None) \
            or os.environ.get("AWS_PARTNER_APP_URL", DEFAULT_DC_HOST)  # AWS Hadron env var
        self._api_token = api_token or os.environ.get("DEEPCHECKS_LLM_API_TOKEN")

        logger.setLevel(log_level)
        self._log_level = log_level
        self.silent_mode = silent_mode

        self._init_api()

    @HandleExceptions(init_logger)
    def _init_api(self):
        if self._api is None:
            if self._host is not None and self._api_token is not None:
                self._api = API.instantiate(host=self._host, token=self._api_token)
            else:
                raise DeepchecksLLMClientError("host/token parameters must be provided")

    @property
    def api(self) -> API:
        """Get the API object for the client."""
        if self._api:
            return self._api
        raise DeepchecksLLMClientError("deepchecks llm client was not initialized correctly, please re-create it")

    @HandleExceptions(logger)
    def create_application(
            self,
            app_name: str,
            app_type: ApplicationType,
            versions: t.Optional[t.List[ApplicationVersionSchema]] = None,
            description: t.Optional[str] = None,
    ):
        """Create a new application.

        Parameters
        ----------
        app_name
            Application name
        app_type
            The Default Interaction Type for interactions of this application
        versions
            List of versions to create for the application
        description
            Description of the application

        Returns
        -------
            The response from the API
        """
        self.api.create_application(app_name=app_name, app_type=app_type, versions=versions, description=description)
        return self.api.get_application(app_name=app_name)

    @HandleExceptions(logger)
    def create_app_version(
            self,
            app_name: str,
            version_name: str,
            description: t.Optional[str] = None,
            additional_fields: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        """Create a new application version.

        Parameters
        ----------
        app_name
            Application name
        version_name
            Version name
        description
            Description of the version
        additional_fields
            Additional fields to add to the version
        Returns
        -------
            The response from the API
        """
        app_id = self._get_application_id(app_name)
        return self.api.create_application_version(
            application_id=app_id,
            version_name=version_name,
            description=description,
            additional_fields=additional_fields
        )

    @HandleExceptions(logger)
    def update_application_version(
        self,
        app_version_id: int,
        name: t.Optional[str] = None,
        description: t.Optional[str] = None,
        additional_fields: t.Optional[dict] = None,
    ):
        """Create a new application.

        Parameters
        ----------
        app_version_id
            Application version id to udate
        name
            New version name
        description
            New description of the version
        additional_fields
            Additional fields to add to the version
        Returns
        -------
            The response from the API
        """
        self.api.update_application_version(
            app_version_id=app_version_id,
            name=name,
            description=description,
            additional_fields=additional_fields,
        )

    @HandleExceptions(logger)
    def get_applications(self):
        """Get all applications as Application objects.

        Note that "custom" attribute in ApplicationVersion is deprecated. Please use `additional_fields` instead.

        Returns
        -------
        List[Application]
            List of applications
        """
        return self.api.get_applications()

    @HandleExceptions(logger)
    def get_versions(self, app_name: t.Optional[str] = None):
        """Get all versions of an application as Version objects.

        Note that "custom" attribute in ApplicationVersion is deprecated. Please use `additional_fields` instead.

        Parameters
        ----------
        app_name
            Name of the application to get versions for

        Returns
        -------
        List[ApplicationVersion]
            List of versions
        """
        return self.api.get_versions(app_name=app_name)

    @HandleExceptions(logger)
    def annotate(self, app_name: str, version_name: str, user_interaction_id: str,
                 annotation: t.Union[AnnotationType, str] = None, reason: t.Optional[str] = None):
        """Annotate a specific interaction by its user_interaction_id.

        Parameters
        ----------
        app_name
            Application name
        version_name
            Name of the version to which this interaction belongs
        user_interaction_id
            The user_interaction_id of the interaction to annotate
        annotation
            Could be one of AnnotationType.GOOD, AnnotationType.BAD, AnnotationType.UNKNOWN
            or None to remove annotation
        reason
            String that explains the reason for the annotation

        Returns
        -------
            None
        """
        version_id = self._get_version_id(version_name=version_name, app_name=app_name)
        self.api.annotate(user_interaction_id, version_id, annotation, reason=reason)

    # pylint: disable=redefined-builtin
    @HandleExceptions(logger)
    def log_interaction(
        self,
        app_name: str,
        version_name: str,
        env_type: t.Union[EnvType, str],
        interaction: LogInteraction,
    ) -> str:
        """Log a single interaction.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of the version to which this interaction will be added
        env_type : EnvType or str
            Type of environment. Allowed values: 'eval', 'prod', 'pentest'
        interaction : LogInteraction
            The interaction data to log.
        Returns
        -------
        str
            The uuid of the interaction
        """
        # pylint: disable=redefined-builtin
        result = self.api.log_interaction(
            app_name=app_name,
            version_name=version_name,
            env_type=env_type,
            interaction=interaction,
        )
        return result.json()[0]

    @HandleExceptions(logger)
    def log_batch_interactions(
            self,
            app_name: str,
            version_name: str,
            env_type: t.Union[EnvType, str],
            interactions: t.List[LogInteraction],
            ignore_duplicates: bool = False,
    ) -> t.List[str]:
        """Log multiple interactions at once.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of the version to which this interaction will be added
        env_type : EnvType or str
            Type of environment. Could be one of EnvType or 'prod', 'eval', 'pentest'
        interactions : list of LogInteraction
            The list of interaction data to log.
        ignore_duplicates : bool
            If True, the system will ignore interactions with user_interaction_id that already exist in the system.

        Returns
        -------
        list of str
            List of the uuids of the interactions

        """
        result = self.api.log_batch(
            app_name=app_name,
            version_name=version_name,
            env_type=env_type,
            interactions=interactions,
            ignore_duplicates=ignore_duplicates,
        )
        return result.json()

    @HandleExceptions(logger)
    def update_interaction(
        self,
        app_name: str,
        version_name: str,
        user_interaction_id: str,
        annotation: t.Optional[t.Union[AnnotationType, str]] = None,
        annotation_reason: t.Optional[str] = None,
        user_value_properties: t.Union[t.List[UserValueProperty], None] = None,
        steps: t.Union[t.List[Step]] = None,
        information_retrieval: t.Union[t.List[str], str] = None,
        input: t.Union[str, None] = None,
        output: t.Union[str, None] = None,
        expected_output: t.Union[str, None] = None,
        action: t.Union[str, None] = None,
        tool_response: t.Union[str, None] = None,
        full_prompt: str = None,
        history: t.Union[t.List[str], str] = None,
        is_completed: t.Union[bool, None] = None,
        started_at: t.Union[datetime, float] = None,
        finished_at: t.Union[datetime, float] = None,
        metadata: t.Optional[t.Dict[str, str]] = None,
        tokens: t.Optional[int] = None,
    ):
        """Update a specific interaction by its user_interaction_id.

        Parameters
        ----------
        app_name : str
            Application name
        version_name
            Name of the version to which this interaction belongs
        user_interaction_id
            Unique id of the interaction to update
        annotation : AnnotationType or str
            Could be one of AnnotationType or 'good', 'bad', 'unknown'
        annotation_reason: str
            String that explains the reason for the annotation
        user_value_properties: list of UserValueProperty
            List of user value properties for interaction
        steps: list of Step
            List of steps taken during the interaction.
            New steps will be added to existing ones for previously incomplete interactions.
            Cannot be changed for completed interactions
        information_retrieval : str or list of str
            Information retrieval. New data will be added to existing ones for previously incomplete interactions.
            Cannot be changed for completed interactions
        input: str or None
            Input data. Old value will be overridden by the new value.
            Note that once interactions are marked as completed, this value cannot be changed.
        output: str or None
            Output data. Old value will be overridden by the new value.
            It cannot be modified for completed interactions.
        expected_output: str or None
            Expected output data. Old value will be overridden by the new value.
            It cannot be modified for completed interactions.
        action: str or None
            Action data. Old value will be overridden by the new value.
            It cannot be modified for completed interactions.
        tool_response: str or None
            Tool Response data. Old value will be overridden by the new value.
            It cannot be modified for completed interactions.
        full_prompt: str or None
            Full prompt data. Old value will be overridden by the new value.
            It cannot be modified for completed interactions.
        history: str or list of str
            History. New data will be added to existing ones for previously incomplete interactions.
            Cannot be changed for completed interactions
        is_completed: bool or None.
            Completed interactions will be shown in the system,
            and cannot be further modified except for annotations,
            topics and user value properties.
            Interaction completeness status will be not changed if None is sent
        started_at : datetime or float
            Timestamp the interaction started_at at. Datetime format is deprecated, use timestamp instead
        finished_at : datetime or float
            Timestamp the interaction finished at. Datetime format is deprecated, use timestamp instead
        metadata: Dict[str, str], optional
            Metdata for the interaction.
        tokens: int, optional
            Token count for the interaction.
        Returns
        -------
            None
        """
        # pylint: disable=redefined-builtin
        version_id = self._get_version_id(app_name=app_name, version_name=version_name)
        interaction_update = InteractionUpdate(
            annotation=annotation,
            annotation_reason=annotation_reason,
            user_value_properties=user_value_properties,
            steps=steps,
            information_retrieval=information_retrieval,
            input=input,
            output=output,
            expected_output=expected_output,
            action=action,
            tool_response=tool_response,
            full_prompt=full_prompt,
            history=history,
            is_completed=is_completed,
            started_at=started_at,
            finished_at=finished_at,
            metadata=metadata,
            tokens=tokens,
        )

        self.api.update_interaction(
            app_version_id=version_id,
            user_interaction_id=user_interaction_id,
            interaction_update=interaction_update,
        )

    @HandleExceptions(logger)
    def delete_interactions(self, app_name: str, version_name: str, user_interaction_ids: t.List[str]):
        """Delete specific interactions by their user_interaction_ids.

        Parameters
        ----------
        app_name : str
            Application name
        version_name: str
            Name of application version
        user_interaction_ids: List[str]
            List of interaction user ids to delete

        Returns
        -------
            None
        """
        version_id = self._get_version_id(app_name=app_name, version_name=version_name)
        self.api.delete_interactions(
            user_interaction_ids=user_interaction_ids, app_version_id=version_id,
        )

    @HandleExceptions(logger)
    def update_interaction_type_config(self, app_name: str, interaction_type: str, file):
        """Update the auto-annotation YAML configuration file for the interaction type within the application.

        Parameters
        ----------
        app_name : str
            Application name
        interaction_type: str
            Interaction Type you wish to update
        file : str
            The path to the configuration file to update

        Returns
        -------
            None
        """
        app_id = self._get_application_id(app_name)
        self.api.update_interaction_type_config(application_id=app_id, interaction_type=interaction_type, file=file)

    @HandleExceptions(logger)
    def get_interaction_type_config(self, app_name: str, interaction_type: str, file_save_path: t.Union[str, None] = None) -> str:
        """Write the auto-annotation YAML configuration file to the specified path.

        Parameters
        ----------
        app_name : str
            Application name
        interaction_type: str
            Interaction Type you wish to update
        file_save_path : str | None, optional
            The path to save the configuration file to. If None, the file will not be saved.

        Returns
        -------
        str
            The auto-annotation YAML configuration file as a string.
        """
        app_id = self._get_application_id(app_name)
        return self.api.get_interaction_type_config(application_id=app_id, interaction_type=interaction_type, file_save_path=file_save_path)

    @HandleGeneratorExceptions(init_logger)
    def data_iterator(self,
                      app_name: str,
                      version_name: str,
                      env_type: t.Union[EnvType, str],
                      start_time: t.Union[datetime, int, None] = None,
                      end_time: t.Union[datetime, int, None] = None,
                      user_interaction_ids: t.Union[t.List[t.Union[str, int]], None] = None,
                      include_incomplete: bool = False,
                      session_ids: t.Union[t.List[t.Union[str, int]], None] = None,
                      interaction_type: t.Union[str, None] = None,
                      ) -> t.Iterable[Interaction]:
        """
        Fetch all interactions from the specified environment type (PROD/EVAL) as an iterable.

        Supports pagination, so this API is suitable for iterating over large amounts of data.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of application version
        env_type : EnvType | str
            The environment type from which to fetch interactions. This can be either "PROD" or "EVAL".
        start_time : datetime | int | None, optional
            The start time from which to fetch interactions. This can be a datetime object or an integer.
            If not provided, interactions will be fetched from the beginning.
        end_time : datetime | int | None, optional
            The end time until which to fetch interactions. This can be a datetime object or an integer.
            If not provided, interactions will be fetched up to the most recent.
        user_interaction_ids: list | None, optional
            user interactions ids to include into the list of interactions.annotation_reason
        include_incomplete : bool
            Return only interactions with completed status or not.
            Only completed are returned by default.
        session_ids: list | None, optional
            List of session IDs to filter by. Maximum 1000 items allowed.
        interaction_type: str | None, optional
            Interaction types to filter by.

        Returns
        -------
        Iterable[Interaction]
            An iterable collection of interactions.

        """
        version_id = self._get_version_id(app_name=app_name, version_name=version_name)

        offset = 0
        limit = 20

        while True:
            interactions = \
                self.api.get_interactions(version_id,
                                          env_type=env_type,
                                          start_time_epoch=get_timestamp(start_time),
                                          end_time_epoch=get_timestamp(end_time),
                                          user_interaction_ids=[str(el) for el in user_interaction_ids] if user_interaction_ids else None,
                                          limit=limit, offset=offset,
                                          include_incomplete=include_incomplete,
                                          session_ids=[str(el) for el in session_ids] if session_ids else None,
                                          interaction_type=interaction_type,
                                          )
            for interaction in interactions:
                yield self._build_interaction_object(interaction)

            # If the size of the data is less than the limit, we"ve reached the end
            if len(interactions) < limit:
                break

            offset += limit

    @HandleExceptions(init_logger)
    def get_data(
            self,
            app_name: str,
            version_name: str,
            env_type: t.Union[EnvType, str],
            return_topics: bool = True, return_annotation_data: bool = True,
            return_builtin_props: bool = True,
            return_user_value_properties: bool = True,
            return_custom_prompt: bool = True,
            start_time: t.Union[datetime, int, None] = None,
            end_time: t.Union[datetime, int, None] = None,
            return_similarities: bool = False,
            user_interaction_ids: t.Union[t.List[str], None] = None,
            include_incomplete: bool = False,
            return_steps: bool = True,
            session_ids: t.Union[t.List[str], None] = None,
            interaction_type: t.Union[str, None] = None,
            return_session_related: bool = False,
            return_only_input_output_texts: bool = False,
    ) -> t.Union[pd.DataFrame, None]:
        """
        Fetch all the interactions from the specified environment (PROD/EVAL) as a pandas DataFrame.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of application version
        env_type : EnvType | str
            The environment type from which to fetch interactions. This can be either "PROD" or "EVAL".
        return_annotation_data : bool, optional
            Whether to include annotation info in the data.
        return_topics : bool, optional
            Whether to include the topic in the data.
        return_builtin_props : bool, optional
            Whether to include built-in properties in the data.
        return_user_value_properties : bool, optional
            Whether to include user value properties in the data.
        return_custom_prompt : bool, optional
            Whether to include LLM properties in the data.
        return_similarities : bool, optional
            Whether to include similarities in the data.
        start_time : datetime | int | None, optional
            The start time from which to fetch interactions. This can be a datetime object or an integer.
            If not provided, interactions will be fetched from the beginning.
        end_time : datetime | int | None, optional
            The end time until which to fetch interactions. This can be a datetime object or an integer.
            If not provided, interactions will be fetched up to the most recent.
        user_interaction_ids: list | None, optional
            user interactions ids to include in the data.
        include_incomplete : bool
            Return only interactions with completed status or not.
            Only completed are returned by default.
        return_steps : bool, optional
            Whether to include steps in the data.
        session_ids: list | None, optional
            List of session IDs to filter by. Maximum 1000 items allowed.
        interaction_type: str | None, optional
            interaction type to filter by.
        return_session_related: bool, optional
            Whether to include session related data in the data.
        return_only_input_output_texts: bool, optional
            If true the only text fields that would be included are input and output.
        Returns
        -------
        pd.DataFrame | None
            A pandas DataFrame containing the interactions, or None in case of a problem retrieving the data.
        """
        eval_set_version_id = self._get_version_id(app_name=app_name, version_name=version_name)
        csv_as_text = self.api.get_interactions_csv(
            eval_set_version_id,
            env_type=env_type,
            start_time_epoch=get_timestamp(start_time),
            end_time_epoch=get_timestamp(end_time),
            return_topics=return_topics,
            return_annotation_data=return_annotation_data,
            return_user_value_properties=return_user_value_properties,
            return_builtin_props=return_builtin_props,
            return_custom_prompt=return_custom_prompt,
            return_similarities=return_similarities,
            user_interaction_ids=user_interaction_ids,
            include_incomplete=include_incomplete,
            return_steps=return_steps,
            session_ids=session_ids,
            interaction_type=interaction_type,
            return_session_related=return_session_related,
            return_only_input_output_texts=return_only_input_output_texts,
        )
        if not csv_as_text:
            return pd.DataFrame()
        return pd.read_csv(io.StringIO(csv_as_text))

    @HandleExceptions(init_logger)
    def get_interaction_by_user_interaction_id(self, app_name: str, version_name: str, user_interaction_id: str) -> Interaction:
        """Get a specific interaction by its user_interaction_id.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of application version
        user_interaction_id : str
            Unique id of the interaction to get

        Returns
        -------
        Interaction
            The interaction object, including the input, output, properties and other fields
        """
        version_id = self._get_version_id(app_name=app_name, version_name=version_name)
        interaction = self.api.get_interaction_by_user_interaction_id(version_id, user_interaction_id)
        return self._build_interaction_object(interaction)

    def _get_application_id(self, app_name: str):
        app = self.api.get_application(app_name)
        if not app:
            raise DeepchecksLLMClientError(f"Application: \"{app_name}\", does not exist")
        return app["id"]

    def _get_application_kind(self, app_name: str):
        app = self.api.get_application(app_name)
        if not app:
            raise DeepchecksLLMClientError(f"Application: \"{app_name}\", does not exist")
        return app["kind"]

    def _get_version_id(self, app_name: str, version_name: str, create_if_not_exist: bool = False):

        app = self.api.get_application(app_name)
        if not app:
            raise DeepchecksLLMClientError(f"Application: \"{app_name}\", does not exist")
        eval_set_version = next((ver for ver in app["versions"] if ver["name"] == version_name), None)
        if not eval_set_version:
            if not create_if_not_exist:
                raise DeepchecksLLMClientError(
                    f"Could not find version \"{version_name}\", in application \"{app_name}\"",
                )
            else:
                return self.api.create_application_version(
                    application_id=app["id"], version_name=version_name,
                )["id"]

        return eval_set_version["id"]

    def get_pentest_prompts(self, app_name: str, probes: t.Optional[t.List[str]] = None) -> pd.DataFrame:
        """Get pentest prompts for the application.

        Parameters
        ----------
        app_name : str
            Application name
        probes: list of str
            List of probes to get pentest prompts for. If None, all probes will be returned.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing the pentest prompts
        """
        app_id = self._get_application_id(app_name)
        csv_content = self.api.get_pentest_prompts(app_id=app_id, probes=probes)
        df = pd.read_csv(io.StringIO(csv_content))
        return df

    def get_user_value_properties(self, app_name: str, interaction_type: t.Optional[str] = None) -> t.List[UserValuePropertyType]:
        """Get the user value properties defined for the current application.

        Parameters
        ----------
        app_name : str
            Application name
        interaction_type : str
            Interaction type

        Returns
        -------
        list[UserValuePropertyType]
            A list of user value properties defined for the application
        """
        app_id = self._get_application_id(app_name)
        user_value_properties = self.api.get_user_value_properties_definitions(application_id=app_id, interaction_type=interaction_type)
        return [
            UserValuePropertyType(
                display_name=prop["property_name"],
                type=prop["column_type"],
                description=prop.get("description")
            ) for prop in user_value_properties
        ]

    def create_user_value_property(
        self,
        app_name: str,
        name: str,
        prop_type: t.Union[PropertyColumnType, str],
        description: t.Optional[str] = None,
        interaction_type: t.Optional[str] = None,
    ) -> None:
        """Define a user value property for the current application.

        Parameters
        ----------
        app_name : str
            Application name
        name : str
            Name of the user value property
        prop_type : PropertyColumnType or str
            Type of the user value property (categorical, numeric)
        description : str, optional
            Description of the user value property
        interaction_type : str, optional
            Interaction type
        Returns
        -------
        None
        """
        app_id = self._get_application_id(app_name)
        self.api.create_user_value_property_definition(
            application_id=app_id,
            name=name,
            prop_type=prop_type,
            description=description,
            interaction_type=interaction_type,
        )

    @HandleExceptions(init_logger)
    def create_interaction_type(
        self,
        app_name: str,
        name: str,
        template_name: t.Optional[BuiltInInteractionType] = None
    ) -> int:
        """Activating Builtin type or Creating a new custom interaction type for the current application.

        Parameters
        ----------
        app_name : str
            Application name
        name : str
            Name of the interaction type
        template_name: BuiltInInteractionType
            Template of the interaction type
        Returns
        -------
        int
            Interaction type id
        """
        app_id = self._get_application_id(app_name)
        create_interaction_response = self.api.create_interaction_type(
            app_id=app_id,
            name=name,
            template_name=template_name,
        )
        return create_interaction_response["id"]

    @HandleExceptions(init_logger)
    def update_interaction_type(
        self,
        interaction_type_id: int,
        name: t.Optional[str] = None,
    ):
        """Update interaction type for the current application.

        Parameters
        ----------
        interaction_type_id : int
            Interaction type id
        name : str, optional
            Name of the custom interaction type

        Returns
        -------
        None
        """
        self.api.update_interaction_type(
            interaction_type_id=interaction_type_id,
            name=name,
        )

    @HandleExceptions(init_logger)
    def get_interaction_types(self, app_name: str) -> t.List[InteractionType]:
        """Get the custom interaction types defined for the current application.

        Parameters
        ----------
        app_name : str
            Application name

        Returns
        -------
        list[InteractionType]
            A list of interaction types defined for the application
        """
        app_id = self._get_application_id(app_name)
        interaction_types = self.api.get_interaction_types(
            app_id=app_id,
        )
        return [
            InteractionType(
                id=interaction_type["id"],
                name=interaction_type["name"],
            ) for interaction_type in interaction_types
        ]

    @HandleExceptions(init_logger)
    def delete_interaction_type(self, interaction_type_id: int):
        """Delete interaction type.

        Parameters
        ----------
        interaction_type_id : int
            Interaction type id
        Returns
        -------
        None
        """
        self.api.delete_interaction_type(
            interaction_type_id=interaction_type_id,
        )

    @HandleExceptions(logger)
    def create_interaction_type_version_data(
        self,
        app_name: str,
        version_name: str,
        interaction_type: str,
        model: t.Optional[str] = None,
        prompt: t.Optional[str] = None,
        metadata_params: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        """Create interaction type version data.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Version name
        interaction_type : str
            Interaction type name
        model : str, optional
            Model name
        prompt : str, optional
            Prompt template
        metadata_params : dict, optional
            Additional metadata parameters

        Returns
        -------
        InteractionTypeVersionData
            Created interaction type version data
        """
        app_version_id = self._get_version_id(app_name, version_name)

        interaction_type_id = None
        interaction_types = self.get_interaction_types(app_name)
        for it in interaction_types:
            if it.name.lower() == interaction_type.lower():
                interaction_type_id = it.id
                break
        if interaction_type_id is None:
            raise DeepchecksLLMClientError(f"Interaction type '{interaction_type}' not found")

        data = self.api.create_interaction_type_version_data(
            interaction_type_id=interaction_type_id,
            application_version_id=app_version_id,
            model=model,
            prompt=prompt,
            metadata_params=metadata_params,
        )
        return InteractionTypeVersionData(
            id=data["id"],
            interaction_type_id=data["interaction_type_id"],
            application_version_id=data["application_version_id"],
            model=data["model"],
            prompt=data["prompt"],
            metadata_params=data["metadata_params"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    @HandleExceptions(logger)
    def get_interaction_types_version_data(
        self,
        app_name: str,
        version_name: str,
    ):
        """Get interaction types version data.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Version name

        Returns
        -------
        list[InteractionTypeVersionData]
            List of interaction type version data
        """
        app_version_id = self._get_version_id(app_name, version_name)

        data_list = self.api.get_interaction_types_version_data(
            application_version_id=app_version_id,
        )

        return [
            InteractionTypeVersionData(
                id=data["id"],
                interaction_type_id=data["interaction_type_id"],
                application_version_id=data["application_version_id"],
                model=data["model"],
                prompt=data["prompt"],
                metadata_params=data["metadata_params"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            for data in data_list
        ]

    @HandleExceptions(logger)
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
        InteractionTypeVersionData
            Updated interaction type version data
        """
        data = self.api.update_interaction_type_version_data(
            interaction_type_data_id=interaction_type_data_id,
            model=model,
            prompt=prompt,
            metadata_params=metadata_params,
        )
        return InteractionTypeVersionData(
            id=data["id"],
            interaction_type_id=data["interaction_type_id"],
            application_version_id=data["application_version_id"],
            model=data["model"],
            prompt=data["prompt"],
            metadata_params=data["metadata_params"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    @HandleExceptions(logger)
    def delete_interaction_type_version_data(self, interaction_type_data_id: int):
        """Delete interaction type version data.

        Parameters
        ----------
        interaction_type_data_id : int
            Interaction type version data id

        Returns
        -------
        None
        """
        self.api.delete_interaction_type_version_data(
            interaction_type_data_id=interaction_type_data_id,
        )

    @HandleExceptions(init_logger)
    def get_interactions_complete_status(
            self,
            app_name: str,
            version_name: str,
            user_interaction_ids: t.List[str],
            events_to_check: t.Optional[t.List[InteractionCompleteEvents]] = None,
    ):
        """Get the completion status of interactions for specified events and user interaction IDs.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of application version
        events_to_check : Optional[List[InteractionCompleteEvents]]
            A list of events whose completion status needs to be checked. By default, only annotation_completed is
            checked
        user_interaction_ids : List[str]
            A list of user interaction IDs to check for completion status.

        Returns
        -------
        Dict[InteractionCompleteEvents, bool]
            A dictionary where keys are events from `events_to_check`
            and values are objects that indicating whether interactions for each event are completed and number of
            completed interactions {"annotation_completed": {"all_completed": True, "number_of_completed": 10}}
        """
        if not events_to_check:
            events_to_check = [InteractionCompleteEvents.ANNOTATION_COMPLETED]

        version_id = self._get_version_id(app_name=app_name, version_name=version_name)
        return self.api.get_interactions_complete_status(
            app_version_id=version_id,
            events_to_check=events_to_check,
            user_interaction_ids=user_interaction_ids,
        )

    @staticmethod
    def _validate_retry_interval_in_seconds(retry_interval_in_seconds):
        if retry_interval_in_seconds < 3:
            raise DeepchecksLLMClientError("retry_interval_in_seconds cannot be lower then 3 seconds")

    @HandleExceptions(init_logger)
    def get_data_if_calculations_completed(
            self,
            app_name: str,
            version_name: str,
            env_type: EnvType,
            user_interaction_ids: t.List[str],
            events_to_check: t.Optional[t.List[InteractionCompleteEvents]] = None,
            max_retries: int = 60,
            retry_interval_in_seconds: int = 3,
            return_topics: bool = True, return_annotation_data: bool = True,
            return_builtin_props: bool = True,
            return_user_value_properties: bool = True,
            return_custom_prompt: bool = True,
            return_similarities: bool = False,
    ) -> t.Optional[pd.DataFrame]:
        """Check if calculations for specified events are completed by calling `get_interactions_complete_status`.

        If all user_interaction_ids completed then we will fetch the data for those ids,
        if not - will sleep and retry again. Consider increasing max_retries or retry_interval_in_seconds if running
        the method returns None.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of application version
        env_type : EnvType
            Environment type
        events_to_check : Optional[List[InteractionCompleteEvents]]
            A list of events whose completion status needs to be checked. By default, only annotation_completed
            is checked
        user_interaction_ids : List[str]
            A list of user interaction IDs to retrieve data for.
        max_retries : Optional[int]
            Maximum number of retries if calculations are not completed. Defaults to 60.
        retry_interval_in_seconds : Optional[float]
            Interval between retries in seconds. Defaults to 3.
        return_annotation_data : bool, optional
            Whether to include annotation info in the data.
        return_topics : bool, optional
            Whether to include the topic in the data.
        return_annotation_data : bool, optional
            Whether to include annotation info in the data.
        return_builtin_props : bool, optional
            Whether to include built-in properties in the data.
        return_user_value_properties : bool, optional
            Whether to include custom properties in the data.
        return_custom_prompt : bool, optional
            Whether to include Custom Prompt properties in the data.
        return_similarities : bool, optional
            Whether to include similarities in the data.

        Returns
        -------
        Optional[pd.DataFrame]
            A DataFrame containing the retrieved data if calculations are completed, otherwise None.
        """
        self._validate_retry_interval_in_seconds(retry_interval_in_seconds)

        if not events_to_check:
            events_to_check = [InteractionCompleteEvents.ANNOTATION_COMPLETED]
        retry_count = 0
        while retry_count < max_retries:
            complete_statuses = self.get_interactions_complete_status(
                app_name=app_name,
                version_name=version_name,
                events_to_check=events_to_check,
                user_interaction_ids=user_interaction_ids,
            )
            if all(status["all_completed"] for status in complete_statuses.values()):
                return self.get_data(
                    app_name=app_name,
                    version_name=version_name,
                    env_type=env_type,
                    return_topics=return_topics,
                    return_annotation_data=return_annotation_data,
                    return_builtin_props=return_builtin_props,
                    return_user_value_properties=return_user_value_properties,
                    return_custom_prompt=return_custom_prompt,
                    return_similarities=return_similarities,
                    user_interaction_ids=user_interaction_ids,
                )
            else:
                for event, status in complete_statuses.items():
                    logger.debug(f"{event} = {status['number_of_completed']}")
                retry_count += 1
                time.sleep(retry_interval_in_seconds)
        return None

    @staticmethod
    def _build_interaction_object(interaction: dict) -> Interaction:
        return Interaction(
            user_interaction_id=interaction["user_interaction_id"],
            input=interaction["input"]["data"] if interaction.get("input") else None,
            information_retrieval=[i["data"] for i in interaction["information_retrieval"]] if
            interaction.get("information_retrieval") else None,
            history=[i["data"] for i in interaction["history"]] if interaction.get("history") else None,
            full_prompt=interaction["prompt"]["data"] if interaction.get("prompt") else None,
            output=interaction["output"]["data"] if interaction.get("output") else None,
            expected_output=interaction["expected_output"]["data"] if interaction.get("expected_output") else None,
            action=interaction["action"]["data"] if interaction.get("action") else None,
            tool_response=interaction["tool_response"]["data"] if interaction.get("tool_response") else None,
            created_at=interaction["created_at"],
            interaction_datetime=interaction["interaction_datetime"],
            topic=interaction["topic"],
            builtin_properties={**(interaction.get("output_properties") or {}), **(interaction.get("input_properties") or {})},
            user_value_properties=interaction.get("custom_properties") or {},
            custom_prompt_properties=interaction.get("llm_properties") or {},
            properties_reasons=interaction.get("properties_reasons") or {},
            is_completed=interaction["is_completed"],
            session_id=interaction["session_id"],
            interaction_type=interaction["interaction_type"]["name"],
            metadata=interaction["metadata"],
            tokens=interaction["tokens"],
            annotation=None if interaction.get("annotation") is None else (
                interaction["annotation"]["value"] and AnnotationType(interaction["annotation"]["value"])),
            annotation_reason=None if interaction.get("annotation") is None else interaction["annotation"]["reason"],
        )
