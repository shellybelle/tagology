````markdown
# Tagology

*A semantic publishing engine built on a BF-hypergraph ontology.*

> **Current Status**
>
> This repository contains the current implementation of Tagology's core engine. It focuses on semantic modeling, ontology design, RDF generation, and sparse hypergraph construction. The broader publishing workbench is under active development.

---

## Overview

Tagology explores a simple idea:

> **Every property-value pair is a tag.**

Rather than treating tags as metadata attached to objects, Tagology treats them as first-class semantic structures. Objects become collections of tags, and those tags become the foundation for organizing, navigating, and ultimately publishing knowledge.

The current engine combines Semantic Web technologies with BF-hypergraphs and sparse matrix representations to build a semantic model that is both machine-readable and computationally efficient.

---

## Current Capabilities

- Transform structured datasets into semantic hypergraphs
- Model knowledge using a custom BF-hypergraph ontology
- Generate RDF/Turtle from structured data
- Load and query graphs through an embedded RDF triplestore
- Build sparse hypergraph incidence matrices
- Generate reusable node and hyperarc indexes
- Validate the complete pipeline using a large U.S. Supreme Court dataset 
---

## BF-Hypergraph Ontology

Tagology models knowledge using a **Backward-Forward (BF) Hypergraph**.

Rather than representing relationships as simple binary edges, the ontology defines two complementary semantic hyperarc types.

### HAS-A Hyperarcs (Forward)

A **HAS-A** hyperarc is a forward hyperarc consisting of:

- one **tail**
- one or more **heads**

It represents an object and every tag describing that object.

```text
          Supreme Court Case
                  │
                  ▼
{1954, Education, Federal, Unanimous}
```

Semantic interpretation:

> **An object has many tags.**

### IS-A Hyperarcs (Backward)

An **IS-A** hyperarc is a backward hyperarc consisting of:

- one or more **tails**
- one **head**

It represents every object sharing a semantic tag.

```text
{Brown, Roe, Gideon}
          │
          ▼
 Constitutional Law
```

Semantic interpretation:

> **Many objects share one semantic concept.**

Together these complementary hyperarcs form a BF-hypergraph.

Every property-value tag participates in both directions:

- **HAS-A** hyperarcs describe an object.
- **IS-A** hyperarcs organize objects through shared semantic meaning.

The ontology represents these relationships explicitly using RDF, while the same structure maps directly onto a signed sparse incidence matrix for efficient analysis.

---

## Architecture

```text
Structured Data
        │
        ▼
Property-Value Tags
        │
        ▼
BF-Hypergraph Ontology
        │
        ▼
RDF / Turtle
        │
        ▼
Embedded Triplestore
        │
        ▼
Sparse Incidence Matrix
        │
        ▼
Semantic Analysis
```

---

## Technology

- Python
- RDF / Turtle
- SPARQL
- rdflib
- PyOxigraph
- SciPy
- Pandas

---

## Looking Ahead

The current repository implements Tagology's semantic modeling engine.

The broader Tagology project is intended to become a semantic publishing workbench for Linked Data.

Rather than requiring users to author RDF directly, Tagology will use its BF-hypergraph representation and incidence matrix as an interactive semantic workspace where users can:

- import structured datasets
- discover duplicate concepts
- refine and normalize property-value tags
- choose canonical labels
- establish Linked Data connections
- curate ontologies
- publish interoperable RDF datasets

In this model, the incidence matrix is more than a computational representation—it becomes the analytical engine that helps users improve the semantic quality of their data before publication.

---

## Design Philosophy

Most Semantic Web tools assume users already know how to model and publish RDF.

Tagology begins one step earlier.

It explores how semantic knowledge can be organized around property-value tags, analyzed as a BF-hypergraph, and refined through computational assistance before being published as interoperable Linked Data.

The long-term goal is not simply to build another graph database, but to lower the barrier to creating high-quality semantic knowledge.
````
