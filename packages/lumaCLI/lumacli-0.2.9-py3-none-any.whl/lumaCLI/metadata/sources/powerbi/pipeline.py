from lumaCLI.metadata.sources.powerbi.extract import powerbi
from lumaCLI.metadata.sources.powerbi.models import WorkspaceInfo
from lumaCLI.metadata.sources.powerbi.transform import transform


def pipeline():
    source = powerbi()
    metadata = WorkspaceInfo(**next(iter(source)))
    yield transform(metadata)


if __name__ == "__main__":
    from pathlib import Path

    manifest = next(iter(pipeline()))

    with Path("powerbi_extracted.json").open("w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(by_alias=True))
    # print(manifest)
