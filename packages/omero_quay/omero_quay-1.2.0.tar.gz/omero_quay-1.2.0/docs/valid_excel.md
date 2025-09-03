# Excel validate

Write a `validate` function:

# Global

- [x] must be xlsx (checked at upload)
- [ ] sheet names `"User", "Investigation", "Study", "Assay"`

# User

- [ ] login must be present
- [ ] user login must exist in omero

Note: user are referred to by their login

# Investigation

- [ ] Must have a name
- [ ] No space in investigation name
- [ ] manager must be a valid user
- [ ] owners: at least one valid user
- [ ] contributors: zero or more valid users
- [ ] collaborators: zero or more valid users
- [ ] no shared users between owners, contributors and collaborators (**not**
      true for manager)
- [ ] samba path: must exist in the buffer machine (check with ssh), discuss
      with Theo

# Study

- [ ] Must have a valid owner
- [ ] Must have a name
- [ ] Must have valid parent investigation (name present in the "investigation"
      sheet)

# Assay

- [ ] Must have a valid owner
- [ ] assay owner must be owner or contributor in the parent investigation
- [ ] Path must exist as a subdir of the investigation in the buffer machine
- [ ] This is invalid:

  | path         | name   |
  | ------------ | ------ |
  | Dir1         | assay1 |
  | Dir1/SubDir1 | assay2 |

No assay path cannot be a subpath of another assay see `pathlib.Path`

- [ ] All the paths must be different
- [ ] parent must be a valid study (name in the Study sheet)
- [ ] Discuss: What K/V entries are required? (with Perrine)

Relevant https://omero.readthedocs.io/en/stable/developers/Python.html

https://gitlab.in2p3.fr/fbi-data/omero-quay/-/blob/dev/src/omero_quay/managers/omero.py?ref_type=heads
