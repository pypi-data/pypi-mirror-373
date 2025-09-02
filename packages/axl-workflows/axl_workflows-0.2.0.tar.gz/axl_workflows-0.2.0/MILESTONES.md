# 📌 AXL Workflows (axl) — Milestones & Tasks

---

## **M10 — Code Delivery (Artifact-only)**

**Goal:** Enable external repos to compile and run without baking images by delivering workflow code to pods as a tar.gz artifact deterministically.

**Reasoning:**

Today, the compiled Argo YAML effectively assumes the user’s workflow Python module is already present inside the runtime image (for example under `/app`). That is not true when users compile from an external repository. Without delivering the workflow source into the pod, imports fail even though the YAML is valid. Users are then forced to build a custom image just to “see it run,” which hurts iteration speed and makes simple demos difficult. We will deliver the workflow source via a tar.gz artifact stored in object storage (MinIO/S3), wired into the workflow, extracted at runtime to a deterministic path that the runner adds to `sys.path`. This preserves the runner import contract and supports offline clusters.

**Tasks**

* [ ] CLI: `--workflow-path` to stage code from repo root/module dir
* [ ] Compiler (artifact): upload/create tar.gz artifact; wire as input; extract to `/axl/workdir`
* [ ] Runner: support `--workflow-archive` (extract to `/axl/workdir`) and prepend to `sys.path`
* [ ] Docs: rationale, trade-offs (vs baked image), examples; troubleshooting
* [ ] Tests: golden YAML for artifact mode; runtime extraction tests

**Acceptance Criteria**

* [ ] Argo workflows run successfully with artifact delivery
* [ ] No dependency on AXL repo being present in the image
* [ ] External example repo compiles and runs end-to-end on Argo

---

## **M11 — Workflow Image Building**

**Goal:** Provide first-class support to bake workflow code and locked dependencies into a container image for production.

**Reasoning:**

In production, relying on runtime package installs or ad‑hoc code delivery increases cold‑start time, couples success to external networks, and risks dependency drift from the declared lockfile. Platform teams need a reproducible, auditable artifact that embeds both the workflow code and its locked dependencies so runs are fast, offline‑capable, and predictable. Providing a first‑class image build command gives a clean promotion path: developers iterate with configmap/artifact/package delivery, then promote to a baked image for stable environments. This aligns with Kubeflow Pipelines’ containerized component best practice and typical platform constraints (image allowlists, no internet at runtime, deterministic supply chain).

**Tasks**

* [ ] CLI: `axl build-image -m module:Class --tag ghcr.io/you/workflow:0.x`
* [ ] Image build: copy code + `pyproject.toml` + `uv.lock` (or requirements)
* [ ] Run `uv sync --frozen` at build time; label image with AXL/workflow versions
* [ ] Push to registry (GHCR or user-provided); auth via GitHub Actions optional
* [ ] Compiler integration: allow per-workflow image override; examples use built image
* [ ] Docs: how-to, CI recipe, promotion from dev → prod
* [ ] Tests: smoke build in CI (cache-only), integration via local registry in e2e

**Acceptance Criteria**

* [ ] Image builds reproducibly from a sample workflow repo and runs on Argo
* [ ] No runtime internet needed; `uv --frozen` enforced
* [ ] Examples/docs updated; users can point `Workflow.image` to built image

---

## **M0 — Project Bootstrap (uv-native)**

**Goal:** Repo skeleton with uv, linting, CI, and minimal CLI.

**Tasks**

* [x] Init repo structure: `axl/`, `examples/`, `tests/`
* [x] Create `pyproject.toml` (PEP 621 metadata, uv config, dev deps)
* [x] Add `uv.lock` (committed)
* [x] Setup dev workflow: `uv venv`, `uv sync --dev`, `uv run …`
* [x] Pre-commit hooks: ruff, black, mypy
* [x] GitHub Actions: setup-uv, cache, run ruff + mypy + pytest
* [x] CLI stub: `axl --version` via Typer
* [x] Base README.md with quickstart (params-as-step, pickle default)

**Acceptance Criteria**

* [x] `uv run axl --version` works
* [x] CI green on main (ruff, black, mypy, pytest)
* [x] Pre-commit hooks block style/type issues locally
* [ ] New clone can `make setup` and run tests successfully

---

## **M1 — DSL & IR MVP** ✅ (Released in v0.1.0)

**Goal:** Define workflows & inspect IR (with io metadata).

**Tasks**

* [x] Implement **`Workflow` base class** (defaults: image, default_io=pickle, input_mode_default, deps policy)
* [x] Implement **`@workflow` decorator** (attribute overrides)
* [x] Implement **`@step` decorator** with options:

  * `io_handler` (default to pickle)
  * `input_mode` = "object" | "path" | {arg: mode}
  * `resources`, `retries`, `env`
* [x] **Params-as-step pattern**: step calls inside `graph()` are symbolic (return `OutputRef`)
* [x] Parse workflow class → **IR** (`IRWorkflow`, `IRNode`, `IREdge`, **output IO metadata**: handler name, file ext)
* [x] Define **IOHandler protocol** + **`pickle_io_handler`** (save/load, metadata)
* [x] CLI: `axl validate -m myflow:MyWorkflow` (build IR; basic checks)
* [x] Unit tests for IR builder (nodes/edges, options captured)
* [x] Type-check CI (`uv run mypy axl`)

**Acceptance Criteria**

* [x] Users can define workflows/classes and steps; calling steps in `graph()` returns `OutputRef`
* [x] `axl validate examples/...:WorkflowClass` builds IR and validates
* [x] IO handlers selectable per step; file extensions derived
* [x] Type checks pass; unit tests cover IR invariants and step wiring

---

## **M1.5 — Local Runtime & Release**

**Goal:** Basic local execution and first PyPI release.

**Tasks**

* [x] **Local Runtime Engine**:
  * Implement `axl/runtime/local.py` with step execution
  * Topological sort and dependency resolution
  * Artifact management with IO handlers
  * Step method invocation and error handling
* [x] **CLI Execution**:
  * [x] `axl run local -m module:Class` command
  * [x] Workflow instantiation
  * [x] Parameter passing (`--params` YAML)
  * [x] Progress reporting and logging
* [x] **Runtime Tests**:
  * [x] End-to-end workflow execution tests
  * [x] Artifact save/load roundtrip tests
  * [x] Error handling and recovery tests
* [x] **Performance Improvements (completed)**:
  * [x] IR indexing for `get_node()` O(1) lookups
  * [x] Iterative IR traversal (builder) to avoid recursion limits
* [ ] **Release Preparation**:
  * Add PyPI metadata to `pyproject.toml` (name, version, license, classifiers)
  * `uv build && uv run twine check dist/*`
  * GitHub Actions: **tag-driven** release (OIDC trusted publisher)
  * README "Install / Quickstart"

➡️ **Release v0.1.0 (PyPI/TestPyPI)** 🎉

* **DSL & IR**: Workflow definition, step decorators, IR building
* **IO Handlers**: Pickle and cloudpickle serialization
* **Local Runtime**: Basic workflow execution
* **CLI**: Validation and local execution commands
* **First PyPI Release**: Installable package

**Acceptance Criteria**

* [x] `axl run local -m examples/...:WorkflowClass` executes end-to-end with artifacts persisted via IO handlers
* [x] Failing step surfaces actionable error with non-zero exit
* [x] PyPI/TestPyPI build passes `twine check`; package installs and `axl --help` works

---

## **M2 — Argo Compiler** ✅ (Released in v0.2.0)

**Goal:** Compile IR → Argo Workflow YAML (KFP-compatible).

**Tasks**

* [x] **M2.1 — Core Compiler Structure**
  * [x] Create `axl/compiler/argo.py` with `ArgoCompiler` class
  * [x] Implement basic YAML generation structure
  * [x] Add workflow metadata and spec generation
  * [x] Create base template structure for steps

* [x] **M2.2 — Template Generation**
  * [x] Implement container template generation for each step
  * [x] Add command/args for runner invocation
  * [x] Generate basic environment variables
  * [x] Add resource specifications (CPU/memory)

* [x] **M2.3 — DAG Structure**
  * [x] Implement DAG task generation from IR edges
  * [x] Add task dependencies mapping
  * [x] Generate task names and template references

* [x] **M2.4 — IO Manifest Generation**
  * [x] Create IO manifest structure for step inputs/outputs
  * [x] Map Python objects to artifact file paths
  * [x] Add file extensions based on IO handlers (`.pkl`, `.json`, etc.)
  * [x] Generate artifact input/output specifications

* [x] **M2.5 — Artifact Handling**
  * [x] Implement PVC-based artifact storage
  * [x] Add artifact input/output mapping in templates
  * [x] Generate artifact paths and naming conventions
  * [x] Add artifact cleanup and lifecycle management

* [x] **M2.6 — Advanced Features**
  * [x] Add retry strategy support (`retryStrategy`)
  * [x] Implement resource limits and requests
  * [x] Add environment variable support
  * [x] Support conditional execution (`when` clauses)

* [x] **M2.7 — CLI Integration**
  * [x] Add `axl compile --target argo --out out.yaml` command
  * [x] Implement workflow class loading and IR building
  * [x] Add output file generation and validation
  * [x] Add help text and error handling

* [x] **M2.8 — Testing & Validation**
  * [x] Create golden-file tests for YAML output
  * [x] Add Argo schema validation (if `argo lint` available)
  * [x] Test with simple workflows (linear, diamond, complex DAGs)
  * [x] Add integration tests with actual Argo installation

* [x] **M2.9 — Documentation & Examples**
  * [x] Update `examples/churn_workflow.py` for Argo compilation
  * [x] Add Argo-specific documentation
  * [x] Create example Argo YAML outputs
  * [x] Add troubleshooting guide for common issues

➡️ **Release v0.2.0**

* **Argo Compiler**: IR → Argo Workflow YAML
* **KFP Compatibility**: Kubeflow Pipelines support
* **Artifact Management**: IO manifest generation
* **Production Ready**: Kubernetes deployment

**Acceptance Criteria**

* [x] `axl compile --target argo` emits YAML with `entrypoint` and `main-dag` template
* [x] Template/task/artifact names DNS-1123 compliant (hyphens)
* [x] Artifacts wired via inputs/outputs at template level; IO manifest passed to runner (template inputs do not use `from`; wiring lives in DAG task `arguments`)
* [x] Workflows run on Argo with `serviceAccountName` and MinIO/S3 artifact repo
* [x] Step-level packages installed by runner and executed successfully

---

## **M3 — Runner Container** ✅ (Released in v0.2.0)

**Goal:** Execute steps with uv-powered envs and io_handlers.

**Tasks**

* [ ] `Dockerfile.runner`: install uv; cache at `/opt/uv-cache` (N/A; moved to M4 GHCR image)
* [x] Runner entrypoint (`axl.runtime.__main__`)

  * Parse IO manifest & step args
  * **Env setup**: create/reuse workflow venv (`uv sync` from lockfile/requirements)
  * **Inputs**: load via handler (`object`) or pass **paths** per `input_mode`
  * Invoke user function
  * **Outputs**: save via handler (default pickle); write metadata
* [x] Artifact storage (PVC path; S3 later)
* [x] Logging: structured JSON
* [x] Local run: `axl run local -m module:Class`
* [x] E2E tests: object↔path modes, pickle roundtrip, failures

➡️ **Included in Release v0.2.0**

* **Runner Container**: Docker-based step execution
* **UV Integration**: Environment management with uv
* **Artifact Storage**: PVC and S3 support
* **Structured Logging**: JSON logs for observability
* **Production Execution**: Containerized workflow runs

**Acceptance Criteria**

* [x] Runner entrypoint loads inputs, executes step, saves outputs according to manifest
* [x] Structured JSON logs printed with workflow, step, status, duration_ms
* [x] Local execution and containerized execution produce identical results

---

## **M3.5 — Auto-Graph Generation**

**Goal:** Eliminate the need for explicit `graph()` methods by auto-generating workflow dependencies from `@step` method signatures and type hints.

**Reasoning:**

Currently, users must define an explicit `graph()` method that wires step dependencies manually. This creates boilerplate code and potential for wiring errors. By analyzing `@step` method signatures, parameter types, and return types, we can automatically infer the workflow DAG. This makes workflows more intuitive (natural Python method signatures), reduces boilerplate, and eliminates manual wiring mistakes. The auto-generation will be smart enough to handle type compatibility, parameter naming, and complex data flow patterns.

**Tasks**

* [ ] **Enhanced `@step` Decorator**:
  * [ ] Capture method signature metadata during decoration
  * [ ] Extract input parameter types and names
  * [ ] Extract return type annotations
  * [ ] Store metadata in `_axl_signature` attribute

* [ ] **Signature Analysis Engine**:
  * [ ] Implement `_extract_input_types()` for parameter analysis
  * [ ] Implement `_extract_output_type()` for return type analysis
  * [ ] Handle type annotations (including generics, Union, Optional)
  * [ ] Support default parameter values and required/optional inputs

* [ ] **Auto-Dependency Resolution**:
  * [ ] Implement `resolve_dependencies()` function
  * [ ] Strategy 1: Exact parameter name matching to step names
  * [ ] Strategy 2: Type-based compatibility matching
  * [ ] Generate `IREdge` objects automatically
  * [ ] Handle complex dependency patterns (diamond, parallel, etc.)

* [ ] **Type Compatibility System**:
  * [ ] Implement `is_type_compatible()` function
  * [ ] Support exact type matches
  * [ ] Handle generic types (List, Dict, Tuple)
  * [ ] Support Union types and Optional types
  * [ ] Fallback to `Any` type for unannotated parameters

* [ ] **IR Builder Enhancement**:
  * [ ] Update `build_ir()` to use auto-graph generation
  * [ ] Remove requirement for explicit `graph()` method
  * [ ] Generate `IRNode` objects from step metadata
  * [ ] Validate generated DAG for cycles and orphaned nodes

* [ ] **Migration & Examples**:
  * [ ] Update all examples to remove `graph()` methods
  * [ ] Test auto-generation with various workflow patterns
  * [ ] Update documentation to reflect new syntax
  * [ ] Add examples of complex dependency patterns

**Acceptance Criteria**

* [ ] Workflows can be defined without explicit `graph()` methods
* [ ] Dependencies are correctly inferred from method signatures
* [ ] Type annotations are respected for parameter matching
* [ ] Complex workflows (diamond, parallel, conditional) work correctly
* [ ] All existing examples compile and run with auto-generated graphs
* [ ] Performance is maintained (O(1) IR lookups preserved)

**Example Syntax**

```python
class IrisKNN(Workflow):
    name = "iris-knn"
    image = "axl-runner:dev3"
    io_handler = "pickle"

    @step(packages=["scikit-learn"])
    def load_data(self) -> tuple[Any, Any]:
        return load_iris().data, load_iris().target

    @step(packages=["scikit-learn"])
    def split(self, data: tuple[Any, Any]) -> tuple[Any, Any, Any, Any]:
        X, y = data
        return train_test_split(X, y, test_size=0.2, random_state=42)

    @step(packages=["scikit-learn"])
    def train(self, split: tuple[Any, Any, Any, Any]) -> tuple[Any, Any, Any]:
        X_train, X_test, y_train, y_test = split
        clf = KNeighborsClassifier(n_neighbors=3)
        clf.fit(X_train, y_train)
        return clf, X_test, y_test

    @step(packages=["scikit-learn"])
    def evaluate(self, trained: tuple[Any, Any, Any]) -> float:
        clf, X_test, y_test = trained
        y_pred = clf.predict(X_test)
        return accuracy_score(y_test, y_pred)

    # No graph() method needed!
    # Auto-generated: load_data -> split -> train -> evaluate
```

---

## **M4 — Runner Image (GHCR Publishing)**

**Goal:** Publish the AXL runner image to GHCR with tags aligned to the AXL version so users don’t need to build locally.

**Tasks**

* [ ] GitHub Actions workflow (on tag/release) to build and push `ghcr.io/axl-workflows/runner:<axl-version>`
* [ ] Tag strategy via `docker/metadata-action` (e.g., `0.1.0`, `0.1`, `latest`)
* [ ] Use GITHUB_TOKEN with `packages: write` permissions
* [ ] Ensure image embeds AXL version matching `axl/__init__.py` (`__version__`)
* [ ] Docs: reference GHCR image in Argo compiler guide; examples default to GHCR image

**Acceptance Criteria**

* [ ] Tagging a release builds and publishes `ghcr.io/axl-workflows/runner:<version>`
* [ ] `latest` tag updated; image pull from public GHCR succeeds without auth
* [ ] Examples use GHCR image and run on Argo without local image build

---

## **M5 — Kubeflow Pipelines (KFP) Compiler**

**Goal:** Compile IR → KFP pipeline package (visible/runnable in KFP UI).

**Tasks**

* [ ] Implement `compiler.kfp` that generates a KFP pipeline package (v1.8-compatible)
  * [ ] Translate IR DAG to KFP components/graph
  * [ ] Preserve AXL runtime contract (runner container, IO manifest)
  * [ ] Support per-step packages (install in container via runner)
* [ ] CLI: `axl compile --target kfp --out pipeline.yaml|.zip`
  * [ ] Optionally `axl kfp run` to upload/create a run via KFP SDK
* [ ] Examples: compile IrisKNN to KFP and run under `pipeline-runner`
* [ ] Golden tests for generated KFP package

**Acceptance Criteria**

* [ ] Compiled package is importable/visible in KFP UI and runnable
* [ ] Pipeline run uses `pipeline-runner` SA and KFP artifact repo
* [ ] Argo-submitted run parity with KFP-compiled run (same steps/outputs)

---

## **M6 — Dagster Compiler**

**Goal:** Compile IR → Dagster ops & job for dev.

**Tasks**

* [ ] Implement `compiler.dagster` (ops, graph, job) that **invokes the runner** for uniform behavior
* [ ] CLI: `axl compile --target dagster --out dagster_job.py`
* [ ] Example job in `examples/`
* [ ] Golden tests for generated code

➡️ **Release v0.3.0**

* **Dagster Compiler**: IR → Dagster ops and jobs
* **Development Workflow**: Local Dagster execution
* **Uniform Behavior**: Same runner across backends
* **Developer Experience**: Rich Dagster UI integration

**Acceptance Criteria**

* [ ] Generated Dagster job runs locally and mirrors IR DAG
* [ ] Ops invoke the AXL runner and persist artifacts correctly
* [ ] Golden snapshot tests stable

---

## **M7 — Dependency Management (uv-first) & Image Baking)**

**Goal:** Reproducible deps at workflow level; optional warm env; baked images for prod.

**Tasks**

* [ ] Workflow-level deps:

  * `use_lockfile=True` (prefer `uv.lock`)
  * `requirements=[...]` **or** `requirements_file="requirements.txt"` fallback
* [ ] Optional **warm_env**: synthetic setup step to pre-build venv/cache
* [ ] CLI: `axl build-image -m module:Class --tag ghcr.io/you/axl:0.x`

  * Copy `pyproject.toml` + `uv.lock` / requirements
  * `uv sync --frozen` at build time (no runtime installs in prod)
* [ ] System packages only in baked images (no apt in runtime pods)
* [ ] Examples: pandas+sklearn workflow; large deps

➡️ **Release v0.4.0**

* **Dependency Management**: UV-first workflow deps
* **Image Baking**: Pre-built container images
* **Reproducible Builds**: Lockfile and frozen deps
* **Production Optimization**: No runtime installs
* **Large Dependency Support**: Efficient caching

**Acceptance Criteria**

* [ ] Workflow-level lockfile respected; `uv sync --frozen` enforced in baked image
* [ ] Optional warm env step reduces cold-starts measurably
* [ ] `axl build-image` produces runnable image; example with heavy deps runs

---

## **M8 — UX & Extras**

**Goal:** Improve developer experience and observability.

**Tasks**

* [ ] CLI polish: consistent help text; `--json` output for validate/compile/run
* [ ] Error taxonomy: user vs infra exit codes; actionable messages
* [ ] Logging/metrics: JSON logs fields per repo rules; optional Prometheus textfile
* [ ] Docs: architecture diagrams (DSL→IR→Compiler→Runner); gotchas; examples end-to-end
* [ ] Make targets: `setup`, `fmt`, `lint`, `test`, `build` verified

**Acceptance Criteria**

* [ ] `axl --help` accurate; machine-readable `--json` responses where applicable
* [ ] Common failure cases surface clear remediation steps
* [ ] Docs include diagrams and runnable examples; links verified

---

## **M9(optional) — Performance & UX Improvements**

**Goal:** Enhance performance and user experience with caching and better data handling.

**Tasks**

* [ ] **Workflow Hashing & Caching**:
  * Add `blake3` dependency for fast hashing
  * Implement `IRWorkflow.compute_hash()` method
  * Hash-based workflow identification and caching
  * CLI: show workflow hash for reproducibility
* [ ] **Hash-based Artifact Storage**:
  * LocalRuntime: optional `use_hash` flag
  * Store artifacts under `workspace/{hash}/` structure
  * Automatic cleanup of old workflow artifacts
  * Hash-based artifact lookup and organization
* [ ] **PyArrow/Parquet IO Handlers**:
  * Add `pyarrow` as optional dependency
  * Implement `ParquetIOHandler` for DataFrames
  * Implement `ArrowIOHandler` for Arrow tables
  * Automatic type detection and conversion
  * Performance benchmarks and tests

➡️ **Release v0.1.1**

* **Performance**: Workflow caching and hash-based storage
* **Data Handling**: PyArrow/Parquet support for ML workflows
* **User Experience**: Better artifact organization and reproducibility
* **Performance**: Faster data serialization and workflow execution

---
