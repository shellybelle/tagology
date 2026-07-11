# tagology

*A Semantic Web publishing and knowledge engineering workbench built around a BF-hypergraph ontology.*

> **Current Status**
>
> This repository contains the current implementation of tagology's core engine. It focuses on semantic modeling, ontology design, RDF generation, and sparse hypergraph construction. The broader semantic publishing workbench is under active development.

---

## Overview

tagology explores a simple idea:

> **Every property-value pair is a tag.**

Rather than treating tags as metadata attached to objects, tagology treats them as first-class semantic structures. Objects become collections of tags, and those tags become the foundation for organizing, navigating, and publishing knowledge.

Structured datasets are transformed into RDF and a corresponding BF-hypergraph, allowing the same semantic model to support both Linked Data publication and computational analysis.

---

## Current Capabilities

- Transform structured datasets into RDF and semantic hypergraphs
- Model knowledge using a custom BF-hypergraph ontology
- Generate RDF from structured data
- Load and query graphs through an embedded RDF triplestore
- Build sparse hypergraph incidence matrices
- Generate reusable node and hyperarc indexes
- Validate the ingestion pipeline using a large U.S. Supreme Court dataset

---

## BF-Hypergraph Ontology

tagology models knowledge using a **Backward-Forward (BF) Hypergraph**.

Rather than representing relationships as simple binary edges, the ontology defines two complementary classes of directed hyperarcs.

### HAS-A Hyperarcs (Forward)

A **HAS-A** hyperarc consists of:

- one **tail**
- one or more **heads**

It represents an object and the tags that describe it.

```text
          Supreme Court Case
                  │
                  ▼
{1954, Education, Federal, Unanimous}
```

Semantic interpretation:

> **An object HAS many tags.**

### IS-A Hyperarcs (Backward)

An **IS-A** hyperarc consists of:

- one or more **tails**
- one **head**

It represents semantic classification by grouping related nodes under a shared concept.

```text
{1954, 1955, 1956, ...}
            │
            ▼
      Decision Year
```

or

```text
{Brown, Roe, Gideon, ...}
            │
            ▼
    Supreme Court Case
```

Semantic interpretation:

> **Many related nodes IS-A a shared semantic concept.**

Together these complementary hyperarcs form a BF-hypergraph.

Every property-value tag participates in both directions:

- **HAS-A** hyperarcs describe an object through its tags.
- **IS-A** hyperarcs organize tags and objects into shared semantic concepts.

These relationships are represented explicitly in RDF while simultaneously mapped onto a signed sparse incidence matrix for efficient computation.

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
RDF
        │
        ▼
Embedded Triplestore
        │
        ▼
Sparse Incidence Matrix
        │
        ▼
Foundation for Semantic Analysis
```

---

## Technology

- Python
- RDF / Turtle
- SPARQL
- RDFLib
- PyOxigraph
- SciPy
- Pandas

---

## Looking Ahead

The current repository implements tagology's semantic modeling engine.

The broader tagology project is intended to become a semantic publishing and knowledge engineering workbench for Linked Data.

Rather than requiring users to author RDF directly, tagology will use its BF-hypergraph representation and incidence matrix as an interactive semantic workspace where users can:

- Import structured datasets
- Discover duplicate concepts
- Normalize property-value tags
- Choose canonical labels
- Establish Linked Data connections
- Curate ontologies
- Publish interoperable RDF datasets

In this model, the incidence matrix is more than a computational representation—it becomes the analytical engine that helps users improve the semantic quality of their data before publication.

---

## Design Philosophy

Most Semantic Web tools assume users already know how to model and publish RDF.

tagology begins one step earlier.

It explores how structured data can be transformed into semantic knowledge through property-value tags, organized using a BF-hypergraph ontology, analyzed computationally, and ultimately published as interoperable Linked Data.

Rather than replacing existing Semantic Web standards, tagology is intended to complement them by providing a practical semantic modeling workflow before publication.
