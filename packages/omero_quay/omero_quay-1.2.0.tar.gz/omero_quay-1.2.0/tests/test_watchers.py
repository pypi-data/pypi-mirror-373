from __future__ import annotations


def test_omero_watcher(conf):  # noqa:ARG001
    assert True  # wait for omero_log merge
    # watcher = OmeroWatcher(conf, host="localhost")
    # with watcher:
    #     events = watcher.find_events(since=10)
    #     if events:
    #         manifest = watcher.gen_manifest(*events)
    #         assert manifest
