import logging

import transaction
from zope.sqlalchemy import mark_changed
from caerp.scripts.utils import (
    command,
    get_value,
)
from caerp_base.models.base import DBSESSION as db


logger = logging.getLogger("caerp")


def load_edp_from_json_command(args, env):
    import json
    import datetime
    from caerp.models.task import Estimation
    from caerp.models.project import Project
    from caerp.models.user.user import User
    from caerp.models.price_study import (
        PriceStudyDiscount,
        PriceStudyProduct,
        PriceStudyWork,
        PriceStudyWorkItem,
        PriceStudy,
    )

    session = db()
    filename = get_value(args, "filepath")
    if not filename:
        raise Exception("Nom de fichier manquant")

    with open(filename, "r") as f:
        data = json.load(f)

    request = env["request"]
    request.dbsession = session
    edp_ids = []
    untreated = []
    devis_ids = []
    for edp in data:
        project = Project.get(edp["project_id"])
        company = project.company
        owner = User.get(edp["owner_id"])
        if not project or not company or not project.customers:
            untreated.append(edp)
            logger.warn(
                f"L'edp {edp} n'a pas pu être restaurée, il manque des clients, des projets ou des enseignes"
            )
            continue
        customer = project.customers[0]
        devis = Estimation.create(
            request,
            customer,
            {
                "project": project,
                "company": company,
                "business_type_id": project.project_type.get_default_business_type().id,
                "user": owner,
                "date": datetime.datetime.strptime(
                    edp["created_at"], "%Y-%m-%dT%H:%M:%S"
                ),
            },
        )
        devis_ids.append(devis.id)
        price_study = devis.set_price_study(request)
        chapter = price_study.chapters[0]
        general_overhead = set()
        for product_data in edp["products"]:
            product = PriceStudyProduct(
                chapter=chapter,
            )
            # Base sale product
            for key in (
                "margin_rate",
                "ht",
                "description",
                "unity",
                "quantity",
                "total_ht",
                "tva_id",
                "product_id",
            ):
                if product_data.get(key):
                    setattr(product, key, product_data[key])
            setattr(product, "order", product_data.get("`order`", 0))
            # product
            if product_data["supplier_ht"]:
                product_data["mode"] = "supplier_ht"
            else:
                product_data["mode"] = "ht"
            for key in ("mode", "supplier_ht", "base_sale_product_id"):
                if product_data.get(key):
                    setattr(product, key, product_data[key])
            session.add(product)
            session.flush()
            if product_data["general_overhead"]:
                general_overhead.add(product_data["general_overhead"])

        for work_data in edp["works"]:
            work = PriceStudyWork(chapter=chapter)
            # Base sale product
            for key in (
                "margin_rate",
                "ht",
                "description",
                "unity",
                "quantity",
                "total_ht",
                "tva_id",
                "product_id",
            ):
                if work_data.get(key):
                    setattr(work, key, work_data[key])
            # Work
            setattr(work, "title", work_data["title"])
            session.add(work)
            session.flush()
            if work_data["general_overhead"]:
                general_overhead.add(work_data["general_overhead"])
            for item_data in work_data["items"]:
                item = PriceStudyWorkItem(price_study_work=work)
                if item_data["supplier_ht"]:
                    item_data["mode"] = "supplier_ht"
                else:
                    item_data["mode"] = "ht"
                for key in (
                    "description",
                    "ht",
                    "supplier_ht",
                    "mode",
                    "unity",
                    "work_unit_ht",
                    "work_unit_quantity",
                    "quantity_inherited",
                    "work_unit_ht",
                    "total_ht",
                    "base_sale_product_id",
                ):
                    if item_data.get(key):
                        setattr(item, key, item_data[key])

                session.add(item)
                session.flush()

        if len(general_overhead) > 0:
            if len(general_overhead) > 1:
                logger.warn(
                    f"!!! L'edp {price_study.id} avait plusieurs coeff de "
                    f"frais généraux différents avant migration"
                )
            price_study.general_overhead = general_overhead[0]
            session.merge(price_study)
        for discount_data in edp["discounts"]:
            discount = PriceStudyDiscount(price_study=price_study)
            for key in ("description", "amount", "percentage", "type_"):
                setattr(discount, key, discount_data.get(key))
            discount.order = discount_data["`order`"]
            session.add(discount)
            session.flush()
        edp_ids.append(price_study.id)
    mark_changed(session)
    transaction.commit()
    transaction.begin()
    session = db()
    request.dbsession = session
    for price_study_id in edp_ids:
        p: PriceStudy = PriceStudy.get(price_study_id)
        p.sync_amounts(sync_down=True)
        p.sync_with_task(request)
    mark_changed(session)
    logger.info("Les devis suivants ont été créés")
    logger.info(devis_ids)
    if untreated:
        for edp in untreated:
            logger.warn(
                f"Une edp n'a pas pu être restaurée, il manque le projet, "
                f"l'enseigne ou plus probablement le projet {edp['project_id']} n'a "
                f"pas de client "
                f"récupérer le json ci-dessous, ajoutez un client au projet et relancez le "
                f"script avec uniquement ces données "
            )
        logger.info(json.dumps(untreated))


def run_notify_on_existing(args, env):
    from caerp.models.activity import Activity
    import datetime
    from caerp.utils.notification import (
        notify_activity_participants,
        notify_career_path_end_date,
    )
    from caerp.models.career_path import CareerPath

    data_type = get_value(args, "type", ["activity", "userdatas"])

    if "activity" in data_type:
        now = datetime.datetime.now()
        activities = Activity.query().filter(
            Activity.datetime >= now, Activity.status == "planned"
        )
        for activity in activities:
            notify_activity_participants(request=env["request"], activity=activity)

    if "userdatas" in data_type:
        today = datetime.date.today()
        for c in (
            CareerPath.query()
            .filter(CareerPath.end_date != None)
            .filter(CareerPath.end_date > today)
        ):
            if c.stage_type in ("contract", "amendment", "entry") and c.userdatas:
                notify_career_path_end_date(env["request"], c.userdatas.user, c)


def custom_entry_point():
    """Script custom utilisé en production avant/après migration

    Usage:
        caerp-custom <config_uri> load_edp_from_json [--filepath=<filepath>]
        caerp-custom <config_uri> run_notify_on_existing [--type=<type>]

    o load_edp_from_json : Charge des edps depuis un fichier json
    o run_notify_on_existing : Génère des notifications pour les éléments existants

    Options:
        -h --help               Show this screen
        --filepath=<filepath>   Chemin vers le fichier à importer
        --type=<type>           Type d'activité à notifier (activity / userdatas)
    """

    def callback(arguments, env):
        if arguments["load_edp_from_json"]:
            func = load_edp_from_json_command
        elif arguments["run_notify_on_existing"]:
            func = run_notify_on_existing
        return func(arguments, env)

    try:
        return command(callback, custom_entry_point.__doc__)
    finally:
        pass
