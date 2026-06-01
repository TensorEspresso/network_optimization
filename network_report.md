# Network Optimization Report

**Michigan Provider Network — Anchor + Small Entity Build Analysis**

*Generated: 2026-06-01*

---

## Executive Summary

Using a deterministic greedy addition algorithm with steepest ascent optimization, we identified an optimal provider network of **6 health systems** covering **4,365 members** across **6 Michigan counties**. The network uses a large anchor (250+ providers) supplemented by smaller entities (25-249 providers) to maximize coverage while keeping network size lean.

| Metric | Value |
|---|---|
| Entities selected | 6 |
| Total providers | 5,585 |
| Final composite score | **82.39%** |
| Final access score | **95.30%** |
| Coverage pairs at 90%+ | 58 of 66 (87.9%) |
| Optimization time | 86.8s |



---

## Methodology

### Algorithm

The optimizer uses a greedy addition approach with steepest ascent:

1. **Phase 1 (Anchor Selection)**: From 35 entities with 250+ providers, evaluate all candidates and select the single entity that maximizes the composite score.
2. **Phase 2 (Build-Out)**: From 329 entities with 25-249 providers, iteratively add the entity that provides the greatest score improvement, one at a time, for 5 rounds.

Each round evaluates every candidate by computing exact coverage across all 66 county-specialty threshold pairs using BallTree spatial indexing.

### Scoring

**Composite score** = weighted combination of:
- **Access** (70% weight): Mean coverage percentage across all county-specialty thresholds
- **Effectiveness** (15% weight): Normalized provider effectiveness scores
- **Efficiency** (15% weight): Normalized provider efficiency scores

**Coverage**: A member is covered for a given specialty if any matching provider exists within the threshold distance for their county. Thresholds range from 10 miles (family practice, internal medicine) to 25 miles (neurology, pulmonology, endocrinology).

### Data

- **Provider pool**: 99,132 providers across 13,842 entities, 46 specialties
- **Members**: 4,365 across 6 counties (Livingston, Macomb, Monroe, Oakland, Washtenaw, Wayne)
- **Thresholds**: 66 requirements across 1 state (MI), 10 specialties
- **Entity filter**: Anchor from 250+ providers, additions from 25-249 providers

---

## Entity Selection Results

### Anchor Selection

From 35 candidates with 250+ providers each:

| Rank | Entity | Providers | Score | Δ Score | Access |
|---|---|---|---|---|---|
| #1 | **Henry Ford Health** | 5,135 | 76.40% | +76.40 | 87.04% |

Henry Ford Health was selected as the anchor, providing immediate coverage across the majority of threshold pairs with 5,135 providers. At 87.04% access, it establishes a strong foundation.

### Sequential Additions

From 329 candidates with 25-249 providers each, the algorithm selected 5 additional entities:

| Rank | Entity | Providers | Score | Δ Score | Access |
|---|---|---|---|---|---|
| #2 | **Concentra Urgent Care** | 5,252 | 79.55% | +3.15 | 91.35% |
| #3 | **TeamHealth** | 5,447 | 80.71% | +1.16 | 92.95% |
| #4 | **Cleveland Clinic** | 5,509 | 81.44% | +0.73 | 93.96% |
| #5 | **Alzohaili Medical Consultants** | 5,544 | 81.93% | +0.49 | 94.67% |
| #6 | **Dermatology Specialists of Canton** | 5,585 | 82.39% | +0.46 | 95.30% |

### Diminishing Returns

Each successive addition yields smaller gains:

- **Round 1→2**: +3.15 points (largest jump — filling major coverage gaps)
- **Round 2→3**: +1.16 points (half the previous gain)
- **Round 3→4**: +0.73 points (continuing decay)
- **Round 4→5**: +0.49 points (marginal improvement)
- **Round 5→6**: +0.46 points (near convergence)

---

## Network Composition

### Selected Entities

| Entity | Providers | % of Network | Role |
|---|---|---|---|
| Henry Ford Health | 5,135 | 91.9% | Anchor |
| Concentra Urgent Care | 117 | 2.1% | Addition |
| TeamHealth | 195 | 3.5% | Addition |
| Cleveland Clinic | 62 | 1.1% | Addition |
| Alzohaili Medical Consultants | 35 | 0.6% | Addition |
| Dermatology Specialists of Canton | 41 | 0.7% | Addition |
| **Total** | **5,585** | **100%** | |

Henry Ford Health dominates the network at 92% of providers. The 5 additions contribute only 450 providers total — each filling specific specialty gaps efficiently.

---

## Coverage Analysis

**58 of 66 threshold pairs (87.9%) meet the 90% coverage threshold.**

### Coverage Gaps (< 90%)

| County | Specialty | Coverage | Members Uncovered |
|---|---|---|---|
| Monroe | General Practice | 28.2% | 102 |
| Monroe | Dermatology | 54.9% | 64 |
| Monroe | Gynecology, OB/GYN | 62.0% | 54 |
| Monroe | Family Practice | 69.0% | 44 |
| Monroe | Endocrinology | 69.7% | 43 |
| Monroe | Cardiology | 82.4% | 25 |
| Monroe | Internal Medicine | 85.2% | 21 |
| Monroe | Orthopedic Surgery | 87.3% | 18 |

Monroe county is the primary gap area — all 8 uncovered specialty pairs are there. The county has 142 members, and the small-entity network struggles to cover it due to distance from Detroit-area providers.

### Full Coverage Table

| County | Specialty | Coverage | Members Covered | Total Members |
|---|---|---|---|---|
| Livingston | Cardiology | 100% | 200 | 200 |
| Livingston | Dermatology | 100% | 200 | 200 |
| Livingston | Endocrinology | 100% | 200 | 200 |
| Livingston | Family Practice | 100% | 200 | 200 |
| Livingston | General Practice | 100% | 200 | 200 |
| Livingston | Gynecology, OB/GYN | 100% | 200 | 200 |
| Livingston | Internal Medicine | 100% | 200 | 200 |
| Livingston | Neurology | 100% | 200 | 200 |
| Livingston | Orthopedic Surgery | 100% | 200 | 200 |
| Livingston | Psychiatry | 100% | 200 | 200 |
| Livingston | Pulmonology | 100% | 200 | 200 |
| Macomb | Cardiology | 100% | 890 | 890 |
| Macomb | Dermatology | 100% | 890 | 890 |
| Macomb | Endocrinology | 100% | 890 | 890 |
| Macomb | Family Practice | 100% | 890 | 890 |
| Macomb | General Practice | 100% | 890 | 890 |
| Macomb | Gynecology, OB/GYN | 100% | 890 | 890 |
| Macomb | Internal Medicine | 100% | 890 | 890 |
| Macomb | Neurology | 100% | 890 | 890 |
| Macomb | Orthopedic Surgery | 100% | 890 | 890 |
| Macomb | Psychiatry | 100% | 890 | 890 |
| Macomb | Pulmonology | 100% | 890 | 890 |
| Monroe | Cardiology | 82.4% | 117 | 142 |
| Monroe | Dermatology | 54.9% | 78 | 142 |
| Monroe | Endocrinology | 69.7% | 99 | 142 |
| Monroe | Family Practice | 69.0% | 98 | 142 |
| Monroe | General Practice | 28.2% | 102 | 142 |
| Monroe | Gynecology, OB/GYN | 62.0% | 88 | 142 |
| Monroe | Internal Medicine | 85.2% | 121 | 142 |
| Monroe | Neurology | 100% | 142 | 142 |
| Monroe | Orthopedic Surgery | 87.3% | 124 | 142 |
| Monroe | Psychiatry | 100% | 142 | 142 |
| Monroe | Pulmonology | 100% | 142 | 142 |
| Oakland | Cardiology | 100% | 1188 | 1188 |
| Oakland | Dermatology | 100% | 1188 | 1188 |
| Oakland | Endocrinology | 100% | 1188 | 1188 |
| Oakland | Family Practice | 100% | 1188 | 1188 |
| Oakland | General Practice | 100% | 1188 | 1188 |
| Oakland | Gynecology, OB/GYN | 100% | 1188 | 1188 |
| Oakland | Internal Medicine | 100% | 1188 | 1188 |
| Oakland | Neurology | 100% | 1188 | 1188 |
| Oakland | Orthopedic Surgery | 100% | 1188 | 1188 |
| Oakland | Psychiatry | 100% | 1188 | 1188 |
| Oakland | Pulmonology | 100% | 1188 | 1188 |
| Washtenaw | Cardiology | 100% | 552 | 552 |
| Washtenaw | Dermatology | 100% | 552 | 552 |
| Washtenaw | Endocrinology | 100% | 552 | 552 |
| Washtenaw | Family Practice | 100% | 552 | 552 |
| Washtenaw | General Practice | 100% | 552 | 552 |
| Washtenaw | Gynecology, OB/GYN | 100% | 552 | 552 |
| Washtenaw | Internal Medicine | 100% | 552 | 552 |
| Washtenaw | Neurology | 100% | 552 | 552 |
| Washtenaw | Orthopedic Surgery | 100% | 552 | 552 |
| Washtenaw | Psychiatry | 100% | 552 | 552 |
| Washtenaw | Pulmonology | 100% | 552 | 552 |
| Wayne | Cardiology | 100% | 1393 | 1393 |
| Wayne | Dermatology | 100% | 1393 | 1393 |
| Wayne | Endocrinology | 100% | 1393 | 1393 |
| Wayne | Family Practice | 100% | 1393 | 1393 |
| Wayne | General Practice | 100% | 1393 | 1393 |
| Wayne | Gynecology, OB/GYN | 100% | 1393 | 1393 |
| Wayne | Internal Medicine | 100% | 1393 | 1393 |
| Wayne | Neurology | 100% | 1393 | 1393 |
| Wayne | Orthopedic Surgery | 100% | 1393 | 1393 |
| Wayne | Psychiatry | 100% | 1393 | 1393 |
| Wayne | Pulmonology | 100% | 1393 | 1393 |

---

## Recommendations

### To Cover Monroe County

The 8 uncovered specialty pairs are all in Monroe county (142 members). Options:

1. **Add a Monroe-based entity**: A local health system with general practice, dermatology, and OB/GYN providers would close all gaps in one addition.
2. **Increase thresholds for Monroe**: If Monroe's thresholds are increased from 10-15 miles to 20-25 miles, existing Detroit-area providers may reach further into the county.
3. **Accept the gap**: If Monroe members can be served through referral to nearby Toledo, OH providers, the gap may be acceptable.

### Network Efficiency

The small-entity network is remarkably efficient:
- **5,585 providers** total (Henry Ford anchor + 5 small-entity additions)
- **95.30% access** covers 4,160 of 4,365 members
- Uncovered members are concentrated in Monroe (205 unique members across 8 specialties)

### Next Steps

1. Evaluate Monroe-specific additions to close remaining gaps
2. Test with different weight configurations (e.g., higher access weight)
3. Consider swap phase to optimize entity mix further
4. Validate provider counts against actual contract eligibility
