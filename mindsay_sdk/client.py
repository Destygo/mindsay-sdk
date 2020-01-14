"""
Mindsay SDK client
"""
import getpass
import logging
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests

from mindsay_sdk import utils

logging.basicConfig(
    format="%(asctime)-25s %(levelname)-8s logger=%(name)-8s event=%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)
logger = logging.getLogger("mindsay")


class Client(requests.Session):
    """
    Mindsay SDK Client class

    The client will sign in on initialization and will remain signed
    in as long as you use the same client object.
    """

    def __init__(self, email: str, production: bool = False):
        super().__init__()

        self.production = production
        environment = "PRODUCTION" if self.production else "staging"

        if self.production:
            logger.warning("Connecting to Mindsay on %s...", environment)
            self.base_url = "https://bos.destygo.com/"
        else:
            logger.warning(
                "Connecting to Mindsay on %s... "
                "Remember to connect to the Mindsay WiFi or set up a SSH tunnel!",
                environment,
            )
            self.base_url = "https://staging-bos.destygo.com/"

        self._user_sign_in(email)
        logger.warning("Connected to Mindsay on %s", environment)

    @classmethod
    def create_client(
        cls,
        user_email: str,
        instance_name: str,
        language: str,
        production: bool,
        experiment_id: Optional[int] = None,
    ) -> "Client":
        """Setup instance, language and experiment if specified"""
        client = cls(user_email, production=production)

        # Get the instance by name
        instances = client.get_instances()
        instance = [
            instance for instance in instances if instance["name"] == instance_name
        ][0]
        client.set_current_instance(instance["id"])

        client.set_current_language(language)

        if experiment_id is not None:
            client.set_current_experiment(experiment_id)

        return client

    def _user_sign_in(self, email: str) -> None:
        """
        Asks for the user password to log in and set Authorization
        header to the client
        """
        password = getpass.getpass(prompt="Password: ")
        response = self.post(
            "users/sign_in", json={"user": {"email": email, "password": password}}
        )
        response.raise_for_status()
        self.headers["Authorization"] = response.headers["Authorization"]
        if response.json()["otp_required_for_login"]:
            self._user_code_auth(email)

    def _user_code_auth(self, email: str) -> None:
        """
        Asks for user email code to authentify and add response
        cookies to the client
        """
        otp_attempt = getpass.getpass(prompt="Email code: ")
        response = self.post(
            "users/code_auth",
            json={"user": {"email": email, "otp_attempt": otp_attempt}},
        )
        response.raise_for_status()

        # self.cookies is defined in super __init__
        self.cookies = (  # pylint: disable=attribute-defined-outside-init
            response.cookies
        )

    def get_current_environment(self) -> dict:
        """Returns information about the current client environment"""
        response = self.get("environment/base")
        response.raise_for_status()
        return response.json()

    def get_bots(self) -> List[Dict[str, Any]]:
        """Returns all bots"""
        # TODO: How to list bots only on current instance ?
        response = self.get("/bots")
        response.raise_for_status()
        return response.json()

    def set_current_bot(self, bot_id: int) -> Dict[str, Any]:
        """Set the current bot"""
        response = self.post("environment/set_current_bot", json={"bot_id": bot_id})
        response.raise_for_status()
        return response.json()

    def get_experiments(self) -> List[Dict[str, Any]]:
        """Returns all experiments"""
        response = self.get("/experiments")
        response.raise_for_status()
        return response.json()

    def set_current_experiment(self, experiment_id: int) -> Dict[str, Any]:
        """Set the current experiment"""
        environment = self.get_current_environment()
        if not environment["current_bot"]["can_use_experiments?"]:
            raise ValueError("This bot cannot use experiments")
        response = self.post(
            "environment/set_current_experiment", json={"experiment_id": experiment_id}
        )
        response.raise_for_status()
        return response.json()

    def get_instances(self) -> List[Dict[str, Any]]:
        """Returns all instances"""
        # TODO: How to list only my instances ?
        response = self.get("/instances")
        response.raise_for_status()
        return response.json()

    def get_instance(self, instance_id: int) -> dict:
        """Returns the instance matching the given id"""
        response = self.get(f"instances/{instance_id}")
        response.raise_for_status()
        return response.json()

    def set_current_instance(self, instance_id: int) -> Dict[str, Any]:
        """Set the instance for next operations"""
        if self.production:
            instance = self.get_instance(instance_id)
            utils.verify_prompt(
                "Enter your instance name to confirm: ", instance["name"]
            )
        response = self.post(
            "environment/set_current_instance", json={"instance_id": instance_id}
        )
        # NOTE: BOS returns a status code 200 when instance_id does
        # not exist and an HTML error
        response.raise_for_status()
        logger.info(
            "Switched to instance %s", response.json()["current_instance"]["name"]
        )
        return response.json()

    def set_current_language(self, language: str) -> Dict[str, Any]:
        """Set the current environment language"""
        response = self.post("environment/change_language", json={"language": language})
        response.raise_for_status()
        logger.info("Current language updated: %s", language)
        return response.json()

    def get_entity_type(self, entity_type_record_id: int) -> Dict[str, Any]:
        """Returns the entity type matching the given id"""
        response = self.get(f"entity_types/{entity_type_record_id}")
        response.raise_for_status()
        return response.json()

    def get_services(self) -> List[Dict[str, Any]]:
        """Returns all services in the current instance"""
        response = self.get("/services")
        response.raise_for_status()
        return response.json()

    def get_service(self, service_record_id: int) -> Dict[str, Any]:
        """Returns the required service"""
        response = self.get(f"/services/{service_record_id}")
        response.raise_for_status()
        return response.json()

    def get_user_nodes(self) -> List[Dict[str, Any]]:
        """Returns all user nodes in the current instance"""
        response = self.get("/user_nodes")
        response.raise_for_status()
        return response.json()

    def get_user_node(self, user_node_record_id: int) -> Dict[str, Any]:
        """Returns the required user node"""
        response = self.get(f"/user_nodes/{user_node_record_id}")
        response.raise_for_status()
        return response.json()

    def get_user_nodes_full(self) -> List[Dict[str, Any]]:
        """Returns all user nodes with full information"""
        return [self.get_user_node(un["record_id"]) for un in self.get_user_nodes()]

    def get_intent(self, intent_record_id: int) -> Dict[str, Any]:
        """Returns the intent matching the given id"""
        response = self.get(f"intents/{intent_record_id}")
        response.raise_for_status()
        return response.json()

    def deploy_intent(self, intent_record_id: int) -> Dict[str, Any]:
        """Deploy the intent matching the given id"""
        response = self.put(f"intents/{intent_record_id}/deploy")
        response.raise_for_status()
        return response.json()

    def get_machine_nodes(self) -> Dict[str, Any]:
        """Returns all machine nodes in the current instance"""
        response = self.get(f"machine_nodes")
        response.raise_for_status()
        return response.json()

    def get_machine_node(self, machine_node_record_id: int) -> Dict[str, Any]:
        """Returns the required machine node"""
        response = self.get(f"machine_nodes/{machine_node_record_id}")
        response.raise_for_status()
        return response.json()

    def get_case_statements(self) -> Dict[str, Any]:
        """Returns all case statements in the current instance"""
        response = self.get(f"case_statements")
        response.raise_for_status()
        return response.json()

    def get_case_statement(self, case_statement_record_id: int) -> Dict[str, Any]:
        """Returns the required case statement"""
        response = self.get(f"case_statements/{case_statement_record_id}")
        response.raise_for_status()
        return response.json()

    def get_answers(self) -> Dict[str, Any]:
        """Returns all answers in the current instance"""
        response = self.get(f"answers")
        response.raise_for_status()
        return response.json()

    def get_answer(self, answer_record_id: int) -> Dict[str, Any]:
        """Returns the required answer"""
        response = self.get(f"answers/{answer_record_id}")
        response.raise_for_status()
        return response.json()

    def update_entity(self, entity_record_id: int, entity: dict) -> Dict[str, Any]:
        """Update the entity matching the given id with the given entity object"""
        response = self.put(f"entities/{entity_record_id}", json=entity)
        response.raise_for_status()
        return response.json()

    def get_knowledge_bases(self) -> List[Dict[str, Any]]:
        """Returns all user nodes in the current instance"""
        response = self.get("/knowledge_bases")
        response.raise_for_status()
        return response.json()

    def get_knowledge_base(self, knowledge_base_record_id: int) -> List[Dict[str, Any]]:
        """Returns all user nodes in the current instance"""
        response = self.get(f"/knowledge_bases/{knowledge_base_record_id}")
        response.raise_for_status()
        return response.json()

    def delete_knowledge_base(self, knowledge_base_record_id: int) -> None:
        response = self.delete(f"/knowledge_bases/{knowledge_base_record_id}")
        response.raise_for_status()

    def get_api_connectors(self) -> List[Dict[str, Any]]:
        """Returns all user nodes in the current instance"""
        response = self.get("/api_connectors")
        response.raise_for_status()
        return response.json()

    def get_api_connector(self, api_connector_record_id: int) -> List[Dict[str, Any]]:
        """Returns all user nodes in the current instance"""
        response = self.get(f"/api_connectors/{api_connector_record_id}")
        response.raise_for_status()
        return response.json()

    def get_channels(self) -> List[Dict[str, Any]]:
        response = self.get("/channels")
        response.raise_for_status()
        return response.json()

    def get_channel(self, channel_uuid: str) -> Dict[str, Any]:
        response = self.get(f"/channels/{channel_uuid}")
        response.raise_for_status()
        return response.json()

    def get(self, url, **kwargs) -> requests.Response:
        """Perform a GET request using the Mindsay base URL"""
        return super().get(self.base_url + url, **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request using the Mindsay base URL"""
        return super().put(self.base_url + url, **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request using the Mindsay base URL"""
        return super().post(self.base_url + url, **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request using the Mindsay base URL"""
        return super().delete(self.base_url + url, **kwargs)
