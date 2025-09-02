# Copyright (c) IBM Corporation
# SPDX-License-Identifier: MIT

import typing

import pytest

from orchestrator.schema.entity import Entity
from orchestrator.schema.experiment import Experiment
from orchestrator.schema.property_value import PropertyValue
from orchestrator.schema.reference import ExperimentReference
from orchestrator.schema.result import InvalidMeasurementResult, ValidMeasurementResult


@pytest.fixture
def valid_measurement_result(property_values, entity) -> ValidMeasurementResult:

    return ValidMeasurementResult(
        entityIdentifier=entity.identifier, measurements=property_values
    )


@pytest.fixture
def invalid_measurement_result(property_values, entity) -> InvalidMeasurementResult:

    return InvalidMeasurementResult(
        entityIdentifier=entity.identifier,
        reason="Insufficient memory",
        experimentReference=ExperimentReference(
            experimentIdentifier="testexp", actuatorIdentifier="testact"
        ),
    )


@pytest.fixture
def valid_measurement_result_and_entity(
    entity_for_parameterized_experiment: typing.Tuple[Entity, Experiment],
) -> [Entity, ValidMeasurementResult]:

    import numpy as np

    test_entity, exp = entity_for_parameterized_experiment
    ref = exp.reference
    assert not test_entity.observedPropertiesFromExperimentReference(ref)

    # Add a result
    values = []
    for op in exp.observedProperties:
        values.append(PropertyValue(value=np.random.random(), property=op))

    return test_entity, ValidMeasurementResult(
        entityIdentifier=test_entity.identifier,
        measurements=values,
    )
