# Contributing

To contribute to the project, you will have to follow this procedure:

## 1. Clone the repository

`git clone git@gitlab.in2p3.fr:fbi-data/omero-quay.git`

## 2. Create a new branch from the "dev" branch

Open a console then type the following lines:

```
git checkout dev
git branch new_branch
git checkout new_branch
git push --set-upstream origin new_branch
```

## 3. Install pre-commit to be able to stick to the syntaxic conventions used by the team

Install pre-commit : `pip install pre-commit`

For more information about pre-commit, see the GitHub
[repository](https://github.com/pre-commit/pre-commit) and the
[pre-commit website](https://pre-commit.com/) For more information about the
hooks, see the ".pre-commit-config.yaml" file.

## 4. Start coding

It depends on what do you want to do. If you are to make a file parser or
converter, try to make a mock-up on fake/test data you can test individually
first. Create a dedicated directory in the tests directory. If you are making
modifications on OMERO (OMERO webapp or modifications of webapp configurations,
or other website modifications), use the testing environment in tests/containers:

```
cd ./tests/containers

# Launch docker environment
./up.sh --web

# Create omero users
docker exec omero-server /opt/omero/server/miniforge3/envs/quay/bin/python \
  /opt/omero/server/omero-quay/tests/containers/create_users.py

# Get the logs contents in real execution time:
docker compose logs -f omero-server
# or
docker compose logs -f omero-web

# Shutdown containers
./up.sh --down

# Purge docker environment, including
# images and volumes
./up.sh --purge
```

If you made any modification to the `quay` binary itself (ex: adding new dependencies ),
you will need to generate custom docker images.

By default, docker pull the default images tagged `dev` in our docker registry. To generate
custom local images, in `tests/containers` :

```
echo "TAG=local" >> .env
docker compose build <YOUR_SERVICES>
./up.sh
```

## 5. Push your modifications

To commit and push your changes, in your new branch :

```
git add *
git commit -m "Type your commentary about your modifs here"
git push
```

## 6. Current unitary tests policy

Still unclear. Really depends on what you are trying to do. Try to get help from
an expert (a.k.a Guillaume Gay).
