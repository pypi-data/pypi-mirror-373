# Avro-Preprocessor

![avropreprocessor](avro.jpg)


This Python project provides a preprocessor for Avro resources. 

The preprocessor is made up of a list of modules.
Each module, in the specified order, performs an operation over the entire list of Avro resources. 

The input is a directory tree (namespace-like) in which each file is either a `domain_message`s or a `type`.

The output is another directory tree, with the same structure as input, in which Avro resources
underwent the list of preprocessing operations. 

Input Avro resources (`domain_message` or `type`) have `exavsc` as file extension.
NEW: they can also be `yaml` files with the same Avro extensions as `exavsc`!
You can even mix `exavsc` and `yaml` files if passed `-ie exavsc,yexavsc`.
Output Avro resources have `avsc` as file extension.

## Schema definition

Two different kinds of data structures are used in this project: *domain messages* and *types*.

#### Domain messages

Domain messages are Avro schemas that can be sent over a Kafka topic.
In general, multiple messages can be associated to each Kafka topic. 
Domain messages are placed in

`schema/com/example/message_schema/domain/<domain_context>/<record_name>`

#### Types

Types are reusable structures that can be referenced in a domain message.
They are placed in

`schema/com/example/message_schema/type/<typename>`

Domain messages *cannot* be reused (i.e. referenced by other domain messages).

### Naming rules 

- Directory structure must match the namespaces used inside the message / type definitions
- Records are defined in camel case
- Properties are defined in snake case

### Kafka topics and Avro subjects

Each directory `<domain_context>` under `schema/com/example/message_schema/domain/`
represents a Kafka topic. All schemas under a specific topic directory (and only them)
will be available to be sent on the corresponding Kafka topic, i.e. they will be registered
on the schema registry.

For subject naming we follow the guidelines defined by Confluent to 
[put several event types in the same Kafka topic](
https://www.confluent.io/blog/put-several-event-types-kafka-topic/); 
in particular we use the strategy 
`io.confluent.kafka.serializers.subject.TopicRecordNameStrategy`.

This behaviour is defined in `avro_naming.py`. 

##### Topic name
```
domain.<domain_context>
```

##### Avro subject names
```
domain.<domain_context>-<fully_qualified_record_name>
```

##### Example
For schema directory:
```
schema/com/example/message_schema/domain/user/
```

Topic name:
```
domain.user
```

List of Avro subjects names:
```
domain.user-com.example.message_schema.domain.user.UserCreated
domain.user-com.example.message_schema.domain.user.UserUpdated
domain.user-com.example.message_schema.domain.user.UserDeleted
```


## List of available preprocessing modules

The following modules should be applied in the order shown as follows.
However, they are all optional.

- `DocumentationCondenser`: JSON strings don't support multi lines inside an editor. This makes
it inconvenient to write long documentation for some fields. This module adds support for
lists as `doc` field in Avro schemas (they will be joined in the output). 
- `NamespaceChecker`: Checks if a resource namespace corresponds to the directory tree structure.
- `DocumentationChecker`: Checks if the documentation corresponds to specific rules:
    1. (sub) schemas with a "name" property MUST have a "doc" property.
    2. (sub) schemas without a "name" property MUST NOT have a "doc" property.
    3. If two (sub) schemas have the same "doc", they must be identical.
- `DefaultValueNullChecker`: Makes sure no default values other than null are used.
- `NamespaceChecker`: Checks if a resource namespace corresponds to the directory tree structure.
properties in `snake_case`.
- `AvroOrderChecker`: Check if the input schemas are sorted according to a fixed order 
(see `avro_sorter.py`). Fails if they are not.
- `MetadataAdder`: Adds the `Metadata` `type` (specified as argument on the command line) as first
field of every domain schema. Use the `--metadata-exclude` option to exclude a comma-separated list
of namespaces.
- `SchemaDependenciesChecker`: Calculates all resources dependencies and assert no cycles are present.
- `NullableOptionalExpander`: Allows for a compact definition of `nullable_optionals`
for "partial entity updates", see its specific section below.
- `LogicalTypeChecker`: Checks for correct usage of logicalType property.
- `ReferencesExpander`: While Apache's `avro-tools` is able to deal with references to other
resources in different files, Confluent's schema registry can only take one JSON as input, for 
each schema. Therefore, references to `type`s in a `domain_message` have to be expanded. 
But with a caveat:
only the first reference ("depth-first", NOT "breadth-first"!) *must* be expanded. All subsequent
references *must not* be expanded, i.e. they have to remain references. 
- `AvroSorter`: For the sake of readability and clearness, JSON fields of Avro resources are
rearranged according to a fixed order (see `avro_sorter.py`). 
- `KeysGenerator`: Generates Avro Schemas for Kafka Keys automatically for every topic based
on the `partition-field` property of schema fields.
- `SchemaMappingGenerator`: Outputs a JSON map `fully qualified schema -> kafka topic` to the file 
`schema-mapping.json`. It also gathers the field names having custom property
`partition-field` and writes them in `schema-mapping.json`. This is done so that Kafka producers
know which set of fields to hash to decide which kafka partition to send a message to.
This module also checks that partition keys are consistent within a given Kafka topic.
Furthermore, gathers the field names of `logicalType == user-id-fields` and stores them in
`schema-mapping.json`. These are meant to be those fields related to users so that they
can be indexed separately (e.g. for GDPR.)
- `DeprecationMappingGenerator`: Outputs a JSON map with info about deprecated schemas/fields to the file 
`deprecation-mapping.json`. This is later used for code generation. Also removes "deprecated" and
"deprecated-symbols" properties from the final schemas.
- `JavaClassesCreator`: Creates Java classes using Apache's `avro-tools`. It is also a very 
convenient way to check correctness of Avro resources.
- `SchemaRegistryChecker`: Check if a schema is compatible with the latest version of the 
same schema in the Schema registry.
- `SchemaRegistrar`: Register an Avro resources (both `domain_message`s AND `type`s!)
for the appropriate
Kafka topic in the schema registry. `type`s are registered for a dummy topic so that we can
check compatibility for them as well (it would not be possible otherwise).
See the documentation in `schema_registrar.py` for further documentation of `subject` 
naming and topics.
Autogenerated keys or the generic key for all schemas (`-k` option from the command line) are
registered as well.


### Installation
```bash
pip install avro-preprocessor
```

### Example Usage

Download Avro tools JAR
```bash
sh download_avro-tools.sh
```

For help:
```bash
avropreprocessor.py -h
```

It is possible to define the `key_subject_name_strategy` with the `-ksns` switch.
Possible values are`RecordNameStrategy` and `TopicRecordNameStrategy` (default).
Only relevant if the `SchemaRegistryChecker` and/or `SchemaRegistrar` modules are active as well.

All modules usage
```bash
avropreprocessor.py -i schema/ -o extended-schema/ -v -s 'http://localhost:8081' -t com.jaumo.message_schema.type -d com.jaumo.message_schema.type.Metadata -p schema-mapping.json -ie 'exavsc' -a ./avro-tools-1.9.0.jar
```

No java classes, no schema registry
```bash
avropreprocessor.py -i schema/ -o build/schema/ -v -s 'http://localhost:8081' -t com.jaumo.message_schema.type -d com.jaumo.message_schema.type.Metadata -p build/schema-mapping.json -m DocumentationCondenser NamespaceChecker DocumentationChecker DefaultValueNullChecker NamesChecker AvroOrderChecker MetadataAdder SchemaDependenciesChecker NullableOptionalExpander ReferencesExpander AvroSorter SchemaMappingGenerator DeprecationMappingGenerator SchemaRegistryChecker
```

Only register to the schema registry
```bash
avropreprocessor.py -i build/schema/ -o /tmp/ -v -s 'http://localhost:8081' -t com.jaumo.message_schema.type -ie 'avsc' -m SchemaRegistryChecker SchemaRegistrar
```

Reorder the *input* schemas according to the order defined in `sort_avro.py`
```bash
avropreprocessor.py -i schema/ -o schema/ -v -t com.jaumo.message_schema.type -ie 'exavsc' -oe 'exavsc' -m AvroSorter
```

Convert input schemas from `exavsc` to `yaml`
```bash
avropreprocessor.py -i schema/ -o schema_yaml/ -v -t com.jaumo.message_schema.type -ie 'exavsc' -oe 'yexavsc' -if 'json' -of 'yaml' -m DocumentationCondenser
```

Then use the yaml schemas as input
```bash
avropreprocessor.py -i schema_yaml/ -o build/schema/ -ie 'yexavsc' -if 'yaml' ...
```

## `nullable_optional`s: a convenient solution to the `Set-as-null` and `null-because-not-present` issue

As `protobuf`, `avro` does not distinguish between these two cases, 
unless some sort of wrapper is used.
The simple solution is to send the entire content of an event every time 
(i.e. always complete updates, never partial updates).

However, since partial updates can still be useful, the module `NullableOptionalExpander` automatises 
the following process. Let's consider a simple Avro schema for user updates:

```json
{
    "namespace": "com.jaumo",
    "type": "record",
    "name": "UserUpdate",
    "doc": "Update user event",
    "fields": [
        {
            "name": "id",
            "doc": "The id",
            "type": "int"
        },
        {
            "name": "name",
            "doc": "The name of the user",
            "type": "string"
        },
        {
            "name": "age",
            "doc": "The age of the user",
            "type": "int"
        },
        {
            "name": "email",
            "doc": "The email of the user",
            "type": "string"
        }
    ]
}
```

This schema does not support `null` values at all. In `avro`, they can be supported as follows:

```json
{
    "namespace": "com.jaumo",
    "type": "record",
    "name": "UserUpdate",
    "doc": "Update user event",
    "fields": [
        {
            "name": "id",
            "doc": "The id",
            "type": "int"
        },
        {
            "name": "name",
            "doc": "The name of the user",
            "type": ["null", "string"],
            "default": null
        },
        {
            "name": "age",
            "doc": "The age of the user",
            "type": ["null", "int"],
            "default": null
        },
        {
            "name": "email",
            "doc": "The email of the user",
            "type": ["null", "string"],
            "default": null
        }
    ]
}
```

With the schema above, both `set-as-null` and `null-because-not-present` are just null,
so they are still ambiguous. To distinguish them, we can wrap around a record type 
(which in Java will be a specific class). Showing the `email` property only, this would be

```json
{
    "name": "email",
    "doc": "The email of the user",
    "default": null,
    "type": [
        "null",
        {
            "name": "OptionalString",
            "type": "record",
            "fields": [
                {
                    "name": "value",
                    "default": null,
                    "type": [
                        "null",
                        "string"
                    ]
                }
            ]
        }
    ]
}
```

Note how the name of the wrapper record (`"OptionalString"`, above)
comes from the prefix `Optional` and the capitalised version of the Avro type field (`string`).
The name of the inner property is always `"value"` (this is done automatically, see below).

Now we have three cases
- `email` set to null means `null-because-not-present`
- `email.value` set to null means `set-as-null`
- `email.value` set to string

Since there's a lot of boilerplate and thus this is error-prone, the `nullable_optional` 
is simple extension to the Avro syntax that adds the property `"nullable_optional": true`. 
If a field has this property set to 
`true`, the field is expanded with its wrapper. The schema above then becomes:

```json
{
    "name": "email",
    "doc": "The email of the user",
    "nullable_optional": true,
    "type": "string"
}
``` 

and it is saved to a `.exavsc` file.

Note how this step is completely **language independent**: its output is a 
completely standard Avro schema that can be used by any library or framework. 
