# Entities

Types:

```python
from hubmap_entity_sdk.types import (
    EntityCreateMultipleSamplesResponse,
    EntityListAncestorOrgansResponse,
    EntityListCollectionsResponse,
    EntityListSiblingsResponse,
    EntityListTupletsResponse,
    EntityListUploadsResponse,
    EntityRetrieveGlobusURLResponse,
)
```

Methods:

- <code title="get /entities/{id}">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">retrieve</a>(id) -> object</code>
- <code title="put /entities/{id}">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">update</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/entity_update_params.py">params</a>) -> object</code>
- <code title="post /entities/multiple-samples/{count}">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">create_multiple_samples</a>(count) -> <a href="./src/hubmap_entity_sdk/types/entity_create_multiple_samples_response.py">EntityCreateMultipleSamplesResponse</a></code>
- <code title="delete /entities/{id}/flush-cache">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">flush_cache</a>(id) -> None</code>
- <code title="get /entities/{id}/instanceof/{type}">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">is_instance_of</a>(type, \*, id) -> object</code>
- <code title="get /entities/{id}/ancestor-organs">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">list_ancestor_organs</a>(id) -> <a href="./src/hubmap_entity_sdk/types/entity_list_ancestor_organs_response.py">EntityListAncestorOrgansResponse</a></code>
- <code title="get /entities/{id}/collections">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">list_collections</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/entity_list_collections_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/entity_list_collections_response.py">EntityListCollectionsResponse</a></code>
- <code title="get /entities/{id}/siblings">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">list_siblings</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/entity_list_siblings_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/entity_list_siblings_response.py">EntityListSiblingsResponse</a></code>
- <code title="get /entities/{id}/tuplets">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">list_tuplets</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/entity_list_tuplets_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/entity_list_tuplets_response.py">EntityListTupletsResponse</a></code>
- <code title="get /entities/{id}/uploads">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">list_uploads</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/entity_list_uploads_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/entity_list_uploads_response.py">EntityListUploadsResponse</a></code>
- <code title="get /entities/{id}/globus-url">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">retrieve_globus_url</a>(id) -> str</code>
- <code title="get /entities/{id}/provenance">client.entities.<a href="./src/hubmap_entity_sdk/resources/entities/entities.py">retrieve_provenance</a>(id) -> object</code>

## Type

Methods:

- <code title="get /entities/type/{type_a}/instanceof/{type_b}">client.entities.type.<a href="./src/hubmap_entity_sdk/resources/entities/type.py">is_instance_of</a>(type_b, \*, type_a) -> object</code>

# EntityTypesAll

Types:

```python
from hubmap_entity_sdk.types import EntityTypesAllListResponse
```

Methods:

- <code title="get /entity-types">client.entity_types_all.<a href="./src/hubmap_entity_sdk/resources/entity_types_all.py">list</a>() -> <a href="./src/hubmap_entity_sdk/types/entity_types_all_list_response.py">EntityTypesAllListResponse</a></code>

# Ancestors

Types:

```python
from hubmap_entity_sdk.types import AncestorRetrieveResponse
```

Methods:

- <code title="get /ancestors/{id}">client.ancestors.<a href="./src/hubmap_entity_sdk/resources/ancestors.py">retrieve</a>(id) -> <a href="./src/hubmap_entity_sdk/types/ancestor_retrieve_response.py">AncestorRetrieveResponse</a></code>

# Descendants

Types:

```python
from hubmap_entity_sdk.types import DescendantRetrieveResponse
```

Methods:

- <code title="get /descendants/{id}">client.descendants.<a href="./src/hubmap_entity_sdk/resources/descendants.py">retrieve</a>(id) -> <a href="./src/hubmap_entity_sdk/types/descendant_retrieve_response.py">DescendantRetrieveResponse</a></code>

# Parents

Types:

```python
from hubmap_entity_sdk.types import ParentRetrieveResponse
```

Methods:

- <code title="get /parents/{id}">client.parents.<a href="./src/hubmap_entity_sdk/resources/parents.py">retrieve</a>(id) -> <a href="./src/hubmap_entity_sdk/types/parent_retrieve_response.py">ParentRetrieveResponse</a></code>

# Children

Types:

```python
from hubmap_entity_sdk.types import ChildRetrieveResponse
```

Methods:

- <code title="get /children/{id}">client.children.<a href="./src/hubmap_entity_sdk/resources/children.py">retrieve</a>(id) -> <a href="./src/hubmap_entity_sdk/types/child_retrieve_response.py">ChildRetrieveResponse</a></code>

# Doi

Methods:

- <code title="get /doi/redirect/{id}">client.doi.<a href="./src/hubmap_entity_sdk/resources/doi.py">redirect</a>(id) -> None</code>

# Datasets

Types:

```python
from hubmap_entity_sdk.types import (
    Collection,
    Dataset,
    Donor,
    DonorMetadata,
    Epicollction,
    File,
    Person,
    Publication,
    Sample,
    Upload,
    DatasetBulkUpdateResponse,
    DatasetCreateComponentsResponse,
    DatasetListDonorsResponse,
    DatasetListOrgansResponse,
    DatasetListSamplesResponse,
    DatasetRetrievePairedDatasetResponse,
    DatasetRetrieveRevisionResponse,
)
```

Methods:

- <code title="put /datasets">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">bulk_update</a>(\*\*<a href="src/hubmap_entity_sdk/types/dataset_bulk_update_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/dataset_bulk_update_response.py">DatasetBulkUpdateResponse</a></code>
- <code title="post /datasets/components">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">create_components</a>(\*\*<a href="src/hubmap_entity_sdk/types/dataset_create_components_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/dataset_create_components_response.py">DatasetCreateComponentsResponse</a></code>
- <code title="get /datasets/{id}/donors">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">list_donors</a>(id) -> <a href="./src/hubmap_entity_sdk/types/dataset_list_donors_response.py">DatasetListDonorsResponse</a></code>
- <code title="get /datasets/{id}/organs">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">list_organs</a>(id) -> <a href="./src/hubmap_entity_sdk/types/dataset_list_organs_response.py">DatasetListOrgansResponse</a></code>
- <code title="get /datasets/{id}/revisions">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">list_revisions</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/dataset_list_revisions_params.py">params</a>) -> object</code>
- <code title="get /datasets/{id}/samples">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">list_samples</a>(id) -> <a href="./src/hubmap_entity_sdk/types/dataset_list_samples_response.py">DatasetListSamplesResponse</a></code>
- <code title="get /datasets/unpublished">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">list_unpublished</a>(\*\*<a href="src/hubmap_entity_sdk/types/dataset_list_unpublished_params.py">params</a>) -> object</code>
- <code title="put /datasets/{id}/retract">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">retract</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/dataset_retract_params.py">params</a>) -> object</code>
- <code title="get /datasets/{id}/latest-revision">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">retrieve_latest_revision</a>(id) -> object</code>
- <code title="get /datasets/{id}/paired-dataset">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">retrieve_paired_dataset</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/dataset_retrieve_paired_dataset_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/dataset_retrieve_paired_dataset_response.py">DatasetRetrievePairedDatasetResponse</a></code>
- <code title="get /datasets/{id}/prov-info">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">retrieve_prov_info</a>(id, \*\*<a href="src/hubmap_entity_sdk/types/dataset_retrieve_prov_info_params.py">params</a>) -> object</code>
- <code title="get /datasets/{id}/prov-metadata">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">retrieve_prov_metadata</a>(id) -> object</code>
- <code title="get /datasets/{id}/revision">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">retrieve_revision</a>(id) -> <a href="./src/hubmap_entity_sdk/types/dataset_retrieve_revision_response.py">DatasetRetrieveRevisionResponse</a></code>
- <code title="get /datasets/sankey_data">client.datasets.<a href="./src/hubmap_entity_sdk/resources/datasets.py">retrieve_sankey_data</a>() -> object</code>

# Uploads

Types:

```python
from hubmap_entity_sdk.types import UploadUpdateBulkResponse
```

Methods:

- <code title="put /uploads">client.uploads.<a href="./src/hubmap_entity_sdk/resources/uploads.py">update_bulk</a>(\*\*<a href="src/hubmap_entity_sdk/types/upload_update_bulk_params.py">params</a>) -> <a href="./src/hubmap_entity_sdk/types/upload_update_bulk_response.py">UploadUpdateBulkResponse</a></code>
