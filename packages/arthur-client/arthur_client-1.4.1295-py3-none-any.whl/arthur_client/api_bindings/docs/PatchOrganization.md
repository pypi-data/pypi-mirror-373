# PatchOrganization


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_organization import PatchOrganization

# TODO update the JSON string below
json = "{}"
# create an instance of PatchOrganization from a JSON string
patch_organization_instance = PatchOrganization.from_json(json)
# print the JSON string representation of the object
print(PatchOrganization.to_json())

# convert the object into a dict
patch_organization_dict = patch_organization_instance.to_dict()
# create an instance of PatchOrganization from a dict
patch_organization_from_dict = PatchOrganization.from_dict(patch_organization_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


