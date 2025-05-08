# TMDL Documentation Validator

This repository includes a Python-based validator for Tabular Model Definition Language (TMDL) artefacts, ensuring that all required model elements (tables, columns, measures, etc.) are properly documented. The validator can be run locally or as part of a GitHub Actions workflow.

## What does it do?

- Scans all `.tmdl` files in your project for artefact declarations (e.g., table, column, measure).
- Checks for documentation: Each artefact must have a documentation row (a triple-slash comment, `/// ...`) immediately above its declaration, with no blank lines in between.
- Reports violations for missing documentation and lists successes for documented artefacts.
- Supports targeted validation for specific artefacts by type and name.

## Usage

### Prerequisites

- Python 3.8 or later

### Validate all artefacts (default: table, column, measure, model, role, partition)

```sh
python .github/scripts/validate_tmdl_docs.py
```

### Validate only specific artefact types (e.g., table, column, measure)

```sh
python .github/scripts/validate_tmdl_docs.py --require table,column,measure
```

### Validate a specific artefact by type and name

```sh
python .github/scripts/validate_tmdl_docs.py --file models/Sample.SemanticModel/definition/tables/financials.tmdl --artefact "column COGS"
```

## Documentation Requirements

- Artefact must be documented with a triple-slash comment (`/// ...`) immediately above its declaration.
- No blank lines between the documentation and the artefact.
- Multiline documentation is supported by stacking multiple `///` lines.

**Example:**
```txt
/// Cost of Goods Sold
column COGS
    dataType: double
    ...
```

## Output

- **Violations:** Lists artefacts missing documentation, with file and line number.
- **Successes:** Lists artefacts with documentation, showing the documentation row(s) verbatim.

## GitHub Actions Integration

This repository includes a GitHub Actions workflow (`.github/workflows/validate-tmdl.yml`) that automatically runs the validator on pull requests and pushes. The workflow will fail if any required artefacts are missing documentation.

**Example workflow step:**
```yaml
- name: Validate TMDL documentation
  run: python .github/scripts/validate_tmdl_docs.py --require table,column,measure
```

## References

- [Tabular Model Definition Language (TMDL) Documentation](https://learn.microsoft.com/power-bi/developer/semantic-model/tmdl/tmdl-introduction)
- [Power BI Project (PBIP) Format](https://learn.microsoft.com/power-bi/create-reports/deployment-pipelines/semantic-model-pbip)