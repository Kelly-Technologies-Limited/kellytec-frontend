# Product workflows

Each YAML in `../workflows/` defines one GitHub workflow. Its `scripts/` entrypoints
live under the matching directory here. YAML jobs and steps remain the orchestration
model; Python files are executable operations, not GitHub Jobs themselves.

| Workflow | Definition |
| --- | --- |
| Check and Build kellytec-design-system | [check-and-build-kellytec-design-system.yml](../workflows/check-and-build-kellytec-design-system.yml) |
| Check kellytec-website | [check-kellytec-website.yml](../workflows/check-kellytec-website.yml) |
| Deploy kellytec-website to GitHub Pages | [deploy-kellytec-website-to-github-pages.yml](../workflows/deploy-kellytec-website-to-github-pages.yml) |

`common/changes/products.json` owns product impact, including shared inputs. Root
plans and documentation run only change detection; unknown paths conservatively
select all products. PRs qualify products without publication or deployment.

`common/scripts/resolve_source_and_dependencies.py` freezes one source/dependency
snapshot per run. Retries restore that snapshot and already-qualified bytes. A
successful check without a product artifact authorizes no downstream operation.
The deployment/publish workflow verifies the original Check run and its entire
artifact manifest before using its selected Automation source.

Registry producers declare each export under `common/registry/` using a concrete
name and domain. Publication is atomic for the complete product set. The Research
platform owns inspection semantics; producer declarations contain no Research UI,
project, server or QC resource bindings.

Cloud resource identifiers are configuration, independent of repository names.
Changing a directory or repository never authorizes recreating a resource or
clearing its deployment state. Remote acceptance follows the repository rename
and reviewed IAM/state cutover. Local test success is not deployment evidence.
