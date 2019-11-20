"""
Mindsay SDK example to replace entity type
"""
from mindsay_sdk import Client
from mindsay_sdk import utils


def replace_entity_type(
    user_email: str,
    instance_id: int,
    experiment_id: int,
    language: str,
    old_entity_type_record_id: int,
    new_entity_type_record_id: int,
):
    """
    Replaces the entity type old_entity_type_record_id with the
    new_entity_type_record_id in all intents for the given
    instance_id, experiment_id and language, using user_email to log
    in.
    """

    # Create mindsay client. This line will ask for your password and email code.
    mindsay = Client(user_email, production=False)

    # Define current environment for next operations
    mindsay.set_current_instance(instance_id)
    mindsay.set_current_experiment(experiment_id)
    mindsay.set_current_language(language)

    # Confirm that we are updating the right entity types (to avoid mistakes)
    old_entity_type = mindsay.get_entity_type(old_entity_type_record_id)
    new_entity_type = mindsay.get_entity_type(new_entity_type_record_id)

    utils.verify_prompt(
        f"Replace entity type {old_entity_type['name']} "
        f"({old_entity_type['record_id']}) "
        f"with entity type {new_entity_type['name']} "
        f"({new_entity_type['record_id']})? (y/n)",
        "y",
    )

    # Loop over all user nodes in the instance
    for user_node in [
        mindsay.get_user_node(un["record_id"]) for un in mindsay.get_user_nodes()
    ]:

        # Retrieve intents in the user node
        intents = [
            mindsay.get_intent(intent["record_id"]) for intent in user_node["intents"]
        ]

        # Select entities we want to update
        entities = [
            entity
            for intent in intents
            for entity in intent["entities"]
            if entity["entity_type_record_id"] == old_entity_type_record_id
        ]

        if entities:
            for entity in entities:
                print(
                    f"Update entity {entity['name']} ({entity['record_id']}) "
                    f"in intent {entity['intent_record_id']}"
                )
                entity["entity_type_record_id"] = new_entity_type_record_id
                mindsay.update_entity(entity["record_id"], entity)

            # Deploy an arbitrary intent in the user node because
            # deploy on a user node does not exist
            print(f"Train user node {user_node['name']} ({user_node['record_id']})")
            mindsay.deploy_intent(user_node["intents"][0]["record_id"])

    print("Done")
