# 📦 es-mapping-inspector

**es-mapping-inspector** is a Python utility to inspect and compare Elasticsearch mappings against Pydantic models.
It helps ensure that your Elasticsearch index mapping is consistent with your application's data models.

---

## ✨ Features

* **Compare** Elasticsearch index mappings with Pydantic models.
* **Inspect** and retrieve detailed mapping information from an Elasticsearch index.
* **Extract** field definitions from Pydantic models for validation and debugging.
* **Logging-friendly** with no default logging configuration (uses `NullHandler`).

---

## 📦 Installation

```bash
pip install es-mapping-inspector
```

---

## 🚀 Quick Start

```python
from es_mapping_inspector import compare_es_mapping_with_model, EsMappingInspector, get_pydantic_model_fields
from my_models import MyPydanticModel

# 1. Inspect an Elasticsearch mapping
inspector = EsMappingInspector(es_client=my_es_client, index_name="my_index")
mapping = inspector.get_mapping()

# 2. Compare with a Pydantic model
differences = compare_es_mapping_with_model(
    mapping=mapping,
    model=MyPydanticModel
)
if differences:
    print("Differences found:", differences)

# 3. Get Pydantic model fields
fields = get_pydantic_model_fields(MyPydanticModel)
print(fields)
```

---

## 📚 API Reference

### `compare_es_mapping_with_model(mapping, model) → dict`

Compares an Elasticsearch mapping with a Pydantic model and returns any differences.

**Parameters:**

* `mapping` *(dict)* – The Elasticsearch index mapping.
* `model` *(BaseModel)* – The Pydantic model to compare against.

---

### `class EsMappingInspector`

Utility class to retrieve and analyze Elasticsearch mappings.

**Methods:**

* `get_mapping()` – Retrieves the full index mapping from Elasticsearch.
* *(Additional methods as needed)*

---

### `get_pydantic_model_fields(model) → dict`

Returns a dictionary of field names and types from a Pydantic model.

---

## 🛠 Development

```bash
git clone https://github.com/yourusername/es-mapping-inspector.git
cd es-mapping-inspector
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

---

## 📝 Versioning

This package follows [Semantic Versioning](https://semver.org/).
Current version: **`__version__`** from `es_mapping_inspector.__about__`.

---

## 📄 License

MIT License – see [LICENSE](LICENSE) file for details.

---

## 💡 Contributing

Pull requests are welcome! Please ensure code style and tests pass before submitting.
