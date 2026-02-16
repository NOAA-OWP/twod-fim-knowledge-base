# Methodology Report: Automated 2D Hydrodynamic Reach-Based FIM Libraries for Operational Flood Forecasting

## Executive Summary
This report presents a pilot‑informed methodology for producing nationwide 2D flood inundation map (FIM) libraries using reach‑based hydrodynamic modeling to move beyond the GIS‑based Height Above Nearest Drainage (HAND) methods. The approach preserves the Flows2FIM operational pattern of pre‑generated per‑reach libraries that can be assembled in near real time. Unlike Ripple1D, the reach‑level 2D models are built from scratch through an automated pipeline rather than repurposed from existing studies.

Our work to date has focused on developing a “structured” methodology that can be automated, identifying decisions that materially affect outcomes, and recording evidence for those decisions through a system decision record (SDR) process.

(to do: redo this section after Key Decision section is updated) Key outcomes to date indicate that a reach‑based 2D library approach is feasible and integrates directly with existing Flows2FIM mosaicking workflows. Downstream stage transfer is required at confluences and other backwater‑sensitive settings because normal‑depth‑only boundaries underpredict water‑surface elevations (WSEL). Domain and stage‑transfer geometry must extend beyond hydrofabric divides in wide floodplains, and coarse modeling helps place transfer lines in large rivers. DEM conditioning around culverts and structures is critical to avoid divergent flow paths and impoundment artifacts. Lake and coastal reaches require non‑standard handling, where GIS‑based or waterbody‑stage approaches are more appropriate.

This report documents the conceptual framework, the evidence‑driven methodology evolution, a proposed automation workflow, known limitations, and a unified appendix of test cases. Once approved, the methodology will be refined and implemented in a prototype area before scaling.

## Introduction
OWP currently produces nationwide flood inundation maps using HAND (Height Above Nearest Drainage) method and, where available, HEC‑RAS 1D based libraries from Ripple1D (NGWPC, n.d.-a). These approaches provide broad coverage and operational reliability, however limitations including physics derived accuracy, reproducibility, and flexibility to handle diverse hydraulic settings are well documented. Bathtub or level‑pool methods such as HAND treat flooding as a static surface and do not represent flow routing, backwater, or structure‑influenced hydraulics. These methods can produce large biases in inundation area (e.g., >200% error) and recent work calls for avoiding them in decision‑relevant flood‑management practice (Sanders et al., 2024). Recent incorporation of Ripple1D libraries improves physical accuracy by leveraging 1D hydraulic models and cross‑sectional data from existing studies, but reliance on **prebuilt legacy models** brings their irregularities such as sparse and discontinuous coverage, inconsistent development methodologies, terrain/data mismatches, and outdated inputs (i.e., unknown or superseded data sources) into OWP's operational flood inundation mapping. As a result, Ripple1D can improve local fidelity but adds complexity and coverage gaps.

Acknowledging the aforementioned limitations, these methods were selected in part to achieve the goal of creating a product with complete national coverage, and the cost effectiveness and scalability of these methods was a key factor for not developing physics based models. Having achieved a national coverage benchmark, along with recent advances in GPU/HPC compute, cloud parallelization, and modern 2D hydrodynamic solvers, it is now feasible to apply 2D modeling beyond local studies and into a national library‑based system. This report proposes a 2D hydrodynamic reach‑based library approach to address these gaps. The approach builds reach‑level models from scratch through an automated pipeline while preserving the Ripple1D and Flows2FIM operational pattern: pre‑generate per‑reach FIM libraries and mosaic them downstream‑to‑upstream in near real time using nowcast or forecast discharges (NGWPC, n.d.-a, n.d.-b). The key difference is how the libraries are derived—the computational engine is 2D hydrodynamics rather than 1D, and model construction is automated rather than repurposed from legacy studies (See Fig. 1 for visual explanation). Because 2D modeling is computationally intensive, the workflow shifts heavy computation (i.e. model simulations) to a pre‑processing step, so forecast‑time FIM development is limited to the rapid assembly step of creating a lightweight selection‑and‑mosaic pointer product (vrt) rather than a new simulation.

This report lays out a pilot‑informed, initial, scalable methodology and explains how it was developed, where the most consequential decisions sit, and where uncertainty remains. It documents those decisions and open questions through a System Decision Records (SDR) process, and defines the conceptual framework, automation logic, and operational interfaces needed to implement the approach. Once approved, the methodology will be refined and tested in a prototype area before scaling further.

The intent of the work described in the following sections is to assess implementation readiness for 2D reach‑based FIM libraries and to sharpen methodological clarity. The work does not deliver a final production automation workflow; instead, it establishes the foundation for upcoming tasks to achieve that goal. The scope therefore focuses on describing the workflow, documenting decision evidence, and identifying where specialized handling or additional validation is required before national‑scale production.


![Reach-based hydrodynamic modeling for the National Water Model using 1D and 2D approaches](methodology-report/image1.png)
*Figure 1. Reach‑based hydrodynamic modeling for the National Water Model river network using Ripple1D and 2D approaches. Ripple1D relies on existing 1D models and conflates their cross sections onto target reaches to build reach‑based models. The new 2D methodology does not rely on existing models; it creates a new 2D model for each reach domain, illustrated by the different colored grids in the rightmost panel.*

## Related Work and Context
This project sits at the intersection of three mature research threads: **library‑based inundation mapping**, **large‑scale 2D hydrodynamics**, and **automated model setup**. The literature below provides the closest precedents and highlights where our approach diverges.

### Library‑based inundation mapping (operational precedents)
The USGS Flood Inundation Mapping (FIM) program defines a **map library** as a set of inundation maps at discrete stages, linked to gages and used operationally for preparedness and response. The USGS process emphasizes repeatable model construction, calibration, and library publication for real‑time use, which is conceptually aligned with our library‑first paradigm (albeit local and not reach‑based at national scale). This is a strong institutional precedent for the idea that *precomputed libraries + real‑time lookup* can be operationally reliable (U.S. Geological Survey, n.d.-a, n.d.-b) and aligns well with the NextGen concept where better performing models can replace existing models throughout the network.

### Continental‑scale 2D forecasting with precomputed libraries (closest analogue)
The Hurricane Harvey study by Wing et al. (2019) is the closest direct analogue. The authors coupled **Fathom‑US** (a continental‑scale 2D model based on LISFLOOD‑FP) to NOAA forecasts of streamflow, rainfall, and coastal surge. For Harvey, fluvial inundation was extracted from an existing US‑wide simulation library, while pluvial and coastal components were simulated for the event. The study produced medium‑term (2–15 day) forecasts and hindcasts, with reported skill around CSI ≈ 0.66 for maximum extent and mean water‑surface error on the order of ~1 m against USGS benchmarks. This work demonstrates that a national 2D library can be operationally coupled to forecasts without crippling lead times. The approach outlined in this document builds on and improces this framework by (1) making the library reach‑based (outputs are organized and indexed per reach), (2) emphasizing downstream stage transfer between connected reaches, (3) treating library construction as a per‑reach automation workflow rather than a single continental model build, and (4) indexing libraries by a discharge × downstream‑WSEL matrix rather than return‑period flow bins.
### Global and regional return‑period libraries (library at scale, but not reach‑based)
The Copernicus CEMS/GloFAS global river flood hazard maps provide precomputed inundation depth layers for multiple return periods (10–500 years). They are derived from LISFLOOD river flows and LISFLOOD‑FP inundation simulations, and are intended for exposure assessment and impact‑based forecasting. These maps are explicitly designed as global library products and are used operationally for rapid mapping. However, they are return‑period‑binned and network‑linked rather than reach‑specific with downstream stage transfer. This demonstrates feasibility of large‑scale library generation and operational linkage to hydrologic forecasts, while also highlighting the gap our reach‑based approach addresses (Baugh et al., 2024).

### Automated 2D model setup frameworks
HydroMT provides a reproducible, data‑driven framework for building hydrologic and hydrodynamic models at scale. Its ecosystem (including HydroMT‑SFINCS) has been used to automate globally applicable compound‑flood modeling from global datasets, with boundary conditions coupled to upstream hydrology and coastal surge/tide models. The NHESS compound‑flood framework demonstrates automated, large‑scale 2D setup and transparent, repeatable preprocessing at global scales (Eilander et al., 2023a, 2023b). These efforts are the closest open‑source automation precedents known to the authors, though they target event‑based simulations rather than reach‑based library construction with stage transfer between connected reaches.

### Foundational 2D floodplain modeling lineage
The raster‑based formulation in Bates and De Roo (2000) introduced a simplified yet dynamic representation using a 1D kinematic wave for channel flow coupled to a 2D diffusion‑wave floodplain. This formulation underpins many modern large‑scale flood models, including LISFLOOD‑FP. The paper provides the methodological lineage for efficient raster‑based modeling at scale and is the technical foundation behind many of the large‑domain models discussed above.

---

Taken together, prior work demonstrates the feasibility of precomputed libraries, large‑scale 2D simulation, and automated model setup, but the specific synthesis of reach‑based 2D modeling with downstream stage transfer and Flows2FIM‑compatible libraries is not yet well represented in the literature and is the central contribution of this methodology.

## Conceptual Modeling Framework
This section describes the conceptual modeling framework for segmented, reach‑based 2D FIM libraries that, when assembled, create outputs with skill approcimate to  FIMS developed using a continuous network‑scale model.

As noted above, the framework mirrors the Ripple1D library approach but uses 2D hydrodynamic models per reach. At a high level, the workflow is:

1. Build an individual 2D model for each reach using the NWM hydrofabric.
2. Apply boundary conditions for each model run using a discharge range at the upstream boundary and a downstream stage derived from the downstream reach simulation.
3. Simulate combinations of discharge and downstream stage to build a per reach FIM library.
4. Mosaic per reach FIMs downstream to upstream using Flows2FIM to match both at reach discharge and downstream stage within a defined tolerance.

The framework is focused on fluvial flooding, where reach‑scale hydraulics dominate and boundary conditions can be represented by discharge and downstream stage. A key assumption for riverine (fluvial) flooding, the response to streamflow is largely confined to the local reach. Under that assumption, a sufficiently dense library spanning the range of upstream flows and downstream stage conditions should yield a close enough FIM for most expected NWM forecast scenarios without requiring forecast event specific simulations. Lake and coastal settings are only touched in the context of boundary‑condition handling for specific reaches; full treatment of those domains and other non‑fluvial processes is outside the current scope.

Under this framework, each reach model consists of a rectangular domain, an inflow boundary, a stage transfer line (STL), and an outflow boundary. The downstream reach water‑surface elevation (WSEL) provides downstream boundary condition to the upstream reach at the STL, enforcing a water‑surface tie‑in to propagate backwater effects. In the “simple case” this structure covers most reaches. Special cases such as lake/coastal reaches, large floodplains, or hydraulically coupled reaches require modifications described later in this report.

![Example geometry for a single reach-based model showing inflow, outflow, and stage transfer lines](methodology-report/image2.png)

*Figure 2. Example geometry for a single reach-based model showing inflow, outflow, and stage transfer lines.*


Each library entry is treated as quasi‑steady for a given discharge and downstream stage. In practice, this means the maps represent steady snapshots of inundation rather than the full time evolution of a flood wave, which aligns with the library‑lookup paradigm.

Operationally, this library framework relies on a simple architecture that mirrors Flows2FIM: (1) pre‑computed FIM libraries of rasters indexed by reach, discharge, and downstream stage; (2) a rating‑curve database that relates discharge and downstream WSEL to the library indices; and

During operations, Flows2FIM assembles these maps by traversing the river network downstream‑to‑upstream and selecting the closest library entry for each reach based on discharge and downstream conditions. This is a lightweight extraction and mosaicking step that runs in seconds without new hydraulic modeling. The separation keeps heavy computation offline and makes operational assembly tractable.

![Overview of discretizing a river system into reach-based 2D hydrodynamic models](methodology-report/image3.png)
*Figure 3. Overview of discretizing a river system into reach based 2D hydrodynamic models. The outer images show development of individual models and their geometries; the central image depicts how these models come together to form a mosaicked FIM for the full network.*


Figure 4 and 5 show how pre‑generated libraries are used to generate FIMs for diverse flow scenarios.

![Example composite FIM for a low-magnitude flood along all reaches](methodology-report/image4.png)
*Figure 4. Example composite FIM for a low‑magnitude flood along all reaches.*

![Example composite FIM for high-magnitude mainstem and low-magnitude tributary conditions](methodology-report/image5.png)
*Figure 5. Example composite FIM for a high‑magnitude event along the mainstem and a low‑magnitude event along a tributary.*

The framework is intentionally implementation agnostic; any hydraulic model or automation tooling can be used to generate individual FIMs as long as the outputs adhere to the library interface described above.

The framework is also flexible about internal model details. For example, DEM conditioning or sub‑grid parameterization can be applied within an individual reach model without changing how the broader system functions. This creates a path for regional experts (e.g., RFCs) to improve reach models in their areas while remaining interoperable with the national library. Realizing this at scale will require governance, QA/QC, and cloud‑infrastructure design, which is beyond the scope of the current work.

## Methodology Development
The primary goal of Phase 1 was to define a defensible, automatable methodology for reach-based 2D FIM library development. This phase was not intended to produce large-scale libraries or automation pipeline. Instead, it was intended to establish a coherent technical foundation that could be implemented, tested, reviewed, and refined before broader deployment.

Methodology development was carried out as an iterative, evidence-driven process. Engineering discussions were used to frame initial options, and early pilot runs were then used to establish a baseline configuration and identify where that baseline functioned well and where it failed under different hydraulic settings. To support this work, lightweight internal tools were developed (described below in the Tooling subsection) and used throughout testing to make setup and comparison more repeatable. As testing expanded, cyclic decision patterns emerged, where choices that improved one case degraded another. To manage that, decision tracking was formalized through System Decision Records (SDR), which preserved decision evolution and rationale and made it easier to revisit why specific design choices were made.

Note that model calibration was not included in scope for this task and should be treated as future work (other limitations and challenges are discussed in a later section). This emphasis reflects operational reality. The primary objective of forecast mapping is reliable capture of inundation patterns at large scale, with the understanding that some depth and extent error will remain. In addition, uncertainty from upstream meteorological and hydrological components in the modeling chain limits the practical value of pursuing very high precision in the mapping step alone. The methodology is therefore framed to balance physical realism with automation feasibility.

The subsections below describe the source datasets and derived inputs used to build models, the tooling that supported development, and the candidate 2D hydraulic models considered for the task at hand, followed by the key methodology decisions and the evidence used to support each one.

### Source Data and Derived Inputs
For current pilots, topography is sourced from USGS 3DEP and resampled to 10 m, surface roughness is derived from MRLC NLCD, and reach geometry/connectivity is sourced from the NHF (NextGen HydroFabric). Pilot discharge inputs were pulled from USGS gages and StreamStats to accelerate testing; production implementation is expected to use NWM retrospective analysis AEP (Annual Exceedance Probability) flows.

For roughness conversion, Table 1 lists the selected NLCD-to-Manning's n lookup, derived from USACE HEC-RAS guidance (U.S. Army Corps of Engineers, n.d.).

**Table 1. NLCD land-cover values to Manning's n roughness lookup**

| NLCD Value | NLCD Class | Manning's n |
| --- | --- | --- |
| 11 | Open Water | 0.04 |
| 21 | Developed, Open Space | 0.04 |
| 22 | Developed, Low Intensity | 0.10 |
| 23 | Developed, Medium Intensity | 0.08 |
| 24 | Developed, High Intensity | 0.15 |
| 31 | Barren Land | 0.025 |
| 41 | Deciduous Forest | 0.16 |
| 42 | Evergreen Forest | 0.16 |
| 43 | Mixed Forest | 0.16 |
| 52 | Shrub/Scrub | 0.10 |
| 71 | Grassland/Herbaceous | 0.035 |
| 81 | Pasture/Hay | 0.03 |
| 82 | Cultivated Crops | 0.035 |
| 90 | Woody Wetlands | 0.12 |
| 95 | Emergent Herbaceous Wetlands | 0.07 |

### 2D Model Selection
An automated 2D based FIM library development pipeline will be highly dependent on the underlying 2D hydrodynamic model, so an evaluation of available 2D hydrodynamic models was necessary to gauge if these models satisfy the our practical requirements. As mentioned earlier the conceptual modeling framework is intentionally model agnostic, but any concrete implementation of this framework through an automated pipeline will be dependent on one particular 2D hydrodynamic model.

For this reason, a preliminary review of potential candidates was perfromed based on criteria that may impact large scale automation: governing equations, grid/mesh paradigm, setup automation burden, CPU/GPU performance, Linux and container support, checkpointing/hot-start support, boundary-condition flexibility, output structure, maturity, documentation quality, and licensing constraints.

Table 2 lists the summary results of the survey of 2D models and the model selection decision basis

**Table 2: 2D model survey summary**

| Model | Equations / Approach | Grid / Automation | Performance | Linux / Container | Boundary Conditions & IO | Status / Rationale |
| --- | --- | --- | --- | --- | --- | --- |
| LISFLOOD-FP | Multiple solvers; some solve shallow-water equations; some use Manning-based formulations | Gridded; automation feasible; broad community patterns | Fast; GPU support for ACC, FV1, DG2 | Linux-friendly; containerizable | Supports hydrograph, fixed inflow, free-flow (valley slope), constant or time-varying WSE; exports WSE and velocity grids; checkpointing | Continue evaluation; strong literature and tooling, good performance |
| TRITON | Full shallow-water equations (ARoe solver) | Gridded; automation feasible; maturity still developing | Very fast on GPU; weaker on CPU | Linux-friendly; containerizable | Supports hydrograph, free flow, constant WSE, normal slope, Froude number; exports depth/velocity; checkpointing | Continue evaluation; strong physics and GPU speed, less mature |
| SFINCS | Shallow-water equations with simplified formulation (convective acceleration ignored) | Gridded; HydroMT provides automated setup | Fast for large domains; performance depends on setup | Linux-friendly; containerizable | Boundary conditions supported via HydroMT workflows; standard raster outputs | Secondary candidate; strong automation, needs validation for reach-based rivers |
| TELEMAC-2D | Shallow-water equations | Mesh-based; may require code-level adjustments | Reported fast; widely used in EU | Linux-capable; containerization possible but non-trivial | Standard hydraulic BCs; IO requires integration work | Not prioritized; higher automation burden |
| HEC-RAS 2D | Shallow-water equations with sub-grid approach | Mesh-based; GUI-centric | Good for engineering studies; automation burden high | Windows-centric; Linux uncertain | Rich BCs, but IO complex | Removed; automation and data handling risks |
| RAS 2025 (alpha) | Shallow-water equations | Mesh-based; API not released | Unknown stability | Linux/API uncertain | Unknown | Removed; timeline risk |
| FastFlood | GIS-hydraulic hybrid | Gridded | Very fast (per literature) | Unknown | Outputs not aligned with hydrodynamic needs | Removed; not a 2D hydrodynamic model |
| PNNL Lagrangian | Novel research method | Unclear | Supposedly fast | Unclear | Unclear | Removed; research-grade |
| MIKE21 / FLO-2D / Delft3D / TUFLOW 3D | Hydrodynamic models | Mixed | Strong but commercial | Licensing constraints | Proprietary tooling | Removed; licensing incompatible |


Followng the model review, LISFLOOD-FP, TRITON, and SFINCS have been identified as active candidates. Although final selection is planned after focused benchmark testing of speed, stability, and feature maturity, the pilot development and automation research still required us to land on one model, so that we can develop our tooling around it and maintain focus on developing methodology and not on details of different models.

Baseon on the initial research, LISFLOOD-FP was selected for tool development. Since our choice of going through with using LISFLOOD-FP we have learned more about SFINCS and active development, this makes SFINCS a very potent candidate and in the future we plan to explore SFINCS further. TRITON as of now is least favorable candidate, mainly because (to do:).

HEC-RAS faces several challenges when it comes to large-scale cloud-based modeling backed by automation due to:
-   Dependency on Windows-based operations
-   Mesh tooling and instability
-   Mapping related to sub grid computational approach
-   Complicated data structures and storage inefficiencies

One of the primary limitations of HEC-RAS for use in the cloud is its reliance on a Windows-based graphical user interface (GUI) for model development. This dependency requires the use of Windows OS components in any automation system, which complicates cloud environments predominantly using (containerized) Linux programs. Although solutions
like Wine exist to emulate Windows applications on Linux, attempts to port HEC-RAS using Wine have had very limited success, marked by instability and unreliable performance, making it a poor choice. Likewise, mapping operations in HEC-RAS must be conducted within a Windows environment, extending the Windows OS dependency to include post processing.

Another significant hurdle is a lack of automated mesh tools available outside the HEC-RAS GUI. Mesh generation and refinement are crucial steps in hydraulic modeling with HEC-RAS, and the computations are highly sensitive to mesh-related issues. Mesh instability is a commonly known issue with HEC-RAS models, requiring manual debugging, which can be time-consuming and labor-intensive. The degree to which manual intervention would be required adds significant risk to project delivery.

Computationally, HEC-RAS utilizes a sub grid approach, which involves subdividing computational cells into smaller elements to capture detailed hydraulic information and reduce simulation time through caching of complex cell properties. This computational approach creates challenges from traditional finite volume methods in map production, as volume accounting is more complex. As a result, there are a handful of known issues with flood rasters created using HEC-RAS software, including cupping and disconnected hydraulic reaches, which would require an additional post-processing step prior to delivery.

With respect to data, the complexity of HEC-RAS\'s data structures poses significant challenges for automation. The software uses a variety of file formats, including text files, binary files, HDF files, and DSS files. This dependency complicates data management and automation, as different tools and processes are required to handle each file type. A result of this approach is data duplication across files: resulting in unnecessary redundancy that increases the storage requirements for simulations, inflating data size and complicating data handling in the cloud.

In September of 2024, USACE released the alpha version of a major update to HEC-RAS (RAS 2025). According to release notes and the HEC newsletter, the new version of software has been designed to incorporate an API and offer a Linux build for headless and containerized operations. At the time of the writing of this narrative, these features have not been published, and the Beta version has likewise not been released. While this version promises to overcome some of the cloud deployment issues noted above, it does not address the mesh, sub grid, and data issues identified as areas of risk for use in this project.

Collectively, these issues highlight the challenges HEC-RAS faces in transitioning to large-scale cloud-based modeling backed by automation.

### Tooling
Pilot work was perfromed using a lightweight automation toolchain to generate model domains, stage-transfer geometry, boundary-condition geometry, and raster inputs. The toolchain was deliberately minimal: it was designed to accelerate iteration and enforce repeatable setup patterns while methodology questions were still open. This avoided overbuilding production software before decision stability was established.

From an automation perspective, this phase also confirmed a practical distinction between 1D and 2D workflows. In 1D, cross-section placement and refinement at hydraulically sensitive locations remain highly judgment-intensive. In 2D, that effort shifts toward grid/domain definition, boundary-condition placement, and terrain conditioning. The burden does not disappear, but it is more rule-driven and therefore better suited to scalable automation once decision rules are mature.

Published large-scale automation efforts (for example, HydroMT-SFINCS workflows in NHESS) support this direction and provide external precedent that 2D setup can be industrialized when preprocessing rules are explicit and reproducible.

![Pilot tooling landing page / workflow overview](methodology-report/image7.png)
*Figure TBD. Pilot tooling used to automate model construction and review.*

### System Decision Records (SDR)
SDR provides the governance layer for methodology development. Each decision is framed as a narrow technical question, alternatives are explicitly defined, and experiments/cases are linked as evidence for selection status. This turns method development into a traceable engineering process rather than ad hoc iteration.

The practical value has been significant in three ways. First, SDR preserves reasoning so earlier choices do not need to be rediscovered when team members rotate or when similar issues reappear. Second, it enables structured revision: previously rejected alternatives can be revisited when new evidence exists, without erasing historical context. Third, it keeps open decisions visible, which helps prioritize pilot design and prevents hidden assumptions from entering automation logic.

### Glossary
Terminology used in this report follows SDR glossary definitions to keep implementation and documentation aligned. In particular, the workflow distinguishes terminal reaches, lake/coastal reaches, headwater reaches, upstream mainstem reaches, and stage transfer lines (STLs), because these terms directly control boundary-condition logic and run sequencing.

### Pilot Cases
Pilot locations were selected to stress the methodology across contrasting hydraulic and physiographic conditions rather than to maximize geographic count. The set includes small rural systems, steep headwaters, urban/structure-influenced corridors, very wide floodplains, arid channels, and lake/coastal terminal settings. Targeted SDR cases were then used to isolate known failure modes such as backwater mismatch at confluences, edge leakage, inflow artifacts, culvert-related blockage, and domain truncation.

This case design was intentional: the goal was to expose where generalized automation rules break and to use those failures to tighten decision logic. The appendix provides case-by-case summaries and figure evidence.

![Pilot site locations](methodology-report/image6.jpeg)
*Figure TBD. Locations of pilot study sites.*

### Key Decisions for Automation
Initial pilots used a simple baseline: model each reach independently, apply straightforward boundary conditions, and rely on downstream-to-upstream sequencing for hydraulic coupling. That baseline exposed predictable weaknesses. The decisions below summarize how those weaknesses were addressed and how they now shape the methodology.

#### Reach Coupling and Stage Transfer
The first major decision was whether downstream stage transfer (KWSE-informed coupling) was necessary or whether normal-depth downstream boundaries were sufficient. In confluences and stream-order mismatch settings, normal-depth-only runs consistently underpredicted downstream water-surface elevation and reduced upstream inundation extent. Stage-transfer-informed runs produced better tie-in behavior and more realistic backwater response.

As a result, downstream stage transfer is currently treated as a default requirement across reaches, not a special-case exception. This aligns with Flows2FIM’s downstream-to-upstream traversal logic and preserves compatibility with library-based operational assembly.

![KWSE vs normal depth comparison at a confluence](methodology-report/Case-001_Fig-002.png)
*Figure TBD. KWSE vs normal-depth comparison showing lower WSEL near tie-in without downstream stage transfer.*

#### Domain Edge and Boundary-Control Strategy
Applying normal depth across all perimeter edges was tested early and consistently created non-physical losses where upstream tributaries or side boundaries intersected the domain edge. The current approach restricts normal-depth outflow treatment to edge cells hydraulically informed by downstream flooding and uses reach-centerline slope for those cells. This materially reduced leakage at non-outlet locations.

For lake and coastal terminal settings, normal-depth-only boundaries also produced pooling artifacts. Current handling uses waterbody-informed edge treatment and stage-transfer-aware downstream control, with STL geometry tied to domain-waterbody intersection. Reach classification rules for lake/coastal tagging remain open.

![Water leaving the domain at non-outlet locations under normal-depth edge conditions](methodology-report/Case-001_Fig-003.png)
*Figure TBD. Water leaving the domain at non-outlet locations when normal depth is applied at all edges.*

![Lake reach normal depth run](methodology-report/Case-002_Fig-002.png)
*Figure TBD. Lake reach behavior under normal-depth boundary conditions.*

![Lake reach KWSE run](methodology-report/Case-002_Fig-003.png)
*Figure TBD. Lake reach behavior under downstream stage transfer.*

#### Stage Transfer Line (STL) Placement
Tests showed that applying stage transfer directly at the outer domain edge can create abrupt hydraulic behavior where downstream geometry or flow regime changes quickly. Using an internal STL derived from downstream WSEL contours produced more stable transitions. The current selection is one STL per reach, derived from coarse-model guidance and reused across runs for that reach.

This simplifies automation and indexing, but it introduces residual risk in highly flat or hydraulically complex reaches where one STL may not represent all flow regimes equally well.

![STL placement alternatives](methodology-report/stl-placement-alternatives.png)
*Figure TBD. Alternative STL placement geometry to reduce WSEL anomalies.*

#### Domain Construction and Expansion
Reach-divide-only domains were frequently too narrow, causing floodplain truncation and edge cutoffs. The current method starts from buffered/coarse-informed geometry and then applies elevation-informed expansion rules until edge flooding is limited relative to outlet elevation constraints. This improved continuity without defaulting to excessively large domains.

![Example of domain truncation](methodology-report/Case-004_FIG-001.png)
*Figure TBD. Flood extent truncated at domain edge when using reach-divide domains.*

![Comparison to benchmark FIM](methodology-report/Case-004_FIG-002.png)
*Figure TBD. Comparison to benchmark FIM showing edge truncation.*

#### Inflow Representation and Special Reach Handling
Point inflows at the reach start produced recurring bullseye artifacts in WSEL contours. A perpendicular inflow line on the upstream mainstem reduced these artifacts and produced smoother fields. Current defaults are a 100 m inflow line width with a 0.25 upstream-reach-length offset. Headwater treatment remains a conditional area where point inflow may still be used but requires additional constraints.

Short and hydraulically flat reaches were also problematic when modeled strictly one-by-one. Current practice merges selected continuous short reaches (based on stream order, drainage-area difference, and length thresholds) to avoid artificial segmentation effects. Flat-reach handling is still provisional and requires further rule development.

![WSEL artifacts from point inflow](methodology-report/Case-006_FIG-002.png)
*Figure TBD. Point inflow producing WSEL “bullseye” artifacts.*

![Reduced artifacts with line inflow](methodology-report/Case-006_FIG-003.png)
*Figure TBD. Line inflow reduces WSEL artifacts.*

#### Terrain Conditioning and Hydraulic Realism
Unconditioned DEMs repeatedly produced divergent flow paths and impoundment around culverts and road crossings that were not hydraulically represented in the terrain. This behavior is severe enough that a no-conditioning approach is not considered viable for production. Alternatives under evaluation include AGREEDEM channel burning, targeted road/culvert burning, and hybrid conditioning workflows.

![Divergent flowpath due to culvert obstruction](methodology-report/Case-003_FIG-002.png)
*Figure TBD. Divergent flowpath caused by unburned culverts.*

![Culvert blocking flow](methodology-report/Case-003_FIG-007.png)
*Figure TBD. Flow impounded upstream of a culvert/road crossing.*

#### Compositing, Run Control, and Remaining Open Decisions
For compositing overlapping reach rasters, the current selection is pixelwise maximum depth. This is robust and simple for operational assembly, but it can amplify local artifacts when upstream boundary errors persist.

Quasi-steady termination criteria are still open and currently treated as a proposed decision. Candidate criteria include combined mass-balance convergence (Qin approximately equal to Qout) and WSEL stabilization across final timesteps.

At the time of this report, principal open SDR items include lake/coastal reach classification logic, final DEM-conditioning method, initial-domain rule finalization, and quasi-steady stopping criteria. These are expected to be resolved during prototype automation and are the main prerequisites for moving from methodology definition to production-scale implementation.

Together, these decisions define the current method baseline and directly inform the proposed automation workflow in the next section.

## Proposed Automation Workflow
This workflow is under development and will be refined as decisions are finalized. It is designed to translate the methodology into a repeatable national-scale pipeline.

![Proposed production framework](methodology-report/image44.jpeg)
*Figure TBD. Proposed production framework for automated 2D FIM libraries.*

### Coarse Modeling
Coarse simulations are used to estimate maximum flood extents and to derive a hydraulic reach network that reflects actual inundation sources. Coarse outputs also seed initial stage surfaces for lake/coastal reaches and help identify areas where the simple reach-based framework is likely to fail.

![Coarse modeling workflow](methodology-report/image45.jpeg)
*Figure TBD. Coarse modeling workflow used to inform reach network and STL placement.*

### Initial Model Creation
For each reach, the pipeline generates inflow geometry, a model domain, a stage transfer line, and initial raster inputs. DEM and roughness rasters are prepared at 10 m resolution, and conditioning rules are applied where culverts or obstructions are likely. Domain expansion rules ensure that flood extents are not truncated at model edges.

![Initial model creation workflow](methodology-report/image46.jpeg)
*Figure TBD. Initial model creation workflow.*

### Simulation Execution
Simulation files are generated automatically for each discharge and downstream stage combination. Runs proceed downstream-to-upstream to propagate stage transfer. Quasi-steady state is evaluated using a consistent criterion. Outputs are converted into FIM rasters and stored as per-reach libraries for later mosaicking.


### Data Model
From an operational standpoint, the library structure should remain consistent with Flows2FIM conventions: a directory per reach, subdirectories per downstream stage (WSE) level, and discharge‑indexed rasters (plus a domain mask). Maintaining this structure ensures libraries remain composable in near real time and simplifies cloud storage and retrieval.

[talk about data model]

![Simulation execution workflow](methodology-report/image47.jpeg)
*Figure TBD. Simulation execution workflow.*

## Step-by-Step Example
[Placeholder: worked example with embedded QGIS maps and model inputs/outputs.]

### Comparison with 2D Map for the Area
[Placeholder: side-by-side comparison and discussion of differences.]

## Limitations and Challenges
Even with the current decisions, several issues remain recurring or require special handling. These limitations inform both the current methodology and the open decisions to be resolved during the prototype phase.

### Lack of Bathymetric Data
Effects of bathymetric data absence/presence on 2D model results.

Here, we looked at the Ohio River near Evansville, IN. Bathymetric data came from USACE eHydro. We ran a series of discharges through the 2D models for this reach and measured the resulting water surface elevations at the USGS gage here.

Results show that the “with bathymetry” model tracks closer to the observed USGS data, especially in lower‑magnitude floods. Notably, the “without bathymetry” model is above the minor flood stage for almost all discharges whereas the “with bathymetry” model only gets to minor flood stage at a ~2‑year event.

In large‑scale implementations, a common workaround is to omit explicit bathymetry and represent river channels as **sub‑grid features** within each 2D cell. In practice, this means the grid cell stores an idealized 1D channel geometry (width, depth, roughness) so flow and storage can be approximated without resolving the channel in the terrain. This can reduce data requirements and improve runtime, but it also shifts accuracy to the quality of the sub‑grid parameterization. For our workflow, this highlights a tradeoff: either invest in bathymetric data where available, or adopt sub‑grid channel representations and quantify the resulting bias, especially for lower‑magnitude flows.

![Bathymetry influence on stage accuracy](methodology-report/image28.png)
*Figure TBD. Ohio River (Evansville) comparison of WSEL with and without bathymetry.*

### Boundary Condition Artifacts
Water‑surface elevation anomalies can occur near inflow boundaries in certain geometries, and non‑physical outflows can occur when edge boundary conditions are too permissive. These artifacts can propagate into composite maps if not controlled by boundary placement, domain sizing, and STL geometry.

### Domain Truncation and Edge Effects
Domains derived strictly from reach divides can truncate flood extents and cause edge pooling. Expansion rules mitigate this, but automation remains sensitive to local topography and floodplain width.

### Confluence Sensitivity
Backwater effects and confluence geometry can produce narrower‑than‑expected FIM extents if downstream stage transfer is not enforced or if STL coverage is incomplete across the floodplain.

### Flat and Hydraulically Coupled Reaches
Flat reaches and hydraulically coupled reaches challenge the reach‑based assumption, particularly where stage changes propagate across multiple reaches or where level‑pool behavior dominates.

### Compute and Cost
Large rivers and wide floodplains can require large domains or reach eclipsing, which affects compute time, storage, and cost. This will need explicit optimization in the prototype phase.

### Volume‑Driven Areas
Some areas respond more to flood volume than peak discharge (e.g., lakes, reservoirs, and extensive floodplains). These settings require alternative handling beyond discharge‑only library selection.

Taken together, these limitations do not negate the approach. They clarify where automation needs guardrails and targeted exceptions so the system remains fit for rapid, decision‑support mapping.

## Discussion and Next Steps
This report proposes a defensible, automatable methodology grounded in pilot evidence and a structured decision process. The next phase will refine open decisions, select a production model, and implement a prototype pipeline for a HUC6-scale area. The SDR system will continue to capture decision evolution, ensuring that methodology changes are traceable and evidence-based.

The approach described here represents a significant compute effort relative to existing GIS or 1D workflows. As a result, near‑term work should prioritize optimization of methodology and cost over expanding library coverage. In practice, this means focusing on the performance envelope of the system before scaling further. Key optimization areas include model choice and solver configuration, CPU vs GPU execution trade‑offs, domain sizing and reach merging rules, use of sub‑grid or multi‑resolution techniques where appropriate, and I/O strategies that avoid writing or storing data outside the flood‑relevant extent. Decisions in these areas have outsized impacts on cost, throughput, and the feasibility of national‑scale production.

We therefore recommend a dedicated optimization and benchmarking effort in the next phase, using a prototype HUC6 to compare candidate models and configurations on representative hardware. The goal is to establish cost‑per‑reach and cost‑per‑library targets, identify bottlenecks, and refine automation rules (domain trimming, reach eclipsing, data reduction) before committing to large‑scale library generation.

Recommended next steps are best framed as a short‑term roadmap tied to time, with an emphasis on optimization before scale. A suggested sequencing is below; durations are placeholders to be adjusted based on staffing and compute availability.

**Suggested Roadmap (Time‑Phased)**
| Phase | Timing (Placeholder) | Primary Focus | Key Outputs |
| --- | --- | --- | --- |
| Phase 1 | 0–2 months | Benchmarking and cost modeling | Model speed/cost comparison (CPU vs GPU); solver configuration sensitivity; cost‑per‑reach and cost‑per‑library targets |
| Phase 2 | 2–4 months | Methodology closure | Decisions finalized for quasi‑steady state, inflow geometry, STL placement, lake/coastal classification; QA/QC acceptance metrics defined |
| Phase 3 | 4–6 months | Automation hardening | Domain expansion rules validated; reach‑merging/eclipsing criteria refined; terrain‑conditioning workflows integrated |
| Phase 4 | 6–9 months | Prototype production | End‑to‑end HUC6 pipeline run; data‑reduction strategies tested; comparison to HAND/Ripple1D baselines |

SDR updates should accompany each phase to keep decision rationale traceable.

## References
Bates, P. D., and A. P. J. De Roo (2000), A simple raster‑based model for flood inundation simulation, *Journal of Hydrology*, 236, 54–77, https://doi.org/10.1016/S0022-1694(00)00278-X.

Baugh, C., J. Colonese, C. D'Angelo, F. Dottori, J. Neal, C. Prudhomme, and P. Salamon (2024), Global river flood hazard maps, European Commission, Joint Research Centre (JRC) [Dataset], http://data.europa.eu/89h/jrc-floods-floodmapgl_rp50y-tif (accessed 12 Feb 2026).

Eilander, D., et al. (2023a), HydroMT: Automated and reproducible model building and analysis, *Journal of Open Source Software*, 8(83), 4897, https://doi.org/10.21105/joss.04897.

Eilander, D., et al. (2023b), A globally applicable framework for compound flood hazard modeling, *Natural Hazards and Earth System Sciences*, 23, 823–, https://doi.org/10.5194/nhess-23-823-2023.

NextGen Water Prediction Capabilities (NGWPC) (n.d.-a), Ripple1D (software), GitHub repository, https://github.com/NGWPC/ripple1d (accessed 12 Feb 2026).

NextGen Water Prediction Capabilities (NGWPC) (n.d.-b), flows2fim (software), GitHub repository, https://github.com/NGWPC/flows2fim (accessed 12 Feb 2026).

Sanders, B. F., O. E. J. Wing, and P. D. Bates (2024), Flooding is not like filling a bath, *Earth’s Future*, 12(12), e2024EF005164, https://doi.org/10.1029/2024EF005164.

U.S. Army Corps of Engineers (USACE) (n.d.), HEC-RAS 2D User’s Manual: Creating land cover, Manning’s n values, and impervious layers, https://www.hec.usace.army.mil/confluence/rasdocs/r2dum/6.6/developing-a-terrain-model-and-geospatial-layers/creating-land-cover-mannings-n-values-and-impervious-layers (accessed 15 Feb 2026).

U.S. Geological Survey (n.d.-a), Flood Inundation Mapping (FIM) Program, https://www.usgs.gov/mission-areas/water-resources/science/flood-inundation-mapping-fim-program (accessed 12 Feb 2026).

U.S. Geological Survey (n.d.-b), Flood Inundation Mapping Science, https://www.usgs.gov/mission-areas/water-resources/science/flood-inundation-mapping-science (accessed 12 Feb 2026).

Wing, O. E. J., et al. (2019), A flood inundation forecast of Hurricane Harvey using a continental‑scale 2D hydrodynamic model, *Journal of Hydrology X*, 4, 100039, https://doi.org/10.1016/j.hydroa.2019.100039.

## Appendices
### Test Cases
The cases below include initial pilot sites and targeted SDR cases. Each case was selected for unique characteristics or known issues. All cases follow the same format to support consistent interpretation and future updates.

#### Case A — Spring Creek near Iron City, GA (Pilot)
**Description**: Small rivers in rural agriculture, unconfined corridor, and confluences.
**Properties**: Flows: [Placeholder]. Stream orders: [Placeholder]. Slopes: [Placeholder]. Gages: USGS 02357000 (mainstem), StreamStats (tributary).
**Setting**:
![Spring Creek pilot site map](methodology-report/image8.png)
*Figure TBD. Spring Creek pilot site overview.*
![Spring Creek reach layout](methodology-report/image9.jpeg)
*Figure TBD. Reach layout for Spring Creek pilot.*
**What Was Performed**: Automated model build and manual review of STL and domain coverage.
**What Was Discovered**: Transfer lines and domains did not always span the lateral floodplain; extensions reduced boundary ponding.
**Issues Encountered**: Truncated flood extents at domain edges; STL coverage gaps in confluence areas.

![Extended domain and STL example](methodology-report/image10.png)
*Figure TBD. Example of domain/STL extension to cover lateral floodplain.*
![Transfer line extension example](methodology-report/image11.png)
*Figure TBD. Transfer line extended to match floodplain extent.*
![Generated FIM example](methodology-report/image12.png)
*Figure TBD. Example FIM output from Spring Creek pilot.*

#### Case B — Quartz Creek near Ohio City, CO (Pilot)
**Description**: Steep terrain with multiple headwaters and tributaries.
**Properties**: Flows: 500‑year (pilot). Stream orders: [Placeholder]. Slopes: [Placeholder]. Gage: USGS 09118000 (mainstem).
**Setting**:
![Quartz Creek pilot site map](methodology-report/image13.png)
*Figure TBD. Quartz Creek pilot site overview.*
**What Was Performed**: Automated STL and domain creation with manual corrections.
**What Was Discovered**: Several STLs needed trimming or redrawing to avoid artificial tie‑ins; some required extension to cover the floodplain.
**Issues Encountered**: Artificial floodplain tie‑ins at confluences when STL overlapped the wrong divide.

![Transfer line trim example](methodology-report/image14.png)
*Figure TBD. STL trimmed to avoid incorrect floodplain tie‑in.*
![Transfer line redraw example](methodology-report/image15.png)
*Figure TBD. STL redrawn to align with correct floodplain.*
![Transfer line update example](methodology-report/image16.png)
*Figure TBD. STL updated to overlap receiver floodplain.*
![Generated FIM example](methodology-report/image17.png)
*Figure TBD. Example FIM output from Quartz Creek pilot.*

#### Case C — Delaware River at Trenton, NJ (Pilot)
**Description**: Urban mainstem and tributary confluence with structures.
**Properties**: Flows: 100‑year (pilot). Stream orders: [Placeholder]. Slopes: [Placeholder]. Gages: USGS 01463500 (mainstem), 01464000 (tributary).
**Setting**:
![Delaware River pilot site map](methodology-report/image18.png)
*Figure TBD. Delaware River pilot site overview.*
**What Was Performed**: Automated model build with manual review; culvert‑burning comparison.
**What Was Discovered**: Small reaches fully inundated at low flows were inefficient and were eclipsed or merged; culvert burning materially changed backwater and inundation.
**Issues Encountered**: Structure‑related impoundment in unconditioned DEM; wide floodplains exceeded default domain/STL extents.

![Eclipsed reaches example](methodology-report/image19.png)
*Figure TBD. Example of eclipsed/merged reaches in urban setting.*
![Overlay of modeled rasters](methodology-report/image20.png)
*Figure TBD. Overlay of modeled rasters for tie‑in review.*
![Culvert‑burning terrain comparison](methodology-report/image21.jpeg)
*Figure TBD. Terrain comparison with and without culvert burning.*
![Culvert impact on inundation](methodology-report/image22.jpeg)
*Figure TBD. Impact of culvert representation on inundation extent.*

#### Case D — Gila River, AZ (Pilot)
**Description**: [Placeholder: site description.]
**Properties**: Flows: [Placeholder]. Stream orders: [Placeholder]. Slopes: [Placeholder]. Gages: [Placeholder].
**Setting**: [Placeholder: site map and reach layout.]
**What Was Performed**: [Placeholder.]
**What Was Discovered**: [Placeholder.]
**Issues Encountered**: [Placeholder.]

#### Case E — Ohio River at Evansville, IN (Pilot)
**Description**: Large river with very wide floodplain and low slope.
**Properties**: Flows: 10‑, 50‑, 100‑, 500‑year. Stream orders: [Placeholder]. Slopes: ~0.00003 (pilot). DEM: 30 m (pilot).
**Setting**:
![Ohio River pilot site overview](methodology-report/image23.jpeg)
*Figure TBD. Ohio River pilot site overview.*
**What Was Performed**: Coarse model run to guide STL placement; reach grouping for large‑river handling.
**What Was Discovered**: Hydrofabric divides were too narrow for STLs; coarse models provided appropriate WSEL contours for STL placement.
**Issues Encountered**: Inefficient overlap when STLs span full floodplain; bathymetry limitations affected stage accuracy.

![FEMA floodplain context](methodology-report/image24.jpeg)
*Figure TBD. FEMA floodplain context for large‑river pilot.*
![Coarse model WSEL contours](methodology-report/image25.jpeg)
*Figure TBD. Coarse model WSEL contours used to guide STL placement.*
![Reach segmentation example](methodology-report/image26.jpeg)
*Figure TBD. Example reach segmentation for large river.*
![Large river reach eclipsing](methodology-report/image27.png)
*Figure TBD. Eclipsing reaches justified for large‑river efficiency.*
![Bathymetry sensitivity](methodology-report/image28.png)
*Figure TBD. Bathymetry influence on stage accuracy.*

#### Case F — Susquehanna River at Binghamton, NY (Pilot)
**Description**: Complex confluence with levees, divergence, and multiple flow changes.
**Properties**: Flows: 10‑, 100‑, 500‑year. Stream orders: [Placeholder]. Slopes: [Placeholder]. Gage‑weighted flows from BLE study.
**Setting**:
![Susquehanna pilot site overview](methodology-report/image29.png)
*Figure TBD. Susquehanna pilot site overview.*
**What Was Performed**: Eclipsed/merged short reaches; multi‑reach model review against FEMA BLE.
**What Was Discovered**: Strong agreement with BLE where geometry was well handled; divergence behavior challenged strict reach‑based separation.
**Issues Encountered**: Anabranching‑like spill paths; need for combined models or expanded domains in hydraulically coupled areas.

![Eclipsed reach examples](methodology-report/image30.png)
*Figure TBD. Eclipsed/merged short reaches near confluence.*
![10-year FIM](methodology-report/image31.png)
*Figure TBD. 10‑year discharge FIM example.*
![100-year FIM](methodology-report/image32.png)
*Figure TBD. 100‑year discharge FIM example.*
![500-year FIM](methodology-report/image33.png)
*Figure TBD. 500‑year discharge FIM example.*
![100-year comparison to FEMA BLE](methodology-report/image34.png)
*Figure TBD. 100‑year comparison to FEMA BLE.*
![500-year comparison to FEMA BLE](methodology-report/image35.png)
*Figure TBD. 500‑year comparison to FEMA BLE.*

#### Case G — Unnamed Wash near Hiko, NV (Pilot)
**Description**: Desert wash with steep slopes and complex flow paths.
**Properties**: Flows: 100‑year (pilot). Stream orders: [Placeholder]. Slopes: [Placeholder]. Gage: USGS 09415600 (mainstem).
**Setting**:
![Unnamed wash pilot site overview](methodology-report/image36.jpeg)
*Figure TBD. Unnamed wash pilot site overview.*
**What Was Performed**: Automated model build; review of highway crossing effects.
**What Was Discovered**: Road crossings without culvert representation caused upstream impoundment.
**Issues Encountered**: Structure‑related flow blockage; potential for divergent flow paths in arid systems.

![100-year FIM example](methodology-report/image37.jpeg)
*Figure TBD. 100‑year discharge FIM example.*
![Highway crossing location](methodology-report/image38.png)
*Figure TBD. Highway crossing location and culvert context.*
![Terrain showing road berm](methodology-report/image39.jpeg)
*Figure TBD. Terrain showing road berm without culvert.*
![Depth raster showing impoundment](methodology-report/image40.jpeg)
*Figure TBD. Depth raster showing impoundment upstream of crossing.*

#### Case H — Lake Murray, SC (Pilot)
**Description**: Lake/terminal reach behavior.
**Properties**: Flows: [Placeholder]. Stream orders: [Placeholder]. Slopes: [Placeholder].
**Setting**:
![Lake Murray pilot site overview](methodology-report/image41.jpeg)
*Figure TBD. Lake Murray pilot site overview.*
**What Was Performed**: Tested reach‑based modeling feasibility.
**What Was Discovered**: Reach‑based 2D modeling is not appropriate in large waterbodies; GIS‑based handling is preferred.
**Issues Encountered**: Discharge‑based forecasting breaks down; need for pour‑point or waterbody‑stage handling.

![Lake Murray example output](methodology-report/image42.jpeg)
*Figure TBD. Example output for lake/terminal reach setting.*

#### Case I — Plum Island Sound, MA (Pilot)
**Description**: Coastal setting influenced by tides.
**Properties**: Flows: [Placeholder]. Stream orders: [Placeholder]. Slopes: [Placeholder]. Tidal gages: [Placeholder].
**Setting**:
![Plum Island Sound pilot site overview](methodology-report/image43.jpeg)
*Figure TBD. Plum Island Sound pilot site overview.*
**What Was Performed**: Evaluated reach‑based feasibility; considered tidal stage inputs.
**What Was Discovered**: Coastal reaches are better handled with GIS‑based approaches and tidal stage inputs.
**Issues Encountered**: Reach‑based discharge methods do not capture coastal boundary dynamics.

#### Case 001 — Y‑Shape Confluence with Stream‑Order Mismatch (SDR)
**Description**: Confluence with two‑level stream‑order difference and strong backwater sensitivity.
**Properties**: Flows: 500, 6000. Stream orders: 4 and 6. Coords: (1930357, 2289467) EPSG:5070.
**Setting**:
![Y‑shape confluence setting](methodology-report/Case-001_Fig-001.png)
*Figure TBD. Y‑shape confluence with stream‑order mismatch.*
**What Was Performed**: Compared normal‑depth downstream boundary vs downstream stage transfer.
**What Was Discovered**: Normal‑depth runs underpredicted WSEL near the downstream tie‑in; stage transfer preserved backwater.
**Issues Encountered**: Lower WSEL at reach end without stage transfer.

![KWSE vs normal depth comparison](methodology-report/Case-001_Fig-002.png)
*Figure TBD. KWSE vs normal-depth comparison near tie‑in.*
![Water leaving the domain under normal-depth edges](methodology-report/Case-001_Fig-003.png)
*Figure TBD. Water leaving the domain at non‑outlet locations.*

#### Case 002 — Lake Reach (SDR)
**Description**: Riverine reach discharging into a lake.
**Properties**: Flows: 2680. Stream order: 4. Coords: (1786548, 2606475) EPSG:5070.
**Setting**:
![Lake reach setting](methodology-report/Case-002_Fig-001.png)
*Figure TBD. Lake reach setting.*
**What Was Performed**: Tested low‑slope normal‑depth boundary vs stage transfer.
**What Was Discovered**: Low‑slope normal depth caused pooling; stage transfer stabilized downstream water surface.
**Issues Encountered**: Higher WSEL near downstream end with low‑slope boundary.

![Normal-depth run](methodology-report/Case-002_Fig-002.png)
*Figure TBD. Normal-depth run for lake reach.*
![KWSE run](methodology-report/Case-002_Fig-003.png)
*Figure TBD. Downstream stage transfer run for lake reach.*
![Low-slope boundary test](methodology-report/Case-002_Fig-004.png)
*Figure TBD. Low-slope boundary condition causing pooling.*

#### Case 003 — Small Culverts (SDR)
**Description**: Small culverts not represented in DEM caused divergent flow paths and impoundment.
**Properties**: Flows: 36.75. Stream order: 1. Coords: (1796329.9, 2607407.4) EPSG:5070.
**Setting**:
![Small culverts setting](methodology-report/Case-003_FIG-001.png)
*Figure TBD. Small culverts case setting.*
**What Was Performed**: Ran models with unmodified DEM and compared to expected flowpaths.
**What Was Discovered**: Unburned culverts diverted flow and reduced downstream inundation.
**Issues Encountered**: Divergent flowpath; culvert blocking flow.

![Divergent flowpath example](methodology-report/Case-003_FIG-002.png)
*Figure TBD. Divergent flowpath due to unburned culverts.*
![Culvert blocking flow](methodology-report/Case-003_FIG-007.png)
*Figure TBD. Flow impounded by culvert obstruction.*
![Culvert blocking flow (alternate view)](methodology-report/Case-003_FIG-008.png)
*Figure TBD. Additional example of culvert obstruction impacts.*

#### Case 004 — Model Domain Example (SDR)
**Description**: Reach‑divide domain truncated flood extent.
**Properties**: Flows: 2344. Stream order: 4. Coords: (1798555, 2602987) EPSG:5070.
**Setting**:
![Model domain example setting](methodology-report/Case-004_FIG-001.png)
*Figure TBD. Model domain example showing truncation.*
**What Was Performed**: Built domain from reach divide and compared to benchmark.
**What Was Discovered**: Floodplain extent cut off at domain edges.
**Issues Encountered**: FIM cutting off arbitrarily at edges.

![Benchmark comparison](methodology-report/Case-004_FIG-002.png)
*Figure TBD. Comparison to benchmark FIM.*

#### Case 005 — Model Domain Example 2 (SDR)
**Description**: Tributary water pooled against mainstem domain edge.
**Properties**: Flows: 52.8. Stream order: 1. Coords: (1811265, 2594919) EPSG:5070.
**Setting**:
![Model domain example 2 setting](methodology-report/Case-005_FIG-001.png)
*Figure TBD. Tributary pooling against mainstem domain edge.*
**What Was Performed**: Reviewed domain behavior during modeled event.
**What Was Discovered**: Edge pooling can occur without hydraulic error but must be handled in automation.
**Issues Encountered**: Potential edge pooling artifacts.

#### Case 006 — Inflow Boundary Conditions (SDR)
**Description**: Inflow geometry effects on WSEL artifacts.
**Properties**: Flows: 13,500. Stream order: 6. Coords: (1903629, 2354784) EPSG:5070. USGS gage 01172000.
**Setting**:
![Inflow boundary conditions setting](methodology-report/Case-006_FIG-001.png)
*Figure TBD. Inflow boundary conditions case setting.*
**What Was Performed**: Compared point vs line inflow geometries at multiple locations.
**What Was Discovered**: Point inflows produced bullseye WSEL artifacts; line inflows reduced artifacts.
**Issues Encountered**: Water‑surface elevation anomalies near inflow boundary.

![Point inflow artifacts](methodology-report/Case-006_FIG-002.png)
*Figure TBD. Point inflow producing WSEL artifacts.*
![Line inflow (upstream mainstem)](methodology-report/Case-006_FIG-003.png)
*Figure TBD. Line inflow on upstream mainstem.*
![Line inflow at reach start](methodology-report/Case-006_FIG-004.png)
*Figure TBD. Line inflow at reach start.*
