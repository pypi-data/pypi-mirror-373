def previous_transformation(cycle: dict, transformations: list, transformation: dict):
    # TODO: should find the transformation starting from the index of the current transformation going reverse
    tr_id = transformation.get('previousTransformationId')
    return next(
        (v for v in transformations if v.get('transformationId') == tr_id),
        cycle
    )
