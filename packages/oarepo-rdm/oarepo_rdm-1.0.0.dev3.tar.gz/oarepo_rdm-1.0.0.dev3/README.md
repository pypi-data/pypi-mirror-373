# OARepo RDM

A set of runtime patches to enable RDM service to work with different metadata models.
It replaces both `search/search_drafts/scan/read` methods to search/look into multiple
models and for the methods that that take a pid delegates the call to a specialized
per-model services.

It also patches the pid context of the `RDMRecord/RDMDraft` so that when a resolve is called
on the record, an instance of a specialized record is returned.

This package depends on oarepo patches to invenio_rdm_records that bring the possibility
to register custom service/resource in place of the default ones.

## Permissions

For performance reasons, permissions for search/scan are evaluated on the rdm-records
level, not on the specialized-service layer. This means that the permissions defined
for the rdm-records service will apply to all requests, regardless of which specialized
service is handling the request.

Please make sure that all the models are using the same permission policy and that
this policy is configured in `RDM_PERMISSION_POLICY` config.
