# Copyright (c) IBM Corporation
# SPDX-License-Identifier: MIT

import asyncio
import enum
import logging
import typing
import uuid
from builtins import anext
from queue import Empty, Queue
from typing import AsyncGenerator, Literal, Optional, Union

import pydantic
import ray

from orchestrator.core.discoveryspace.group_samplers import (
    ExplicitEntitySpaceGroupedGridSampleGenerator,
    RandomGroupSampleSelector,
    SequentialGroupSampleSelector,
)
from orchestrator.core.discoveryspace.samplers import (
    ExplicitEntitySpaceGridSampleGenerator,
    RandomSampleSelector,
    SamplerTypeEnum,
    SequentialSampleSelector,
    WalkModeEnum,
)
from orchestrator.core.discoveryspace.space import DiscoverySpace
from orchestrator.core.operation.config import (
    DiscoveryOperationEnum,
    FunctionOperationInfo,
)
from orchestrator.core.operation.operation import OperationOutput
from orchestrator.modules.actuators.base import ActuatorBase
from orchestrator.modules.operators.base import Characterize, measure_or_replay_async
from orchestrator.modules.operators.collections import explore_operation
from orchestrator.modules.operators.discovery_space_manager import DiscoverySpaceManager
from orchestrator.modules.operators.orchestrate import (
    explore_operation_function_wrapper,
)
from orchestrator.schema.entity import Entity
from orchestrator.schema.measurementspace import MeasurementSpace
from orchestrator.schema.request import MeasurementRequest, MeasurementRequestStateEnum
from orchestrator.utilities.environment import enable_ray_actor_coverage
from orchestrator.utilities.logging import configure_logging
from orchestrator.utilities.support import prepare_dependent_experiment_input

if typing.TYPE_CHECKING:
    from orchestrator.schema.entityspace import EntitySpaceRepresentation

import sys

if sys.stdout.isatty() or sys.stderr.isatty():
    ENTITY = "\033[95m"
    EXPERIMENT = "\033[95m"
    SUMMARY = "\033[1;97m"
    SUBMIT = "\033[96m"
    COMPLETE = "\033[92m"
    REQUEST = "\033[96m"
    MAXED = "\033[93m"
    FAILED = "\033[91m"
    RESET = "\033[0m"
else:
    ENTITY = ""
    EXPERIMENT = ""
    SUMMARY = ""
    SUBMIT = ""
    COMPLETE = ""
    REQUEST = ""
    RESET = ""
    MAXED = ""
    FAILED = ""


class FilterModeEnum(enum.Enum):

    noFilter = "noFilter"
    measured = "measured"
    unmeasured = "unmeasured"
    partial = "partial"


class CombinedWalkModeEnum(enum.Enum):
    """Enum for flat and grouped walk variants

    It allows specifying the combination in one field rather than having to use two fields
    """

    RANDOM = "random"
    SEQUENTIAL = "sequential"
    RANDOMGROUPED = "randomgrouped"
    SEQUENTIALGROUPED = "sequentialgrouped"


class EntityFilter(pydantic.BaseModel):

    filterMode: FilterModeEnum = pydantic.Field(
        default=FilterModeEnum.noFilter, description="Filtering mode for entities"
    )

    def applyFilter(
        self,
        entity: Entity,
        measurementSpace: MeasurementSpace,
    ) -> bool:

        retval = True
        if self.filterMode != FilterModeEnum.noFilter:
            measurement_count = measurementSpace.numberExperimentsApplied(entity)
            if self.filterMode == FilterModeEnum.measured:
                # Check if all experiments in measurement space have values for entity
                retval = (
                    True
                    if measurement_count == len(measurementSpace.experiments)
                    else False
                )
            elif self.filterMode == FilterModeEnum.partial:
                # Check if more than one but less than all measurements
                retval = (
                    True
                    if (0 < measurement_count < len(measurementSpace.experiments))
                    else False
                )
            elif self.filterMode == FilterModeEnum.unmeasured:
                retval = True if measurement_count == 0 else False

        return retval


class RandomWalkParameters(pydantic.BaseModel):

    mode: Literal["random", "sequential", "randomgrouped", "sequentialgrouped"] = (
        pydantic.Field(
            default="random",
            description="How the walk should be performed: random, sequential, groupedrandom or groupedsequential",
        )
    )
    samplerType: Literal["selector", "generator"] = pydantic.Field(
        default="selector", description="The sampler to use"
    )
    grouping: list[str] = pydantic.Field(
        default=[],
        description="List of variable names that need to be grouped together",
    )
    numberEntities: Union[int, Literal["all"]] = pydantic.Field(
        default=1,
        description="Number of entities to sample or 'all' if you want to sample all and discoveryspace is finite. "
        "Note if discoveryspace is not-finite then specifying 'all' will raise an error at runtime",
    )
    batchSize: int = pydantic.Field(
        default=1,
        description="The number of concurrent experiments will be maintained at"
        " this value multiplied by the size of the measurement space",
    )
    singleMeasurement: bool = pydantic.Field(
        default=True,
        description="If True reuse existing measurements for an experiment",
    )
    maxRetries: int = pydantic.Field(
        default=0, description="The number of times to retry failed measurements"
    )
    filter: EntityFilter = pydantic.Field(
        default=EntityFilter(),
        description="Filter for entities. Only entities matching filter are considered "
        "sampled and sent for measurement. Default is noFilter",
    )

    model_config = pydantic.ConfigDict(extra="forbid")

    @pydantic.field_validator("batchSize")
    def validate_runtime_config(cls, value, values: "pydantic.FieldValidationInfo"):

        if values.data.get("numberEntities") != "all":
            assert values.data.get("numberEntities") >= value, (
                f'Number of entities to sample {values.data.get("numberEntities")} '
                f"cannot be less than batch size {value}"
            )
        if (
            values.data.get("mode") == CombinedWalkModeEnum.RANDOMGROUPED
            or values.data.get("mode") == CombinedWalkModeEnum.SEQUENTIALGROUPED
        ):
            assert len(values.data.get("grouping")) > 0, (
                f'grouping {values.data.get("grouping")} has to contain some names for the grouping '
                f'mode {values.data.get("mode")}'
            )

        return value


class RequestRetry(pydantic.BaseModel):

    measurementRequest: MeasurementRequest = pydantic.Field(
        description="The request being retried"
    )
    retries: int = pydantic.Field(
        default=0, description="Number of times it has been retried"
    )
    finalStatus: Optional[MeasurementRequestStateEnum] = pydantic.Field(
        default=None, description="The final status"
    )

    def __str__(self):

        return (
            f"Request {self.measurementRequest.requestid}. Entity: {self.measurementRequest.entities[0]}. "
            f"Experiment: {self.measurementRequest.experimentReference}. "
            f"Retried: {self.retries} times. Final status: {self.finalStatus}"
        )


@ray.remote
class RandomWalk(Characterize):
    """Performs a random walk through a set of known entities in a space"""

    @classmethod
    def defaultOperationParameters(
        cls,
    ) -> RandomWalkParameters:

        return RandomWalkParameters()

    @classmethod
    def validateOperationParameters(cls, parameters) -> RandomWalkParameters:

        return RandomWalkParameters.model_validate(parameters)

    @classmethod
    def description(cls):

        return """RandomWalk provides capabilities for sampling points in an entity space and applying
            measurements to them via a variety of walk and sampling filters.

            Walk types supported include fully random or sequential grid (if supported by entity space)
            with or without entities grouping. Sampling filters allow skipping points in the space according
            to various criteria e.g. not-measured, measured."""

    def __init__(
        self,
        operationActorName: str,
        namespace: str,
        state: DiscoverySpaceManager,
        actuators: dict[str, "ActuatorBase"],
        params=None,
    ):

        enable_ray_actor_coverage("random_walk")
        configure_logging()
        # waiting_for_debugger_if_local_mode()

        self.runid = str(uuid.uuid4())[:6]
        self.params = (
            RandomWalkParameters(**params)
            if params is not None
            else RandomWalkParameters()
        )
        self.log = logging.getLogger("RandomWalk")

        self.criticalError = False

        self.update_queue = asyncio.queues.Queue()
        self.actuators = actuators
        self._entitiesSampled = 0
        self._experimentsRequested = 0
        # Key is requestIndex, value is RequestRetry
        # IMPORTANT: We can map one request index/one retry as we know in RandomWalk
        # we only submit one entity per request -> we know only one MeasurementRequest will be created for each request
        # If this was not true we would need to use the entity id+requestIndex
        self._retriedExperimentRequests = {}  # type: dict[int, RequestRetry]

        try:
            self.mode = CombinedWalkModeEnum(self.params.mode)
        except ValueError:
            raise ValueError(
                "Unknown walk mode %s. Known modes %s"
                % (self.params.mode, [item.value for item in CombinedWalkModeEnum])
            )

        try:
            self.sampler = SamplerTypeEnum(self.params.samplerType)
        except ValueError:
            raise ValueError(
                "Unknown sampler type  %s. "
                "Known sampler types %s"
                % (
                    self.params.samplerType,
                    [item.value for item in SamplerTypeEnum],
                )
            )

        # Sets state, actorName ivars and subscribes to the state
        super().__init__(
            operationActorName=operationActorName,
            namespace=namespace,
            state=state,
            actuators=actuators,
        )

    def onUpdate(self, measurementRequest):

        self.update_queue.put_nowait(measurementRequest)

    def onCompleted(self):

        self.log.info("Completed")

    def onError(self, error: Exception):

        self.update_queue.put_nowait(error)

    async def run(self):

        self.log.debug(
            f"Starting random walk. Using sampler {self.sampler} with walk mode {self.mode}"
        )
        # noinspection PyUnresolvedReferences
        measurement_queue = await self.state.measurement_queue.remote()
        sampler = None
        match self.sampler:
            case SamplerTypeEnum.SELECTOR:
                match self.mode:
                    case CombinedWalkModeEnum.RANDOM:
                        sampler = RandomSampleSelector()
                    case CombinedWalkModeEnum.SEQUENTIAL:
                        sampler = SequentialSampleSelector()
                    case CombinedWalkModeEnum.RANDOMGROUPED:
                        sampler = RandomGroupSampleSelector(group=self.params.grouping)
                    case CombinedWalkModeEnum.SEQUENTIALGROUPED:
                        sampler = SequentialGroupSampleSelector(
                            group=self.params.grouping
                        )
                    case _:
                        # this can never happen, as we are validating this above
                        pass

            case SamplerTypeEnum.GENERATOR:
                match self.mode:
                    case CombinedWalkModeEnum.RANDOMGROUPED:
                        sampler = ExplicitEntitySpaceGroupedGridSampleGenerator(
                            mode=WalkModeEnum.RANDOM, group=self.params.grouping
                        )
                    case CombinedWalkModeEnum.SEQUENTIALGROUPED:
                        sampler = ExplicitEntitySpaceGroupedGridSampleGenerator(
                            mode=WalkModeEnum.SEQUENTIAL, group=self.params.grouping
                        )
                    case CombinedWalkModeEnum.RANDOM:
                        sampler = ExplicitEntitySpaceGridSampleGenerator(
                            mode=WalkModeEnum.RANDOM
                        )
                    case CombinedWalkModeEnum.SEQUENTIAL:
                        sampler = ExplicitEntitySpaceGridSampleGenerator(
                            mode=WalkModeEnum.SEQUENTIAL
                        )
                    case _:
                        # this can never happen, as we are validating this above
                        pass
            case _:
                # this can never happen, as we are validating this above
                pass

        if not sampler:
            raise ValueError(
                f"Could not identify sampler matching {self.sampler} and mode, {self.mode}"
            )

        iterator = await sampler.remoteEntityIterator(
            remoteDiscoverySpace=self.state, batchsize=1
        )

        # noinspection PyUnresolvedReferences
        ds = await self.state.discoverySpace.remote()  # type: DiscoverySpace

        measurement_space = ds.measurementSpace
        entity_space: Optional[None, "EntitySpaceRepresentation"] = ds.entitySpace

        #
        # Check and/or Determine numberOfEntities to sample
        #
        if self.params.numberEntities == "all":

            if entity_space is not None:
                if entity_space.isDiscreteSpace:
                    try:
                        number_entities = entity_space.size
                    except AttributeError:
                        # noinspection PyUnresolvedReferences
                        self.state.unsubscribeFromUpdates.remote(
                            subscriberName=self.actorName
                        )
                        raise ValueError(
                            "Cannot specify 'all' for number of entities to sample for space with unbounded dimensions"
                        )
                    else:
                        print(
                            f"'all' specified for number of entities to sample. "
                            f"This is {number_entities} entities - the size of the entity space"
                        )
                else:
                    # noinspection PyUnresolvedReferences
                    self.state.unsubscribeFromUpdates.remote(
                        subscriberName=self.actorName
                    )
                    raise ValueError(
                        "Cannot specify 'all' for number of entities to sample for non-discrete space"
                    )
            else:
                number_entities = ds.sample_store.numberOfEntities
                print(
                    f"'all' specified for number of entities to sample. "
                    f"This is {number_entities} entities - the number of entities in the sample store"
                )
        else:
            number_entities = self.params.numberEntities  # type: int

        if entity_space is not None and entity_space.isDiscreteSpace:
            try:
                size = entity_space.size
            except AttributeError:
                # No size - whatever numberEntities is, is fine
                pass
            else:
                if size < number_entities:
                    raise ValueError(
                        f"Requested number of entities to sample, {number_entities}, "
                        f"is greater than the space size {size} "
                    )
        elif entity_space is None:
            if ds.sample_store.numberOfEntities < number_entities:
                raise ValueError(
                    f"Requested number of entities to sample, {number_entities}, "
                    f"is greater than the number of entities in the sample store {ds.sample_store.numberOfEntities} "
                )

        print(
            f"Running random walk with sampler {self.sampler}, sample selector {self.mode} "
            f"for {number_entities} iterations"
        )

        #
        # Continuous batching:
        #
        # Below we control so each experiment requested has only one entity

        #
        # STEP ONE: Send Initial Batch
        #

        number_experiments = len(measurement_space.experiments)
        print(f"Submitting initial batch of size {self.params.batchSize} entities")
        print(
            f"There are {number_experiments} experiments in measurement space -"
            f" therefore there can be up to {self.params.batchSize*number_experiments} experiments running concurrently"
        )
        # Create batch
        self._entitiesSampled = 0
        while self._entitiesSampled < self.params.batchSize:
            try:
                passedFilter = False
                while passedFilter is False:
                    entities = await anext(iterator)
                    # We know there is only one entity as we set batch_size = 1 for all iterators
                    passedFilter = self.params.filter.applyFilter(
                        entities[0], measurement_space
                    )
            except (StopAsyncIteration, StopIteration):
                self.log.debug(
                    "Iterator raised iteration error - No more entities to add to initial batch"
                )
                print(
                    "Continuous batching: INITIAL BATCH: No entities left to add to initial batch "
                )
                break
            else:
                # Submit independent experiments for the entities
                self.log.debug(
                    f"Initial batch. Entity {self._entitiesSampled} is {entities[0].identifier}"
                )
                independent_experiments = measurement_space.independentExperiments
                for experiment in independent_experiments:
                    print(
                        f"Submitting experiment {EXPERIMENT}{experiment}{RESET} for {ENTITY}{entities[0].identifier}{RESET}"
                    )
                    experiment_identifiers = await measure_or_replay_async(
                        requestIndex=self._entitiesSampled,
                        requesterid=self.operationIdentifier(),
                        experimentReference=experiment.reference,
                        entities=entities,
                        actuators=self.actuators,
                        measurement_queue=measurement_queue,
                        memoize=self.params.singleMeasurement,
                    )

                    # This is for the number of experiments submitted in total
                    self._experimentsRequested += len(experiment_identifiers)

                    if len(experiment_identifiers) == 0:
                        self.log.warning(
                            f"No experiments submitted by actuators for entities {[e.identifier for e in entities]}. "
                            f"Will not wait"
                        )
                        print(
                            f"No experiments submitted by actuators for entity {[e.identifier for e in entities]}. "
                            f"Will not wait"
                        )

                self._entitiesSampled += 1

            print(
                "Initial batch. "
                "Total entities sampled %d. "
                "Experiments available per entity %d. "
                "Total experiment requests generated %d. "
                % (
                    self._entitiesSampled,
                    len(independent_experiments),
                    self._experimentsRequested,
                )
            )

        # STEP TWO: Continuous batching
        #
        # 2(a) wait for measurements to complete
        # 2(b) for each completion check does it allow a dependent calculation to start
        # 2(c) if it does launch it
        # 2(d) check if all experiments launched have completed.

        completed_experiments = 0  # experiments which are considered finished
        # The number of requests that have finished - it may take more than one request
        # to complete an experiment depending on retries
        finished_requests = 0
        waiting_on_requests = True if self._experimentsRequested > 0 else False
        continuous_batching_queue = Queue()
        while waiting_on_requests is True and not self.criticalError:
            print(
                f"\nContinuous batching: {SUMMARY}SUMMARY{RESET}. Entities sampled and submitted: {self._entitiesSampled}. "
                f"Experiments completed: {completed_experiments} "
                f"Waiting on {self._experimentsRequested - finished_requests} active requests. "
                f"There are {len(measurement_space.dependentExperiments)} dependent experiments"
            )

            # Wait for a finished measurement request or an error
            measurement_request = (
                await self.update_queue.get()
            )  # type: typing.Union[MeasurementRequest | Exception]
            if isinstance(measurement_request, Exception):
                self.criticalError = True
                self.log.critical(
                    "Received information on critical error will exit: %s"
                    % measurement_request
                )
                continue  # break back to while condition so it will exit

            print(
                f"Continuous Batching: {COMPLETE}EXPERIMENT COMPLETION{RESET}. Received finished notification for experiment "
                f"in measurement request in group {measurement_request.requestIndex}: {REQUEST}%s{RESET}"
                % (measurement_request,)
            )
            #  Only process experiments we submitted.
            if measurement_request.operation_id == self.operationIdentifier():
                finished_requests += 1

                # Process the finished measurement
                # If there are dependent experiments they will be added to the queue here
                # If the measurement is considered completed this will return True
                # otherwise if the measurement was resubmitted due to Failure this is not considered completed
                # and False will be returned
                completed = self._processCompletedMeasurement(
                    measurement_request,
                    measurement_space,
                    continuous_batching_queue,
                )

                completed_experiments += completed

                # If the queue is empty, add the next entity + experiments
                if (
                    continuous_batching_queue.empty()
                    and self._entitiesSampled < number_entities
                ):
                    # If there are no more entities to sample this does nothing
                    # This can happen if it's not possible to sample the requested number of entities
                    # due to, for example, filters removing many Entities from consideration
                    await self._sampleEntityAndAddMeasurementsToQueue(
                        continuous_batching_queue, iterator, measurement_space
                    )

                # Get the next experiment from the continuous batching queue and submit it
                # If there are no experiment to get this does nothing
                # This will update self._experimentsRequested
                await self._getAndSubmitMeasurement(
                    completed_experiments, continuous_batching_queue, measurement_queue
                )

            waiting_on_requests = finished_requests < self._experimentsRequested

        if len(self._retriedExperimentRequests) > 0:
            print(
                f"Summary of {len(self._retriedExperimentRequests)} retried experiments"
            )
            for key in self._retriedExperimentRequests:
                print(f"Request {key}: {self._retriedExperimentRequests[key]}")

        if not self.criticalError:
            print("All entities submitted and measurement requests complete. Exiting")
        else:
            print(
                f"Encountered critical error after submitting {self._experimentsRequested} measurements requests. "
                f"Was notified that {finished_requests} measurements had completed before error."
            )
        # noinspection PyUnresolvedReferences
        self.state.unsubscribeFromUpdates.remote(subscriberName=self.actorName)

    def _processCompletedMeasurement(
        self,
        measurementRequest: MeasurementRequest,
        measurementSpace: MeasurementSpace,
        continuousBatchingQueue: Queue,
    ) -> bool:

        if measurementRequest.status == MeasurementRequestStateEnum.SUCCESS:
            completed = True

            if measurementRequest.requestIndex in self._retriedExperimentRequests:
                self._retriedExperimentRequests[
                    measurementRequest.requestIndex
                ].finalStatus = MeasurementRequestStateEnum.SUCCESS

            for entity in measurementRequest.entities:
                self.log.debug(
                    "%s"
                    % [
                        "%s" % v
                        for v in entity.propertyValuesFromExperimentReference(
                            measurementRequest.experimentReference
                        )
                    ]
                )

            has_dependent_experiments = len(measurementSpace.dependentExperiments) > 0

            # If this experiment has dependent experiments add them to the queue
            if has_dependent_experiments:
                prepared_inputs = prepare_dependent_experiment_input(
                    measurement_request=measurementRequest,
                    measurement_space=measurementSpace,
                )

                for d in prepared_inputs:
                    continuousBatchingQueue.put(d._asdict())
        else:
            print(
                f"Continuous Batching: {FAILED}EXPERIMENT FAILURE{RESET}. Experiment request {REQUEST}{measurementRequest.requestid}{RESET} "
                f"with measurement request index {measurementRequest.requestIndex} failed"
            )

            if not self._retriedExperimentRequests.get(measurementRequest.requestIndex):
                self._retriedExperimentRequests[measurementRequest.requestIndex] = (
                    RequestRetry(measurementRequest=measurementRequest)
                )

            retry_tracker = self._retriedExperimentRequests[
                measurementRequest.requestIndex
            ]

            if retry_tracker.retries == self.params.maxRetries:
                print(
                    f"Continuous Batching: {MAXED}EXPERIMENT RETRY{RESET}. Max retries {self.params.maxRetries} "
                    f"reached for request {REQUEST}{measurementRequest.requestid}{RESET}"
                )
                retry_tracker.finalStatus = MeasurementRequestStateEnum.FAILED
                # It's completed as we are not trying again
                completed = True
            else:
                retry_tracker.retries += 1
                print(
                    f"Continuous Batching: {SUMMARY}EXPERIMENT COMPLETION{RESET}. Will retry request {REQUEST}{measurementRequest.requestIndex}{RESET}."
                    f" Retry attempt {self._retriedExperimentRequests[measurementRequest.requestIndex].retries} "
                    f"of {self.params.maxRetries}"
                )

                completed = False
                continuousBatchingQueue.put(
                    {
                        "entities": measurementRequest.entities,
                        "experimentReference": measurementRequest.experimentReference,
                        "requestIndex": measurementRequest.requestIndex,
                    }
                )

        return completed

    async def _getAndSubmitMeasurement(
        self, completedExperiments, continuousBatchingQueue, updateQueue
    ):
        """
        Gets an experiment+entity for continuousBatchingQueue and submits it

        Params
            completedExperiments: The number of completedExperiments. For logging
            continuousBatchingQueue: The queue instance to retrieve the next experiment+entity from
            measurement_queue: queue to pass to Actuator
        """

        try:
            next_experiment_and_entity = continuousBatchingQueue.get(block=False)
        except Empty:
            print(
                f"Continuous batching: {SUMMARY}GET EXPERIMENT{RESET}. No new experiments in queue. "
                f"Requests made: {self._experimentsRequested}. Experiments Completed: {completedExperiments}"
            )
        else:
            experiment_reference = next_experiment_and_entity["experimentReference"]
            entities = next_experiment_and_entity["entities"]
            request_index = next_experiment_and_entity["requestIndex"]
            print(
                f"Continuous batching: {SUBMIT}SUBMIT EXPERIMENT{RESET}. Submitting experiment {EXPERIMENT}{experiment_reference}{RESET} "
                f"for {ENTITY}{entities[0].identifier}{RESET}"
            )
            experiment_identifiers = await measure_or_replay_async(
                requestIndex=request_index,
                requesterid=self.operationIdentifier(),
                experimentReference=experiment_reference,
                entities=entities,
                actuators=self.actuators,
                measurement_queue=updateQueue,
                memoize=self.params.singleMeasurement,
            )

            self._experimentsRequested += len(experiment_identifiers)

    async def _sampleEntityAndAddMeasurementsToQueue(
        self,
        continuousBatchingQueue: Queue,
        iterator: AsyncGenerator[list[Entity], None],
        measurementSpace: MeasurementSpace,
    ) -> list[Entity]:
        """
        Samples an entity from the sampler and adds the requested measurements to the continuousBatchingQueue

        If there are no more entities to sample this method returns an empty list and no measurements are added
        to the queue

        Updates self._entitiesSampled

        Params:
            continuousBatchingQueue: A queue new measurements are added to
                As a dict with keys "entity", "experiment", "requestIndex"
            iterator: An iterator which returns Entities
            measurementSpace: The measurement space

        Returns:
            A list with 0 or 1 Entity instance.
        """
        try:
            passedFilter = False
            while passedFilter is False:
                entities = await anext(iterator)
                # We know there is only one entity as we set batch_size = 1 for all iterators
                passedFilter = self.params.filter.applyFilter(
                    entities[0], measurementSpace=measurementSpace
                )
        except (StopAsyncIteration, StopIteration):
            self.log.debug("No entities remaining - iterator raised StopIteration")
            entities = []
        else:
            # We know the batch size is one hence the 0
            self.log.debug(
                f"Continuous batching: {SUMMARY}ADD EXPERIMENT{RESET}. "
                f"Next entity (index {self._entitiesSampled}) is {ENTITY}{entities[0].identifier}{RESET}"
            )
            independent_experiments = measurementSpace.independentExperiments
            for experiment in independent_experiments:
                self.log.debug(
                    f"Continuous batching: {SUMMARY}ADD EXPERIMENT{RESET}. adding experiment {experiment} "
                    f"for {ENTITY}{entities[0].identifier}{RESET} to queue"
                )
                continuousBatchingQueue.put(
                    {
                        "entities": entities,
                        "experimentReference": experiment.reference,
                        "requestIndex": self._entitiesSampled,
                    }
                )

        self._entitiesSampled += len(entities)

        return entities

    def numberEntitiesSampled(self):

        return self._entitiesSampled

    def numberMeasurementsRequested(self):

        return self._experimentsRequested

    def operationIdentifier(self):

        return "%s-%s" % (self.__class__.operatorIdentifier(), self.runid)

    @classmethod
    def operatorIdentifier(cls):

        from importlib.metadata import version

        version = version("ado-core")

        return "randomwalk-%s" % version

    @classmethod
    def operationType(cls) -> DiscoveryOperationEnum:

        return DiscoveryOperationEnum.SEARCH


@explore_operation(
    name="random_walk",
    description=RandomWalk.description(),
    configuration_model=RandomWalkParameters,
    configuration_model_default=RandomWalkParameters(),
)
def random_walk(
    discoverySpace: DiscoverySpace,
    operationInfo: FunctionOperationInfo = FunctionOperationInfo(),
    **kwargs: typing.Dict,
) -> OperationOutput:
    """
    Performs a random_walk operation on a given discoverySpace

    """

    import uuid

    import orchestrator.modules.module

    module = orchestrator.core.operation.config.OperatorModuleConf(
        moduleName="orchestrator.modules.operators.randomwalk",
        moduleClass="RandomWalk",
        moduleType=orchestrator.modules.module.ModuleTypeEnum.OPERATION,
    )

    return explore_operation_function_wrapper(
        discovery_space=discoverySpace,
        module=module,
        parameters=kwargs,
        namespace=f"namespace-{str(uuid.uuid4())[:8]}",
        operation_info=operationInfo,
    )
