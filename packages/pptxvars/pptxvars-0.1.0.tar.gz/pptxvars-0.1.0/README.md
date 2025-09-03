# pptxvars

**Replace {{KEY}} tokens in PPTX while preserving styling**

---

steps:

1. Create a custom powerpoint presentation
2. Define your variables in powerpoint textboxes by {{VARIABLE_NAME}}
3. Define in a YAML file what values must replace the {{KEYS}}
4. Execute replacement:

```powershell
pptxvars --template templates/example_prs.pptx `
         --vars templates/example.yml `
         --out 'output/{STEM}_{DATE}.pptx'
```

Or through library:

```python
from pathlib import Path
from pptxvars import apply_vars

apply_vars(
    pptx_in=Path("templates/example_prs.pptx"),
    yaml_vars=Path("templates/example.yml"),
    pptx_out=Path("output/out.pptx"),
)
```
