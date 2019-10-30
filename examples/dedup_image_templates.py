"""
Mindsay SDK example to replace entity type
"""
import logging
from collections import defaultdict

import tqdm
from mindsay_sdk import Client


logger = logging.getLogger("mindsay")


USER_EMAIL = "gratien@destygo.com"
INSTANCE_NAME = "Benchmark NLP - test"
LANGUAGE = "fr_FR"
EXPERIMENT_ID = 15

MINDSAY = Client(USER_EMAIL, production=True)


def setup_bos_environment():
    """Setup instance, language and experiment"""
    instances = MINDSAY.get_instances()
    instance = [
        instance for instance in instances if instance["name"] == INSTANCE_NAME
    ][0]
    MINDSAY.set_current_instance(instance["id"])
    MINDSAY.set_current_language(LANGUAGE)
    MINDSAY.set_current_experiment(EXPERIMENT_ID)


def _groupby_name(array):
    """Group list of dict by 'name' attribute"""
    res = defaultdict(list)
    for element in array:
        res[element["name"]].append(element)
    return res


def get_all_answers():
    """Gather all answers content in a list"""
    answer_record_ids = MINDSAY.get("/answers").json()

    answers = []
    for answer_record_id in answer_record_ids:
        answer = MINDSAY.get("/answers/{}".format(answer_record_id["record_id"])).json()
        answers.append(answer)

    return answers


def dedup_image_templates():
    """
    1. Group image templates by name
    2. Assumes 'same name' = 'duplicate'
    3. Adjust depending templates to point on image_template #1
    4. Keep image_template #1 and remove duplicates
    """
    image_templates = MINDSAY.get("/image_templates").json()
    dupl_image_templates_by_name = {
        name: image_templates
        for name, image_templates in _groupby_name(image_templates).items()
        if len(image_templates) > 1
    }
    logger.info("Duplicated image_templates: %s", len(dupl_image_templates_by_name))
    answers = get_all_answers()
    templates = [template for answer in answers for template in answer["templates"]]

    for image_template_name, image_templates_group in tqdm.tqdm(
        dupl_image_templates_by_name.items()
    ):
        if len(image_templates_group) <= 1:
            continue
        logger.info("image_template_name %s is duplicated", image_template_name)
        image_template_record_ids = [
            image_template["record_id"] for image_template in image_templates_group
        ]

        # update templates with reference image_template
        updated_templates = []
        for template in templates:
            if template["image_template_record_id"] in image_template_record_ids[1:]:
                template["image_template_record_id"] = image_template_record_ids[0]
                MINDSAY.put(
                    f'/templates/{template["record_id"]}/',
                    json={"image_template_record_id": image_template_record_ids[0]},
                )
                updated_templates.append(template["record_id"])
        logger.info(
            "%s updated templates: %s", len(updated_templates), updated_templates
        )

        # remove unused image_templates
        for image_template_record_id in image_template_record_ids[1:]:
            MINDSAY.delete(f"/image_templates/{image_template_record_id}")

        logger.info(
            "%s deleted image_templates: %s",
            len(image_template_record_ids[1:]),
            image_template_record_ids[1:],
        )


def is_image_templates_dedup():
    """Sanity check"""
    image_templates = MINDSAY.get("/image_templates").json()
    assert not [
        image_templates
        for image_templates in _groupby_name(image_templates).values()
        if len(image_templates) > 1
    ]
