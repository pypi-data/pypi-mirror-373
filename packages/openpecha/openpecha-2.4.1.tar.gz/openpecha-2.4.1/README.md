# OpenPecha Toolkit V2

<p align="center">
  <a href="https://openpecha.org"><img src="https://avatars.githubusercontent.com/u/82142807?s=400&u=19e108a15566f3a1449bafb03b8dd706a72aebcd&v=4" alt="OpenPecha" width="150"></a>
</p>

<h3 align="center">Toolkit V2</h3>

A Python package for working with stand-off text annotations in the [OpenPecha](https://openpecha.org) framework, built around the Stand-off Text Annotation Model (STAM). Toolkit V2 features robust parsing, transformation, and serialization of annotated buddhist textual corpora.

---

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Key Concepts](#key-concepts)
- [Getting Started & Usage Guide](#getting-started--usage-guide)
- [Tutorial](#Tutorial)
- [Serializer](#serializer)
- [API Reference](#api-reference)
- [Diving Deeper](#diving-deeper)
- [Contributing](#contributing)
- [License](#license)
- [Project Owners](#project-owners)

---

## Introduction

**Toolkit V2** is the next-generation Python toolkit for managing annotated texts in the OpenPecha ecosystem. It provides:
- Tools for creating, editing, and serializing annotated corpora using the STAM model.
- Support for multiple annotation types (segmentation, alignment, pagination, language, etc.).
- Parsers for various input formats (DOCX, OCR, Pedurma, etc.).
- Serializers for exporting annotated data.

**STAM (Stand-off Text Annotation Model)** is a flexible data model for representing all information about a text as stand-off annotations, keeping the base text and annotations separate for maximum interoperability.

**OpenPecha Backend** hosted on Firebase, serves as the central storage system for texts and their corresponding annotations. While the toolkit handles parsing, editing, and serialization, all storage, access, and import operations are managed by the backend.

---

## Installation

**Stable version:**
```bash
pip install openpecha
```

**Development version:**
```bash
pip install git+https://github.com/OpenPecha/toolkit-v2.git
```

---
## Key Concepts

### Pecha
A Pecha is the core data model representing a text corpus with its annotations and metadata. Each Pecha:
- Has a unique ID (8-digit UUID)
- Contains one or more base texts
- Stores multiple annotation layers
- Includes metadata (title, author, language, etc.)
- Can be created from scratch or parsed from various formats (DOCX, OCR, etc.)

```Pecha (P0001)
├── metadata.json
├── base/
│   ├── base1.txt
│   └── base2.txt
└── layers/
    ├── segmentation-1234.json
    ├── alignment-5678.json
    ├── pagination-9012.json
    └── footnote-3456.json
```

Example of a Pecha's internal structure:
```Pecha (P0001)
├── metadata.json
│   ├── id: "P0001"
│   ├── title: {"en": "Sample Text", "bo": "དཔེ་ཚན།"}
│   ├── author: "Author Name"
│   └── language: "bo"
├── base/
│   └── base1.txt
│       └── "ཨོཾ་མ་ཎི་པདྨེ་ཧཱུྃ།..."
└── layers/
    ├── Segmentation-1234.json
    │   └── {"index": 1, "span": {"start": 0, "end": 10}, ...}
    ├── Alignment-5678.json
    │   └── {"alignment_index": "1-2", "span": {"start": 0, "end":   20}, ...}
    └── Pagination-9012.json
        └── {"page": 1, "span": {"start": 0, "end": 100}, ...}
```

### Layer
A Layer is a collection of annotations of a specific type for a given base text. Key features:
- Each layer has a specific type (e.g., Segmentation, Alignment, Pagination)
- Layers are stored as JSON files in the STAM format
- Common layer types include:
  - Segmentation: Divides text into meaningful segments
  - Alignment: Maps segments between different texts (e.g., root text and commentary)
  - Pagination: Marks page boundaries
  - Language: Indicates language of text segments
  - Footnote: Contains footnote annotations

### STAM (Stand-off Text Annotation Model)
STAM is the underlying data format for storing annotations. It:
- Keeps base text and annotations separate
- Uses a flexible JSON structure
- Supports multiple annotation types
- Enables interoperability between different systems
- Allows for complex annotation relationships

## Alignment Transfer
Alignment refers to mapping relationships between two or more texts. This process is crucial for creating parallel texts, which are widely used in translation, commentary analysis, and language learning. Alignments help link corresponding sections across different versions or types of texts—whether it's between a root text and its translation, a commentary, or other related materials.

---

## Getting Started & Usage Guide

To get started and explore all features, see the [Getting Started & Usage Guide](docs/usage.md).

---

## Tutorial Guide

To see a story-driven walkthrough of parsing, annotating, and serializing a Tibetan text, with code and explanations., see the [Tutorial Guide](docs/tutorials.md)

## Serializer

The `JsonSerializer` class provides utilities for extracting and serializing annotation data from a Pecha. Key methods include:

- `get_base(pecha)`: Returns the base text from the first base in the given Pecha.
- `to_dict(ann_store, ann_type)`: Converts an AnnotationStore to a list of annotation dictionaries for the given annotation type.
- `get_edition_base(pecha, edition_layer_path)`: Constructs a new base text by applying version variant operations (insertions/deletions) from an edition layer.
- `serialize(pecha, manifestation_info)`: Serializes a Pecha with its annotations based on manifestation information, returning base text and annotations.
- `serialize_edition_annotations(pecha, edition_layer_path, layer_path)`: Serializes annotations that are based on an edition base rather than the original base.

See the [API Reference](docs/api-references.md#jsonserializer) for full details and usage examples.


## API Reference

For a detailed list of classes and methods, see the [API Reference](docs/api-references.md).


---

## Diving Deeper
- [STAM GitHub](https://github.com/annotation/stam)
- [STAM Python GitHub](https://github.com/annotation/stam-python)
- [STAM Python Documentation](https://stam-python.readthedocs.io/en/latest/)
- [STAM Python Tutorial](https://github.com/annotation/stam-python/blob/master/tutorial.ipynb)
- [OpenPecha Paper](https://dl.acm.org/doi/abs/10.1145/3418060)

---

## Contributing
We welcome contributions! Please open issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Project Owners
- [@10zinten](https://github.com/10zinten)
- [@tsundue](https://github.com/tenzin3)
- [@ta4tsering](https://github.com/ta4tsering)

