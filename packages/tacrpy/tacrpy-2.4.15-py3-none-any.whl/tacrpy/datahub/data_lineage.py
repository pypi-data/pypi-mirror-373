"""Soubor funkcí, které slouží k hromadnému vytváření podkladů k tvorbě a úpravě data lineage \
v DataHubu přes API."""


def _create_field_lineage(entity_urn: str, upstream_urn: str, field_dict: dict[str, str]) -> dict[str, any]:
    """ Vytvoří data lineage na úrovni dvou fieldů.

    :param entity_urn: URN datasetu, ve kterém je field, pro které tvoříme data lineage
    :param upstream_urn: URN datasetu, ve kterém je field, na který má vazbu (lineage)
    :param field_dict: informace a filed level lineage
    :return: dict s informacemi o vazbě mezi dvěma fieldy
    """

    field_upstream_name = field_dict['upstream_lineage_field']
    field_upstream_urn = f'urn:li:schemaField:({upstream_urn},{field_upstream_name})'
    field_upstream_type = field_dict['upstream_field_type']

    field_downstream_name = field_dict['downstream_lineage_field']
    field_downstream_urn = f'urn:li:schemaField:({entity_urn},{field_downstream_name})'
    field_downstream_type = field_dict['downstream_field_type']

    field_lineage = {
        'upstreamType': field_upstream_type,
        'upstreams': [
            field_upstream_urn
        ],
        'downstreamType': field_downstream_type,
        'downstreams': [
            field_downstream_urn
        ]
    }

    return field_lineage


def create_dataset_lineage(entity_name: str, platform: str, lineage_dict: dict[str, any]
                           , field_level: bool = False) -> dict[str, any]:
    """ Vytvoří data lineage (vazby) pro daný dataset.

    Umožňuje vytvářet data lineage na úrovni datasetů i na úrovni jednotlivých fieldů.

    :param entity_name: název datasetu, pro který se data lineage vytváří
    :param platform: název platformy, která je zdrojem datasetu
                     (např. etalon, googlesheets, ISTA, Postgres, OpenAPI...)
    :param lineage_dict: dict datasetu, který obsahuje jednotlivé vazby (na úrovni datasetů nebo na úrovni fieldů)
    :param field_level: informace, jestli obsahuje dataset lineage na úrovni fieldů
    :return: dict vazeb (data lineage) pro daný dataset
    """

    entity_urn = f'urn:li:dataset:(urn:li:dataPlatform:{platform},{entity_name},PROD)'

    upstreams = []
    field_lineages = []

    for key, value in lineage_dict.items():
        upstream_name = value['upstream_lineage_dataset']
        upstream_platform = value['upstream_platform']
        upstream_urn = f'urn:li:dataset:(urn:li:dataPlatform:{upstream_platform},{upstream_name},PROD)'
        upstream_type = value['upstream_dataset_type']

        upstream_dict = {
            'dataset': upstream_urn,
            'type': upstream_type
        }

        # pro field_lineage bude existovat více záznamů pro vazbu dvou datasetů, proto se "filtruje"
        if upstream_dict not in upstreams:
            upstreams.append(upstream_dict)

        if field_level:
            field_lineage = _create_field_lineage(entity_urn, upstream_urn, value)
            field_lineages.append(field_lineage)

    upstream_lineage = {
        "entityType": "dataset",
        "entityUrn": entity_urn,
        "aspect": {
            "__type": "UpstreamLineage",
            "upstreams": upstreams,
            "fineGrainedLineages": field_lineages
        }
      }

    return upstream_lineage

# TODO: rozdílné funkce na vytvoření nové data lineage a update stávající data lineage
