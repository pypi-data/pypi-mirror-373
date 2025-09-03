""" """

from __future__ import annotations

import pytest

from omero_quay.managers.filesystem import FSManager
from omero_quay.managers.irods import iRODSManager
from omero_quay.managers.omero import OmeroManager

managers = {"irods": iRODSManager, "file": FSManager, "omero": OmeroManager}


class TestManager:
    scheme = "file"
    host = "localhost"

    @pytest.fixture
    def manager(self, fs_manifest, conf):
        with managers[self.scheme](
            conf=conf, manifest=fs_manifest, host=self.host
        ) as manager:
            yield manager

    def test_set_state(self, manager):
        if not manager:
            return
        current_state = manager.state
        assert current_state
        manager.set_state("changed")
        assert manager.manifest.states[-1].status == "changed"

    def test(self):
        pass

    def test_parse(self):
        pass

    def test_annotate(self):
        pass

    def test_transfer(self):
        pass

    def test_crud(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        pass


"""

From pytest documentation

# content of test_scenarios.py


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for scenario in metafunc.cls.scenarios:
        idlist.append(scenario[0])
        items = scenario[1].items()
        argnames = [x[0] for x in items]
        argvalues.append([x[1] for x in items])
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


scenario1 = ("basic", {"attribute": "value"})
scenario2 = ("advanced", {"attribute": "value2"})


class TestSampleWithScenarios:
    scenarios = [scenario1, scenario2]

    def test_demo1(self, attribute):
        assert isinstance(attribute, str)

    def test_demo2(self, attribute):
        assert isinstance(attribute, str)



  """


class TestiRODSManager(TestManager):
    scheme = "irods"

    @pytest.fixture
    def manager(self, irods_manifest, conf):
        with iRODSManager(conf, irods_manifest) as manager:
            yield manager

    def test_parse(self, manager):
        # limited to the study case rn
        for assay in manager.manifest.assays:
            if assay.importlinks:
                manager.register(assay)
                break
        else:
            msg = "No importlink found in manifest"
            raise ValueError(msg)
        assert manager.destinations[assay.owner]

    def test_annotate(self):
        pass

    def test_transfer(self):
        pass

    def test_crud(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        pass


class TestOmeroManager(TestManager):
    scheme = "irods"

    @pytest.fixture
    def manager(self, irods_manifest, conf):
        with OmeroManager(conf, irods_manifest) as manager:
            yield manager

    # def test_parse(self, manager):
    #     # limited to the study case rn
    #     for isaobject in manager.isaobjects:
    #         if isaobject.importlink is not None:
    #             manager.register(isaobject)
    #             break
    #     else:
    #         msg = "No importlink found in manifest"
    #         raise ValueError(msg)
    #     assert manager.destinations[isaobject.owner]
