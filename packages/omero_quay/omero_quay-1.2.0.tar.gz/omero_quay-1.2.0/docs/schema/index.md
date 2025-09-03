# manifset-schema

A linkML schema to describe bioimage file transfer between iRODS and OMERO

URI: https://w3id.org/omero-quay/manifest

Name: manifest-schema

## Classes

| Class                                                                                                                                     | Description                                                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [Error](Error.md)                                                                                                                         | If the state is errored, provides context of the error In python, message corresponds to exc_value, and details to the traceback  |
| [KVPair](KVPair.md)                                                                                                                       | None                                                                                                                              |
| [NamedThing](NamedThing.md)                                                                                                               | A generic grouping for any identifiable entity                                                                                    |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Collection](Collection.md)                                                               | A collection is equivalent to a directory in a unix file system. It can have sub-collections                                      |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Assay](Assay.md)                         | An assay is a collection of images and is the lower organisation level. Companion files will be added as file annotation in omero |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Investigation](Investigation.md)         | The top level collection in the hierarchy, equivalent to a Group in iRODS and OMERO                                               |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Study](Study.md)                         | A Study is a (potentially growing) collection of assays                                                                           |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[DataLink](DataLink.md)                                                                   | None                                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[File](File.md)                                                                           | None                                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Image](Image.md)                         | None                                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Manifest](Manifest.md)                                                                   | The root data entity                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[QuayAnnotation](QuayAnnotation.md)                                                       | None                                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CommentAnnotation](CommentAnnotation.md) | None                                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FileAnnotation](FileAnnotation.md)       | None                                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[MapAnnotation](MapAnnotation.md)         | In iRODS, there is an optional Unit, so key value pairs are really triples. For now this is not supported                         |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[TagAnnotation](TagAnnotation.md)         | None                                                                                                                              |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[User](User.md)                                                                           | Represents a user in the system - this user can log into iRODS and omero and samnba                                               |
| [State](State.md)                                                                                                                         | None                                                                                                                              |

## Slots

| Slot                                    | Description                                      |
| --------------------------------------- | ------------------------------------------------ |
| [ann_type](ann_type.md)                 |                                                  |
| [assays](assays.md)                     |                                                  |
| [children](children.md)                 |                                                  |
| [comment](comment.md)                   |                                                  |
| [content_type](content_type.md)         |                                                  |
| [creation_date](creation_date.md)       |                                                  |
| [datalinks](datalinks.md)               |                                                  |
| [delete](delete.md)                     |                                                  |
| [description](description.md)           |                                                  |
| [details](details.md)                   |                                                  |
| [email](email.md)                       |                                                  |
| [error](error.md)                       |                                                  |
| [file](file.md)                         |                                                  |
| [first_name](first_name.md)             |                                                  |
| [has_children](has_children.md)         |                                                  |
| [host](host.md)                         |                                                  |
| [id](id.md)                             |                                                  |
| [images](images.md)                     |                                                  |
| [importlink](importlink.md)             |                                                  |
| [institution](institution.md)           |                                                  |
| [investigations](investigations.md)     |                                                  |
| [irods_id](irods_id.md)                 |                                                  |
| [key](key.md)                           |                                                  |
| [kv_pairs](kv_pairs.md)                 |                                                  |
| [last_name](last_name.md)               |                                                  |
| [manager](manager.md)                   |                                                  |
| [members](members.md)                   |                                                  |
| [message](message.md)                   |                                                  |
| [MIMEType](MIMEType.md)                 |                                                  |
| [mode](mode.md)                         |                                                  |
| [name](name.md)                         |                                                  |
| [namespace](namespace.md)               |                                                  |
| [ome_id](ome_id.md)                     |                                                  |
| [owner](owner.md)                       |                                                  |
| [parents](parents.md)                   |                                                  |
| [password](password.md)                 |                                                  |
| [quay_annotations](quay_annotations.md) |                                                  |
| [role](role.md)                         |                                                  |
| [schema_version](schema_version.md)     |                                                  |
| [scheme](scheme.md)                     |                                                  |
| [srce_url](srce_url.md)                 | urls are intended to be parsed by python `urllib |
| [states](states.md)                     |                                                  |
| [status](status.md)                     |                                                  |
| [studies](studies.md)                   |                                                  |
| [timestamp](timestamp.md)               |                                                  |
| [trgt_url](trgt_url.md)                 | urls are intended to be parsed by python `urllib |
| [unix_gid](unix_gid.md)                 | group id that can be used in a unix system       |
| [unix_uid](unix_uid.md)                 | user id that can be used in a unix system        |
| [urls](urls.md)                         | urls are intended to be parsed by python `urllib |
| [value](value.md)                       |                                                  |

## Enumerations

| Enumeration           | Description                                                                      |
| --------------------- | -------------------------------------------------------------------------------- |
| [AnnType](AnnType.md) |                                                                                  |
| [Mode](Mode.md)       | access permission from an access control list see: https://docs                  |
| [Role](Role.md)       | User role for a collection (actually managed at the Investigation level) In m... |
| [Scheme](Scheme.md)   | A scheme refers to a data server type (iRODS, omero, a filesystem or an S3 se... |
| [Status](Status.md)   | Used to indicate up-to-dateness of a service with respect to a manifest          |

## Types

| Type                                    | Description                                                                      |
| --------------------------------------- | -------------------------------------------------------------------------------- |
| [Boolean](Boolean.md)                   | A binary (true or false) value                                                   |
| [Curie](Curie.md)                       | a compact URI                                                                    |
| [Date](Date.md)                         | a date (year, month and day) in an idealized calendar                            |
| [DateOrDatetime](DateOrDatetime.md)     | Either a date or a datetime                                                      |
| [Datetime](Datetime.md)                 | The combination of a date and time                                               |
| [Decimal](Decimal.md)                   | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md)                     | A real number that conforms to the xsd:double specification                      |
| [Float](Float.md)                       | A real number that conforms to the xsd:float specification                       |
| [Integer](Integer.md)                   | An integer                                                                       |
| [Jsonpath](Jsonpath.md)                 | A string encoding a JSON Path                                                    |
| [Jsonpointer](Jsonpointer.md)           | A string encoding a JSON Pointer                                                 |
| [Ncname](Ncname.md)                     | Prefix part of CURIE                                                             |
| [Nodeidentifier](Nodeidentifier.md)     | A URI, CURIE or BNODE that represents a node in a model                          |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model                            |
| [Sparqlpath](Sparqlpath.md)             | A string encoding a SPARQL Property Path                                         |
| [String](String.md)                     | A character string                                                               |
| [Time](Time.md)                         | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md)                           | a complete URI                                                                   |
| [Uriorcurie](Uriorcurie.md)             | a URI or a CURIE                                                                 |

## Subsets

| Subset | Description |
| ------ | ----------- |
