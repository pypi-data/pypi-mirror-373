---
status: published #Status can be draft, reviewed or published. 
---

## `operator` and `operation`

An `operator` is a code module that provides a capability to perform an `operation` on a `discoveryspace`.
For example the `RandomWalk` operator provides the capability to perform a random walk `operation` on a `discoveryspace`.

The `operator` defines the inputs arguments you can set for its `operations`.

The [operators](../operators/working-with-operators.md) section contains more details about the available `operators`, what they do and how to use them.
This page covers how you create and work with `operations` using a given `operator` in general.

## Creating an `operation` resource

### Pre-requisites

The only pre-requisite to creating an `operation` is that there is a suitable `discoveryspace` for it to work on.

### Getting input options and potential values

You can get a default input options for an operation along with a description of its fields by executing
```commandline
ado template operation --operator-name $OPERATOR_NAME --include-schema
```

In addition, check the [operator](../operators/working-with-operators.md) section for an entry for the particular $OPERATOR_NAME for more detail.

!!! info  end

    The `ado template operation` command will always output the latest arguments schema for the operator.
    So use this if the online documentation does not seem to work as it may have fallen behind. 

### The `operation` configuration YAML

The configuration for all `operations` has three top-level fields
```yaml
spaces: # This list of spaces to operate on
 - space_abc123
operation: 
  module: # Describes the operator to use - more below
    ...
  parameters: # The input arguments for this operation
actuatorConfigurationIdentifiers: # Optional
  - actuatorconfiguration-name-123
```

Each `operator` has different input arguments. As a result the fields under `operation.parameters` of every operation will be different. 
To get an initial set of parameter values, use one of the following methods

* Follow the previous section and use `ado template operation` 
* Check if there is an entry for the `operator` in the [operator](../operators/working-with-operators.md) section of the documentation website. 
* Check the [examples](../examples/examples.md) section to see if there is an example of using the given `operator`

For illustrative purposes here is a configuration for a random walk operation 

```YAML
spaces: ###The spaces to operate on
  - 'space-630588-bfebfe' 
operation: #The operators
  module: # The operator will be RandomWalk
    moduleClass: RandomWalk
    moduleName: orchestrator.modules.operators.randomwalk
  parameters: # The parameters for this RandomWalk operation
    numberIterations: 60
    batchSize: 1
    mode: 'sequential'
    samplerType: 'generator'
actuatorConfigurationIdentifiers:
  - actuatorconfiguration-st4sd-3cb3bb82
```

## Specifying the `operator`

The `operation.module` field sets the `operator` to use. For example above it was

```yaml
operation: #The operators
  module: # The operator will be RandomWalk
    moduleClass: RandomWalk
    moduleName: orchestrator.modules.operators.randomwalk
```

`operators` can be implemented in two ways - function or class - and how to specify them depends on which was used.
The documentation for the given operator (see [operators](../operators/working-with-operators.md)) should describe what to use. 
Here we just give a general overview.

For function operators the module field will look like
```yaml
module: 
  operationName: detect_anomalous_series # The name of the operation/operator
  operationType: characterize #The type of the operation/operator
```

The function operators fields are identical to the fields output by `ado describe operators`. 
`operationName` is given by the "OPERATOR" filed and "operationType" by the "Type" field. 
So to use any of these operators just fill in these fields appropriately. 

For class `operators` the module field will look like
```yaml
module:
    moduleClass: RandomWalk # The name of the class providing the operation
    moduleName: orchestrator.modules.operators.randomwalk # The module containing this class
```

!!! info  end

    Note im most cases the class method of specifying operators can be replaced by the function method,
    because most of the class operators have associated functions. 

### Passing actuator parameters

If you need to provide parameters to the actuators defined on the space, you can do it 
via the `actuatorConfigurationIdentifiers` field. 

For example, the below shows an operation specifying an actuator configuration for the `st4sd` actuator.
```yaml
spaces: ###The spaces to operate on
  - 'space-630588-bfebfe' 
operation: #The operators
  ... # The operation config
actuatorConfigurationIdentifiers:
  - actuatorconfiguration-st4sd-3cb3bb82
```

The actuator configurations provided must belong to one of the actuators defined on the space(s) operated on and only one actuator configuration can be provided for each actuator. 
Both these conditions are checked on creating the `operation` resource and an appropriate error message is output if they are not.

### Starting the operation

Executing
```commandline
ado create operation -f OPERATION.YAML
```
will create the `operation` resource in the active context and start performing whatever that operation does. 
Currently, the operation happens synchronously with this command i.e. it will not return until the operation is complete.

Before creating, and hence starting, the `operation`, the `parameters` will be validated with the `operator`. 
If they are not valid e.g. a required argument is missing, the `create` operation will fail with a relevant error. 

!!! info  end

    Although the `create` command does not execute until the operation is finished distributed users querying the
    same context will be able to see the created operation, from the moment it is created.

### `operation` resource specific fields

`operation` resources have some top-level fields in addition to common ones described [resources](resources.md#common-features-of-resources)

These are (with example values):

```yaml
operationType: characterize # The type of the operation: characterize, modify etc.
operatorIdentifier: profile-1.1 # The identifier of the operator including its version
result: ... # The result of the operation if any
```

For more on the result field see [getting operation output](#getting-operation-output).



## Getting `operation` output

An operation can create any type of ado resource.
To see the resources created by an operation use `ado show related operation`.
Note output that is text, tables or locations will be contained in `datacontainer` resource.

## `operation` status update events

In addition to the [status update events common to all resources](resources.md#resource-status) `operations`
define two more events: `started` and `finished`. 

The finished event also has a custom field `exit_state` which described how the operation finished.
It can be `success`, `fail` or `error`. 

Here is an example of the status field of an operation resource after it has completed
```yaml
created: '2024-12-19T10:54:42.015388Z'
identifier: raytune-0.7.5.dev10+g731d1e21.d20241218-ax-018647
kind: operation
metadata:
  entities_submitted: 11
  experiments_requested: 11
operationType: search
operatorIdentifier: raytune-0.7.5.dev10+g731d1e21.d20241218
status:
- event: created
  recorded_at: '2024-12-19T10:53:58.411745Z'
- event: added
  recorded_at: '2024-12-19T10:54:45.841908Z'
- event: started
  recorded_at: '2024-12-19T10:54:55.995781Z'
- event: finished
  exit_state: success
  recorded_at: '2024-12-19T10:55:21.429855Z'
- event: updated
  recorded_at: '2024-12-19T10:55:21.431450Z'
version: v1
```

## Deleting operations

!!!info
    Please note that [standard deletion constraints](resources.md#deleting-resources) apply 
    alongside the considerations discussed in this section.

!!!warning
    Deleting an operation that uses the replay actuator 
    **will also remove the original measurements from the database**, 
    making it impossible for it to be run again on the same sample store.
    

Deleting an operation is a destructive action that also removes associated data. 
The deletion process follows this logic:

- Requests associated with the operation are deleted if their results are not referenced by other operations
- Results are deleted **only if they are no longer referenced by any remaining requests**.

This means that if a measurement result has been reused (e.g., replayed) in another operation, it will not be deleted.

### Restrictions

By default, operations cannot be deleted while other operations are still running. 
This safeguard prevents potential consistency issues, such as deleting results that are 
actively being replayed in a running operation.

To override this restriction, you can use the [--force option](../getting-started/ado.md#ado-delete), 
which allows deletion even when other operations are in progress.
