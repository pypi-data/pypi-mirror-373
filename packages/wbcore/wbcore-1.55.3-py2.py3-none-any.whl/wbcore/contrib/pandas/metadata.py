from slugify import slugify

from wbcore.metadata.metadata import WBCoreMetadata


class PandasMetadata(WBCoreMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)
        metadata["identifier"] += f"-{slugify(view.__class__.__name__)}"
        metadata["fields"] = view.get_pandas_fields(request).to_dict()
        # if ordering fields is not included in the metadata (e.g. dev didn't explicitly specify a list), then we inject the pandas fields by default
        # it is safe to do that because for pandas table, the ordering happens on AgGrid
        if not metadata["ordering_fields"]:
            metadata["ordering_fields"] = {key: key for key in metadata["fields"].keys()}
        return metadata
