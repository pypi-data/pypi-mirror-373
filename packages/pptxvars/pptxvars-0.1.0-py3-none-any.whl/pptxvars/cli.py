import argparse
import sys
from pathlib import Path
from .replacer import apply_vars, load_vars, format_outpath


def main():
    ap = argparse.ArgumentParser(prog="pptxvars", description="Replace {{KEY}} in PPTX with YAML values")
    ap.add_argument("--template", required=True, help="Input PPTX template path")
    ap.add_argument("--vars", required=True, help="YAML with variables")
    ap.add_argument("--out", default="{STEM}_{DATE}.pptx",
                    help="Output path or pattern. Supports {KEY} and {STEM}. Default: {STEM}_{DATE}.pptx")
    args = ap.parse_args()

    tpl = Path(args.template).resolve()
    yml = Path(args.vars).resolve()
    if not tpl.exists(): sys.exit(f"Missing template: {tpl}")
    if not yml.exists(): sys.exit(f"Missing vars: {yml}")

    vars_map = load_vars(yml)
    vars_map.setdefault("STEM", tpl.stem)

    out_path = format_outpath(args.out, vars_map, default_dir=tpl.parent)
    apply_vars(tpl, yml, out_path)
    print(f"Variables applied: {tpl.name} -> {out_path}")


if __name__ == "__main__":
    main()

# Example usage:
# pptxvars --template templates/example_prs.pptx `
#          --vars templates/example.yml `
#          --out "output/{STEM}_{DATE}.pptx"
