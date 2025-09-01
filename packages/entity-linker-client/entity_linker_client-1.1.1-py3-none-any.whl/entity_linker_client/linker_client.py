import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union
from uuid import UUID
from .models import EntityLinkingConfig
from .config import default_config
from .utils import convert_config_to_dict
from .http_client import HttpClient

load_dotenv()

BASE_URL = os.getenv("ENTITY_LINKER_BASE_URL", "http://entitylinker:6000")


class EntityLinker:
    """
    A client for interacting with the Entity Linker service.

    This class can be used to manage linkers on the service, or to interact with a specific linker instance
    by initializing the class with a linker_id.

    Attributes:
        base_url (str): The base URL of the entity linker service.
        linker_id (Optional[UUID]): The ID of the linker instance.
        config (Optional[EntityLinkingConfig]): The configuration of the linker instance.
        client (HttpClient): The HTTP client for making requests to the service.
    """

    def __init__(self, base_url: str = BASE_URL, linker_id: Optional[UUID] = None,
                 config: Optional[EntityLinkingConfig] = None,
                 source_columns: Optional[List[str]] = None,
                 target_columns: Optional[List[str]] = None
                 ):
        """
        Initializes the EntityLinker client.

        If a `linker_id` is provided, the client will interact with an existing linker.
        If no `linker_id` is provided, a new linker will be created based on the provided `config`.
        If no `config` is provided, a new one will be generated using `source_columns` and `target_columns`.

        Args:
            base_url (str): The base URL of the entity linker service.
            linker_id (Optional[UUID]): The ID of an existing linker.
            config (Optional[EntityLinkingConfig]): The configuration for a new linker.
            source_columns (Optional[List[str]]): A list of column names from the source table to generate a config.
            target_columns (Optional[List[str]]): A list of column names from the target table to generate a config.

        Raises:
            ValueError: If no `linker_id` or `config` is provided, and `source_columns` or `target_columns` are missing.
        """
        self.base_url = base_url.rstrip('/')
        self.client = HttpClient(self.base_url)
        self.linker_id = linker_id
        self.config = convert_config_to_dict(config) if config else None

        if self.linker_id is None:
            if self.config is None:
                if not source_columns or not target_columns:
                    raise ValueError(
                        "If a new linker is being created without a config, "
                        "source_columns and target_columns must be provided to generate a new config.")

                # Generate a new config
                self.config = self.generate_config(
                    initial_config=default_config,
                    source_columns=source_columns,
                    target_columns=target_columns,
                    base_url=self.base_url
                )
                self._create_linker(self.config)

            else:
                self._create_linker(self.config)
        else:
            if self.config is None:
                self.config = self.get_info().get('config', {})

    def _create_linker(self, config: Dict[str, Any]):
        """
        Creates a new linker on the service.

        This method is called internally during initialization if no `linker_id` is provided.

        Args:
            config (Dict[str, Any]): The configuration for the new linker.

        Raises:
            Exception: If the linker creation fails.
        """
        response = self.client.post("/api/linkers", json=config)
        if not response or "linker_id" not in response:
            raise Exception(
                "Failed to create linker: 'linker_id' not in response.")
        self.linker_id = UUID(response["linker_id"])
        print(f"Created new linker with ID: {self.linker_id}")

    @staticmethod
    def list_available_linkers(base_url: str = BASE_URL) -> List[Dict[str, Any]]:
        """
        Lists all available entity linkers on the service.

        Args:
            base_url (str): The base URL of the entity linker service.

        Returns:
            A list of dictionaries, where each dictionary represents an available linker.
        """
        with HttpClient(base_url) as client:
            response = client.get("/api/linkers")
            if response is None:
                return []
            return response

    @staticmethod
    def get_linker_info(linker_id: str, base_url: str = BASE_URL) -> Dict[str, Any]:
        """
        Gets all available information for a specific entity linker.

        Args:
            linker_id (str): The ID of the linker to retrieve information for.
            base_url (str): The base URL of the entity linker service.

        Returns:
            A dictionary containing information about the specified linker.
        """
        with HttpClient(base_url) as client:
            response = client.get(f"/api/linkers/{linker_id}")
            if response is None:
                return {}
            return response

    @staticmethod
    def generate_config(initial_config: EntityLinkingConfig, source_columns: List[str], target_columns: List[str], base_url: str = BASE_URL) -> Dict[str, Any]:
        """
        Generates a new configuration for an entity linker based on table schemas.

        Args:
            initial_config (EntityLinkingConfig): An initial configuration to base the generation on.
            source_columns (List[str]): A list of column names from the source entities.
            target_columns (List[str]): A list of column names from the target entities.
            base_url (str): The base URL of the entity linker service.

        Returns:
            A dictionary representing the generated configuration.

        Raises:
            ValueError: If the API returns an empty response.
        """
        dict_config = convert_config_to_dict(initial_config)
        with HttpClient(base_url) as client:
            response = client.post("/api/linkers/generate-config", json={
                "initial_config": dict_config, "source_columns": source_columns, "target_columns": target_columns})
        if response is None:
            raise ValueError(
                "Failed to generate config: API returned an empty response.")
        return response

    def get_info(self) -> Dict[str, Any]:
        """
        Gets information about this specific entity linker instance.

        Returns:
            A dictionary containing information about the linker.

        Raises:
            ValueError: If the linker has no ID or if the API returns an empty response.
        """
        if not self.linker_id:
            raise ValueError(
                "Linker has no ID. It may not have been created successfully.")
        response = self.client.get(f"/api/linkers/{self.linker_id}")
        if response is None:
            raise ValueError(
                "Failed to get linker info: API returned an empty response.")
        return response

    def update_config(self, config_updates: Union[EntityLinkingConfig, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Updates the configuration of this entity linker instance.

        Args:
            config_updates (Union[EntityLinkingConfig, Dict[str, Any]]): An object containing the configuration updates.

        Returns:
            A dictionary confirming the updates.

        Raises:
            ValueError: If the linker has no ID or if the API returns an empty response.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        if isinstance(config_updates, EntityLinkingConfig):
            config_dict = convert_config_to_dict(config_updates)
        else:
            config_dict = config_updates
        response = self.client.put(
            f"/api/linkers/{self.linker_id}/config", json=config_dict)
        if response is None:
            raise ValueError(
                "Failed to update config: API returned an empty response.")
        self.config = config_updates
        return response
    
    def delete_linker(self) -> None:
        """
        Deletes this linker instance.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        self.client.delete(f"/api/linkers/{self.linker_id}")
        self.linker_id = None

    def add_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a new entity to this linker instance.

        Args:
            entity_data (Dict[str, Any]): A dictionary containing the data for the new entity.

        Returns:
            A dictionary representing the added entity.

        Raises:
            ValueError: If the linker has no ID or if the API returns an empty response.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        response = self.client.post(
            f"/api/linkers/{self.linker_id}/entities", json=entity_data)
        if response is None:
            raise ValueError(
                "Failed to add entity: API returned an empty response.")
        return response

    def add_entities_batch(self, entities_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adds a batch of new entities to this linker instance.

        Args:
            entities_data (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                                  represents a new entity.

        Returns:
            A list of dictionaries representing the added entities.

        Raises:
            ValueError: If the linker has no ID.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        response = self.client.post(
            f"/api/linkers/{self.linker_id}/entities/batch", json=entities_data)
        if response is None:
            raise ValueError(
                "Failed to add entities: API returned an empty response.")
        return response

    def get_entity(self, entity_id: UUID) -> Dict[str, Any]:
        """
        Gets a specific entity from this linker instance by its ID.

        Args:
            entity_id (UUID): The ID of the entity to retrieve.

        Returns:
            A dictionary representing the requested entity.

        Raises:
            ValueError: If the linker has no ID or if the API returns an empty response.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        response = self.client.get(
            f"/api/linkers/{self.linker_id}/entities/{entity_id}")
        if response is None:
            raise ValueError(
                f"Failed to get entity {entity_id}: API returned an empty response.")
        return response

    def modify_entity(self, entity_id: UUID, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifies an existing entity in this linker instance.

        Args:
            entity_id (UUID): The ID of the entity to modify.
            entity_data (Dict[str, Any]): A dictionary containing the updated entity data.

        Returns:
            A dictionary representing the modified entity.

        Raises:
            ValueError: If the linker has no ID or if the API returns an empty response.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        response = self.client.put(
            f"/api/linkers/{self.linker_id}/entities/{entity_id}", json=entity_data)
        if response is None:
            raise ValueError(
                f"Failed to modify entity {entity_id}: API returned an empty response.")
        return response

    def delete_entity(self, entity_id: UUID) -> None:
        """
        Deletes an entity from this linker instance.

        Args:
            entity_id (UUID): The ID of the entity to delete.

        Raises:
            ValueError: If the linker has no ID.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        self.client.delete(
            f"/api/linkers/{self.linker_id}/entities/{entity_id}")

    def link_entity(self, entity_data: Dict[str, Any], add_entity: bool = False) -> Dict[str, Any]:
        """
        Finds and links entities based on the provided data.

        Args:
            entity_data (Dict[str, Any]): A dictionary containing the entity data to link.
            add_entity (bool): If True, adds the entity to the database if no match is found. 
                               Defaults to False.

        Returns:
            A dictionary containing the linking results. An empty dictionary is returned if no
            link is found.

        Raises:
            ValueError: If the linker has no ID.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        params = {"add_entity": add_entity}
        response = self.client.post(
            f"/api/linkers/{self.linker_id}/link", json=entity_data, params=params)
        if response is None:
            # A link operation not finding anything can be represented by an empty dictionary.
            return {}
        return response

    def link_entity_with_id(self, entity_id: UUID) -> Dict[str, Any]:
        """
        Links an entity to an existing one within a linker.
        
        Args:
            entity_id (UUID): The ID of the entity to link.
            
        Returns:
            A dictionary containing the linking results. An empty dictionary is returned if no
            link is found.
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        
        params = {"entity_id": str(entity_id)}
        response = self.client.post(
            f"/api/linkers/{self.linker_id}/link-with-id", params=params)
        if response is None:
            return {}
        return response

    def link_entities_batch(self, entities_data: List[Dict[str, Any]], fast_linking: bool = True) -> List[Dict[str, Any]]:
        """
        Links multiple entities in batches.
        
        This method efficiently processes multiple entities by first batch inserting them into the database,
        then performing parallel linking operations. The batch approach significantly improves performance
        compared to linking entities individually.

        Args:
            entities_data (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                                  represents an entity to link.
            fast_linking (bool): Whether to use fast linking methods first. 
                                 Defaults to True.

        Returns:
            A list of dictionaries containing the batch linking results with the following structure:
            [
                {
                    "entity_id": "uuid-of-input-entity",
                    "linked_entity_id": "uuid-of-matched-entity" or null
                },
                ...
            ]
        """
        if not self.linker_id:
            raise ValueError("Linker has no ID.")
        
        payload = {
            "entity_models": entities_data,
            "fast_linking": fast_linking
        }
        
        response = self.client.post(
            f"/api/linkers/{self.linker_id}/link-batch", json=payload)
        
        if response is None:
            raise ValueError(
                "Failed to batch link entities: API returned an empty response.")
        
        return response