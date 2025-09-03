from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "0.2"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'https://w3id.org/omero-quay/manifest/',
     'description': 'A linkML schema to describe bioimage file transfer between '
                    'iRODS and OMERO',
     'id': 'https://w3id.org/omero-quay/manifest',
     'imports': ['linkml:types'],
     'license': 'GNU GPL v3.0',
     'name': 'manifest-schema',
     'prefixes': {'ORCID': {'prefix_prefix': 'ORCID',
                            'prefix_reference': 'https://orcid.org/'},
                  'biolink': {'prefix_prefix': 'biolink',
                              'prefix_reference': 'https://w3id.org/biolink/'},
                  'django': {'prefix_prefix': 'django',
                             'prefix_reference': 'https://docs.djangoproject.com/en/4.2/ref/contrib/auth/'},
                  'edam': {'prefix_prefix': 'edam',
                           'prefix_reference': 'https://edamontology.org/'},
                  'irods': {'prefix_prefix': 'irods',
                            'prefix_reference': 'https://docs.irods.org/latest/system_overview/glossary/#'},
                  'isa': {'prefix_prefix': 'isa',
                          'prefix_reference': 'https://isa-specs.readthedocs.io/en/latest/isamodel.html#'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'madbot': {'prefix_prefix': 'madbot',
                             'prefix_reference': 'https://gitlab.com/ifb-elixirfr/madbot/madbot-api/'},
                  'ome': {'prefix_prefix': 'ome',
                          'prefix_reference': 'https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html#'},
                  'quay': {'prefix_prefix': 'quay',
                           'prefix_reference': 'https://w3id.org/omero-quay/manifest'},
                  'ror': {'prefix_prefix': 'ror',
                          'prefix_reference': 'https://ror.readme.io/v2/docs/data-structure#'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'},
                  'wiki': {'prefix_prefix': 'wiki',
                           'prefix_reference': 'https://en.wikipedia.org/wiki/'}},
     'see_also': ['https://pypi.org/project/omero-cli-transfer/'],
     'source_file': 'src/omero_quay/schema/manifest-schema.yml',
     'title': 'manifset-schema'} )

class Mode(str, Enum):
    """
    access permission from an access control list see: https://docs.irods.org/4.3.0/icommands/user/#ichmod and https://omero.readthedocs.io/en/stable/sysadmins/\ server-permissions.html#administrator we use the OMERO default behavior of setting the permissions at the group / investigation level.
Below are the atomic permissions in iRODS and OMERO

  - own -> implicit in OMERO delete_object -> Delete write,
  - modify_object -> Edit, Move between groups, Mix data, Change
  - ownership create_object -> Edit delete_metadata -> Remove
  - annotations modify_metadata -> Annotate create_metadata ->
  - Annotate read, read_object -> View read_metadata -> View
  - null

From this (non-bijective) mapping, we reproduce the sets in OMERO, as described here https://omero.readthedocs.io/en/stable/sysadmins/\ server-permissions.html#administrator
    """
    private = "private"
    read_only = "read_only"
    read_annotate = "read_annotate"
    read_write = "read_write"


class Role(str, Enum):
    """
    User role for a collection (actually managed at the Investigation level) In madbot there are 4 roles, used here, but in Omero there are effectively only 2 (group owner and group member)
For now we map `owner` and `manager` to  group owner in omero, and `contributor` and `collaborator` to group members
[TO BE DEBATED]: if a group has only collaborators, we set the group to read_only if it has contibutors, we set it to read_annotate?
    """
    # A collection owner has read_write privileges on the collection Will have `own` ACLs in iRODS omero: group owner
    owner = "owner"
    # A collection manager has read_write privileges on the collection Will have 'delete_object' ACls in iRODS omero : group owner
    manager = "manager"
    # A collection contributor has read_write privileges on the collection Can't delete data in madbot Will have 'write' ACLs in iRODS omero : group member
    contributor = "contributor"
    # A collection contributor has read_write privileges on the collection Can't delete data in madbot Will have 'read' ACLs in iRODS omero : group member
    collaborator = "collaborator"


class AnnType(str, Enum):
    map_annotation = "map_annotation"
    tag_annotation = "tag_annotation"
    file_annotation = "file_annotation"
    comment_annotation = "comment_annotation"


class Scheme(str, Enum):
    """
    A scheme refers to a data server type (iRODS, omero, a filesystem or an S3 server)
    """
    irods = "irods"
    omero = "omero"
    file = "file"
    smb = "smb"
    xlsx = "xlsx"
    atk = "atk"


class Status(str, Enum):
    """
    Used to indicate up-to-dateness of a service with respect to a manifest.
started: The manifest is new
checked: The manifest is conform here and in the other services
changed: The manifest is conform here and must be pushed to peers
expired: The manifest needs to be processed here
errored: Well ...
    """
    started = "started"
    checked = "checked"
    changed = "changed"
    expired = "expired"
    errored = "errored"



class Thing(ConfiguredBaseModel):
    """
    A generic grouping for any identifiable entity
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Thing',
         'from_schema': 'https://w3id.org/omero-quay/manifest'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class NamedThing(Thing):
    """
    A generic grouping for an entity with foreign identities and a description not for thin objects as states
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'https://w3id.org/omero-quay/manifest'})

    name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class User(NamedThing):
    """
    Represents a user in the system - this user can log into iRODS and omero and samnba
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Person',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:Experimenter', 'schema:Person', 'irods:user-name'],
         'slot_usage': {'email': {'name': 'email',
                                  'pattern': '^\\S+@[\\S+\\.]+\\S+',
                                  'required': True},
                        'first_name': {'name': 'first_name', 'required': True},
                        'last_name': {'name': 'last_name', 'required': True},
                        'name': {'name': 'name', 'required': True}}})

    email: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'email',
         'aliases': ['ome:email', 'django:email'],
         'domain_of': ['User']} })
    first_name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'first_name',
         'aliases': ['django:first_name', 'ome:first_name'],
         'domain_of': ['User']} })
    last_name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'last_name',
         'aliases': ['ome:last_name', 'django:last_name'],
         'domain_of': ['User']} })
    role: Optional[Role] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'role', 'domain_of': ['User']} })
    institutions: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'institutions', 'domain_of': ['User']} })
    password: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'password', 'domain_of': ['User']} })
    unix_uid: Optional[int] = Field(default=None, description="""user id that can be used in a unix system""", json_schema_extra = { "linkml_meta": {'alias': 'unix_uid', 'domain_of': ['User'], 'slot_uri': 'schema:identifier'} })
    unix_gid: Optional[int] = Field(default=None, description="""group id that can be used in a unix system""", json_schema_extra = { "linkml_meta": {'alias': 'unix_gid', 'domain_of': ['User'], 'slot_uri': 'schema:identifier'} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })

    @field_validator('email')
    def pattern_email(cls, v):
        pattern=re.compile(r"^\S+@[\S+\.]+\S+")
        if isinstance(v,list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid email format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid email format: {v}")
        return v


class Provenance(Thing):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/omero-quay/manifest'})

    ror_ids: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'ror_ids', 'domain_of': ['Provenance'], 'slot_uri': 'ror:id'} })
    host: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'host', 'domain_of': ['Provenance', 'Store', 'State']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    stores: Optional[list[Store]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'stores', 'domain_of': ['Provenance']} })
    route: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'route', 'domain_of': ['Provenance', 'Manifest']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class Store(Thing):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/omero-quay/manifest'})

    scheme: Optional[Scheme] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'scheme', 'domain_of': ['Store', 'State']} })
    host: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'host', 'domain_of': ['Provenance', 'Store', 'State']} })
    resc: Optional[str] = Field(default=None, description="""iRODS resource where the investigations should be stored""", json_schema_extra = { "linkml_meta": {'alias': 'resc', 'domain_of': ['Store'], 'slot_uri': 'irods:Resource'} })
    data_roots: Optional[list[str]] = Field(default_factory=list, description="""Each data root is constructed as a url and MUST point to a directory or collection common to all datasets. We can use jinja templates to indicate variables
  - file:///mnt/SHARE
  - irods:///devZone/home/{{ user }}
  - nfs_mount:///mnt/buffers/""", json_schema_extra = { "linkml_meta": {'alias': 'data_roots', 'domain_of': ['Store']} })
    is_isa: Optional[bool] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'is_isa', 'domain_of': ['Store']} })
    post_url: Optional[str] = Field(default=None, description="""if the host has an omero-quay tornado server listening this is the url  to post to""", json_schema_extra = { "linkml_meta": {'alias': 'post_url', 'domain_of': ['Store']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class DataLink(Thing):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/omero-quay/manifest'})

    owner: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['DataLink', 'Collection', 'File']} })
    srce_url: Optional[str] = Field(default=None, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'srce_url', 'domain_of': ['DataLink']} })
    trgt_url: Optional[str] = Field(default=None, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'trgt_url', 'domain_of': ['DataLink']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class State(Thing):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/omero-quay/manifest'})

    store: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'store', 'domain_of': ['State']} })
    status: Optional[Status] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'status', 'domain_of': ['State']} })
    timestamps: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'timestamps', 'domain_of': ['State', 'Manifest']} })
    scheme: Optional[Scheme] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'scheme', 'domain_of': ['Store', 'State']} })
    host: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'host', 'domain_of': ['Provenance', 'Store', 'State']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class Error(ConfiguredBaseModel):
    """
    If the state is errored, provides context of the error In python, message corresponds to exc_value, and details to the traceback
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/omero-quay/manifest'})

    message: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'message', 'domain_of': ['Error']} })
    details: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'details', 'domain_of': ['Error']} })


class Collection(NamedThing):
    """
    A collection is equivalent to a directory in a unix file system. It can have sub-collections
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'irods:Collection',
         'from_schema': 'https://w3id.org/omero-quay/manifest'})

    owner: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['DataLink', 'Collection', 'File']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    parents: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'parents', 'domain_of': ['Collection', 'File']} })
    datalinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'datalinks', 'domain_of': ['Collection']} })
    importlinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'importlinks', 'domain_of': ['Collection']} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    children: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'children', 'domain_of': ['Collection']} })
    name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class Manifest(NamedThing):
    """
    The root data entity
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/omero-quay/manifest',
         'slot_usage': {'assays': {'inlined_as_list': True, 'name': 'assays'},
                        'images': {'inlined_as_list': True, 'name': 'images'},
                        'investigations': {'inlined_as_list': True,
                                           'name': 'investigations'},
                        'quay_annotations': {'inlined_as_list': True,
                                             'name': 'quay_annotations'},
                        'route': {'inlined_as_list': True, 'name': 'route'},
                        'studies': {'inlined_as_list': True, 'name': 'studies'}},
         'tree_root': True})

    provenance: Optional[Provenance] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'provenance', 'domain_of': ['Manifest']} })
    destination: Optional[Provenance] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'destination', 'domain_of': ['Manifest']} })
    route: Optional[list[Store]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'route', 'domain_of': ['Provenance', 'Manifest']} })
    manager: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'manager', 'domain_of': ['Manifest']} })
    members: Optional[list[User]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'members',
         'aliases': ['ome:experimenter_ref'],
         'domain_of': ['Manifest']} })
    investigations: Optional[list[Investigation]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'investigations',
         'domain_of': ['Manifest'],
         'mappings': ['ome:experimenter_group_ref']} })
    studies: Optional[list[Study]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'studies', 'domain_of': ['Manifest'], 'mappings': ['ome:project_ref']} })
    assays: Optional[list[Assay]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'assays', 'domain_of': ['Manifest'], 'mappings': ['ome:dataset_ref']} })
    images: Optional[list[Image]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'images',
         'domain_of': ['Manifest', 'Assay'],
         'mappings': ['ome:image_ref']} })
    quay_annotations: Optional[list[Union[CommentAnnotation, FileAnnotation, MapAnnotation, TagAnnotation]]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    error: Optional[Error] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'error', 'domain_of': ['Manifest']} })
    step: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'alias': 'step', 'domain_of': ['Manifest'], 'ifabsent': '0'} })
    states: Optional[list[State]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'states', 'domain_of': ['Manifest']} })
    schema_version: Optional[str] = Field(default="1.1", json_schema_extra = { "linkml_meta": {'alias': 'schema_version',
         'domain_of': ['Manifest'],
         'ifabsent': 'string("1.1")'} })
    timestamps: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'timestamps', 'domain_of': ['State', 'Manifest']} })
    name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class Investigation(Collection):
    """
    The top level collection in the hierarchy, equivalent to a Group in iRODS and OMERO
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'isa:Investigation',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:ExperimenterGroup',
                             'isa:Investigation',
                             'madbot:Investigation',
                             'irods:Collection'],
         'slot_usage': {'children': {'name': 'children', 'range': 'Study'}}})

    owners: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'owners', 'domain_of': ['Investigation']} })
    contributors: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'contributors', 'domain_of': ['Investigation']} })
    collaborators: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'collaborators', 'domain_of': ['Investigation']} })
    mode: Optional[Mode] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'mode', 'domain_of': ['Investigation']} })
    owner: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['DataLink', 'Collection', 'File']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    parents: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'parents', 'domain_of': ['Collection', 'File']} })
    datalinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'datalinks', 'domain_of': ['Collection']} })
    importlinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'importlinks', 'domain_of': ['Collection']} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    children: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'children', 'domain_of': ['Collection']} })
    name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class Study(Collection):
    """
    A Study is a (potentially growing) collection of assays
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'biolink:Study',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:Project',
                             'isa:Study',
                             'madbot:Study',
                             'irods:Collection'],
         'slot_usage': {'children': {'name': 'children', 'range': 'Assay'},
                        'parents': {'name': 'parents', 'range': 'Investigation'}}})

    owner: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['DataLink', 'Collection', 'File']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    parents: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'parents', 'domain_of': ['Collection', 'File']} })
    datalinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'datalinks', 'domain_of': ['Collection']} })
    importlinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'importlinks', 'domain_of': ['Collection']} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    children: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'children', 'domain_of': ['Collection']} })
    name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class Assay(Collection):
    """
    An assay is a collection of images and is the lower organisation level. Companion files will be added as file annotation in omero
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'ome:Dataset',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:Dataset',
                             'biolink:Assay',
                             'isa:Assay',
                             'irods:Collection'],
         'slot_usage': {'children': {'name': 'children', 'range': 'File'},
                        'parents': {'name': 'parents', 'range': 'Study'}}})

    images: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'images',
         'domain_of': ['Manifest', 'Assay'],
         'mappings': ['ome:image_ref']} })
    owner: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['DataLink', 'Collection', 'File']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    parents: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'parents', 'domain_of': ['Collection', 'File']} })
    datalinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'datalinks', 'domain_of': ['Collection']} })
    importlinks: Optional[list[DataLink]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'importlinks', 'domain_of': ['Collection']} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    children: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'children', 'domain_of': ['Collection']} })
    name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class QuayAnnotation(Thing):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'class_uri': 'ome:Annotation',
         'from_schema': 'https://w3id.org/omero-quay/manifest'})

    ann_type: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ann_type', 'domain_of': ['QuayAnnotation', 'FileAnnotation']} })
    namespace: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'namespace', 'domain_of': ['QuayAnnotation']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    kv_pairs: Optional[list[KVPair]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'kv_pairs', 'domain_of': ['QuayAnnotation', 'MapAnnotation']} })
    value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['QuayAnnotation',
                       'TagAnnotation',
                       'CommentAnnotation',
                       'KVPair']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class FileAnnotation(QuayAnnotation):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'ome:FileAnnotation',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:FileAnnotation', 'irods:data_object'],
         'slot_usage': {'ann_type': {'ifabsent': 'string(file_annotation)',
                                     'name': 'ann_type'}}})

    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    ann_type: Optional[str] = Field(default="file_annotation", json_schema_extra = { "linkml_meta": {'alias': 'ann_type',
         'domain_of': ['QuayAnnotation', 'FileAnnotation'],
         'ifabsent': 'string(file_annotation)'} })
    namespace: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'namespace', 'domain_of': ['QuayAnnotation']} })
    kv_pairs: Optional[list[KVPair]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'kv_pairs', 'domain_of': ['QuayAnnotation', 'MapAnnotation']} })
    value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['QuayAnnotation',
                       'TagAnnotation',
                       'CommentAnnotation',
                       'KVPair']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class MapAnnotation(QuayAnnotation):
    """
    In iRODS, there is an optional Unit, so key value pairs are really triples. For now this is not supported
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'ome:MapAnnotation',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:MapAnnotation', 'irods:Metadata'],
         'slot_usage': {'ann_type': {'ifabsent': 'string(map_annotation)',
                                     'name': 'ann_type'}}})

    kv_pairs: Optional[list[KVPair]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'kv_pairs', 'domain_of': ['QuayAnnotation', 'MapAnnotation']} })
    ann_type: Optional[str] = Field(default="map_annotation", json_schema_extra = { "linkml_meta": {'alias': 'ann_type',
         'domain_of': ['QuayAnnotation', 'FileAnnotation'],
         'ifabsent': 'string(map_annotation)'} })
    namespace: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'namespace', 'domain_of': ['QuayAnnotation']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['QuayAnnotation',
                       'TagAnnotation',
                       'CommentAnnotation',
                       'KVPair']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class TagAnnotation(QuayAnnotation):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'ome:TagAnnotation',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:TagAnnotation', 'irods:Metadata'],
         'slot_usage': {'ann_type': {'ifabsent': 'string(tag_annotation)',
                                     'name': 'ann_type'}}})

    value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['QuayAnnotation',
                       'TagAnnotation',
                       'CommentAnnotation',
                       'KVPair']} })
    ann_type: Optional[str] = Field(default="tag_annotation", json_schema_extra = { "linkml_meta": {'alias': 'ann_type',
         'domain_of': ['QuayAnnotation', 'FileAnnotation'],
         'ifabsent': 'string(tag_annotation)'} })
    namespace: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'namespace', 'domain_of': ['QuayAnnotation']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    kv_pairs: Optional[list[KVPair]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'kv_pairs', 'domain_of': ['QuayAnnotation', 'MapAnnotation']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class CommentAnnotation(QuayAnnotation):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'ome:CommentAnnotation',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:CommentAnnotation', 'irods:Metadata'],
         'slot_usage': {'ann_type': {'ifabsent': 'string(comment_annotation)',
                                     'name': 'ann_type'}}})

    value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['QuayAnnotation',
                       'TagAnnotation',
                       'CommentAnnotation',
                       'KVPair']} })
    ann_type: Optional[str] = Field(default="comment_annotation", json_schema_extra = { "linkml_meta": {'alias': 'ann_type',
         'domain_of': ['QuayAnnotation', 'FileAnnotation'],
         'ifabsent': 'string(comment_annotation)'} })
    namespace: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'namespace', 'domain_of': ['QuayAnnotation']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    kv_pairs: Optional[list[KVPair]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'kv_pairs', 'domain_of': ['QuayAnnotation', 'MapAnnotation']} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class File(NamedThing):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:File',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:BinaryFile', 'irods:data-object'],
         'slot_usage': {'name': {'description': 'The name here should be relative to '
                                                'the parent collection',
                                 'name': 'name'},
                        'parents': {'name': 'parents', 'range': 'Assay'}}})

    owner: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['DataLink', 'Collection', 'File']} })
    MIMEType: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'MIMEType', 'domain_of': ['File']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    parents: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'parents', 'domain_of': ['Collection', 'File']} })
    name: Optional[str] = Field(default=None, description="""The name here should be relative to the parent collection""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class Image(File):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'ome:Image',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['ome:Image', 'irods:data_object'],
         'slot_usage': {'parents': {'name': 'parents', 'range': 'Assay'}}})

    quay_annotations: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'quay_annotations',
         'any_of': [{'range': 'TagAnnotation'},
                    {'range': 'MapAnnotation'},
                    {'range': 'FileAnnotation'},
                    {'range': 'CommentAnnotation'}],
         'domain_of': ['NamedThing', 'Manifest', 'Image'],
         'mappings': ['ome:annotation_ref']} })
    owner: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['DataLink', 'Collection', 'File']} })
    MIMEType: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'MIMEType', 'domain_of': ['File']} })
    urls: Optional[list[str]] = Field(default_factory=list, description="""urls are intended to be parsed by python `urllib.parse.urlparse` method, and MUST be formatted accordingly, e.g:
  - https://my.file.server/path/to/file
  - ssh://user@my.file.server:path/to/file
  - irods:///irodsZone/home/group/path/to/file
  - file:///SHARE/data/group/path/to/file
File and irods paths MUST be absolute""", json_schema_extra = { "linkml_meta": {'alias': 'urls',
         'domain_of': ['Provenance',
                       'Collection',
                       'QuayAnnotation',
                       'FileAnnotation',
                       'File']} })
    parents: Optional[list[str]] = Field(default_factory=list, json_schema_extra = { "linkml_meta": {'alias': 'parents', 'domain_of': ['Collection', 'File']} })
    name: Optional[str] = Field(default=None, description="""The name here should be relative to the parent collection""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'aliases': ['ome:name', 'madbot:id', 'irods:name'],
         'domain_of': ['NamedThing']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'aliases': ['ome:description'],
         'domain_of': ['NamedThing']} })
    ome_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'ome_id',
         'domain_of': ['NamedThing'],
         'mappings': ['ome:id'],
         'slot_uri': 'schema:identifier'} })
    irods_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'irods_id',
         'domain_of': ['NamedThing'],
         'mappings': ['irods:id'],
         'slot_uri': 'schema:identifier'} })
    delete: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'alias': 'delete',
         'domain_of': ['NamedThing', 'Collection'],
         'ifabsent': 'False'} })
    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['Thing'], 'slot_uri': 'schema:identifier'} })


class KVPair(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'ome:Map_M',
         'from_schema': 'https://w3id.org/omero-quay/manifest',
         'narrow_mappings': ['schema:PropertyValue', 'irods:AVU']})

    key: str = Field(default=..., json_schema_extra = { "linkml_meta": {'alias': 'key', 'domain_of': ['KVPair'], 'slot_uri': 'ome:Map_Map_M_K'} })
    value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'value',
         'domain_of': ['QuayAnnotation',
                       'TagAnnotation',
                       'CommentAnnotation',
                       'KVPair']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Thing.model_rebuild()
NamedThing.model_rebuild()
User.model_rebuild()
Provenance.model_rebuild()
Store.model_rebuild()
DataLink.model_rebuild()
State.model_rebuild()
Error.model_rebuild()
Collection.model_rebuild()
Manifest.model_rebuild()
Investigation.model_rebuild()
Study.model_rebuild()
Assay.model_rebuild()
QuayAnnotation.model_rebuild()
FileAnnotation.model_rebuild()
MapAnnotation.model_rebuild()
TagAnnotation.model_rebuild()
CommentAnnotation.model_rebuild()
File.model_rebuild()
Image.model_rebuild()
KVPair.model_rebuild()
