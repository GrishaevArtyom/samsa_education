import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path

from radon.complexity import cc_visit


IGNORED_NAMES = {
    "str", "int", "float", "bool", "list", "dict", "set", "tuple",
    "None", "True", "False", "Enum", "dataclass", "field",
}


def iter_python_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".py" else []

    return [
        file
        for file in path.rglob("*.py")
        if "__pycache__" not in file.parts and ".venv" not in file.parts
    ]


def check_cyclomatic_complexity(files: list[Path], max_complexity: int) -> list[str]:
    errors = []

    for file in files:
        source = file.read_text(encoding="utf-8")

        for block in cc_visit(source):
            complexity = getattr(block, "complexity", 0)
            name = getattr(block, "fullname", block.name)

            if complexity > max_complexity:
                errors.append(
                    f"{file}:{block.lineno} {name}: "
                    f"cyclomatic complexity {complexity} > {max_complexity}"
                )

    return errors


def normalized_lines(files: list[Path]) -> list[tuple[Path, int, str]]:
    result = []

    for file in files:
        lines = file.read_text(encoding="utf-8").splitlines()

        for number, line in enumerate(lines, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            result.append((file, number, line))

    return result


def check_duplication(
    files: list[Path],
    max_percent: float,
    window: int = 5,
) -> tuple[list[str], float]:
    lines = normalized_lines(files)

    if len(lines) < window:
        return [], 0.0

    chunks = defaultdict(list)

    for index in range(0, len(lines) - window + 1):
        text = tuple(line for _, _, line in lines[index:index + window])
        chunks[text].append(index)

    duplicated_indexes = set()

    for indexes in chunks.values():
        if len(indexes) > 1:
            for index in indexes:
                duplicated_indexes.update(range(index, index + window))

    duplicated_percent = len(duplicated_indexes) / len(lines) * 100

    if duplicated_percent >= max_percent:
        return [
            f"code duplication {duplicated_percent:.2f}% >= {max_percent}%"
        ], duplicated_percent

    return [], duplicated_percent


def collect_classes(
    files: list[Path],
) -> tuple[dict[str, Path], dict[str, list[str]], dict[str, set[str]]]:
    class_files = {}
    inheritance = {}
    coupling = defaultdict(set)

    for file in files:
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_files[node.name] = file

    project_classes = set(class_files)

    for file in files:
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            base_names = []

            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.append(base.attr)

            inheritance[node.name] = [
                base for base in base_names
                if base in project_classes
            ]

            for child in ast.walk(node):
                if isinstance(child, ast.Name):
                    name = child.id

                    if (
                        name in project_classes
                        and name != node.name
                        and name not in IGNORED_NAMES
                    ):
                        coupling[node.name].add(name)

                elif isinstance(child, ast.Attribute):
                    name = child.attr

                    if (
                        name in project_classes
                        and name != node.name
                        and name not in IGNORED_NAMES
                    ):
                        coupling[node.name].add(name)

    return class_files, inheritance, coupling


def inheritance_depth(
    class_name: str,
    inheritance: dict[str, list[str]],
    seen: set[str] | None = None,
) -> int:
    seen = seen or set()

    if class_name in seen:
        return 0

    seen.add(class_name)
    bases = inheritance.get(class_name, [])

    if not bases:
        return 0

    return 1 + max(
        inheritance_depth(base, inheritance, seen)
        for base in bases
    )


def check_design_metrics(
    files: list[Path],
    max_cbo: int,
    max_dit: int,
) -> tuple[list[str], dict[str, int], dict[str, int]]:
    _, inheritance, coupling = collect_classes(files)

    errors = []
    cbo_values = {
        class_name: len(dependencies)
        for class_name, dependencies in coupling.items()
    }
    dit_values = {
        class_name: inheritance_depth(class_name, inheritance)
        for class_name in inheritance
    }

    for class_name, value in sorted(cbo_values.items()):
        if value > max_cbo:
            errors.append(f"{class_name}: CBO {value} > {max_cbo}")

    for class_name, value in sorted(dit_values.items()):
        if value > max_dit:
            errors.append(f"{class_name}: DIT {value} > {max_dit}")

    return errors, cbo_values, dit_values


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check educational code quality metrics."
    )

    parser.add_argument("--path", default="backend/quality_demo.py")
    parser.add_argument("--max-complexity", type=int, default=15)
    parser.add_argument("--max-duplication", type=float, default=10.0)
    parser.add_argument("--max-cbo", type=int, default=15)
    parser.add_argument("--max-dit", type=int, default=7)

    args = parser.parse_args()

    files = iter_python_files(Path(args.path))

    if not files:
        print(f"No Python files found in {args.path}", file=sys.stderr)
        return 1

    errors = []

    errors.extend(
        check_cyclomatic_complexity(
            files,
            args.max_complexity,
        )
    )

    duplication_errors, duplication_percent = check_duplication(
        files,
        args.max_duplication,
    )
    errors.extend(duplication_errors)

    design_errors, cbo_values, dit_values = check_design_metrics(
        files,
        args.max_cbo,
        args.max_dit,
    )
    errors.extend(design_errors)

    print("Quality metrics report")
    print(f"Checked files: {len(files)}")
    print(f"Max cyclomatic complexity threshold: <= {args.max_complexity}")
    print(
        f"Code duplication: {duplication_percent:.2f}% "
        f"/ threshold < {args.max_duplication}%"
    )
    print(f"CBO values: {dict(sorted(cbo_values.items()))}")
    print(f"DIT values: {dict(sorted(dit_values.items()))}")

    if errors:
        print("\nFAILED:")

        for error in errors:
            print(f"- {error}")

        return 1

    print("\nPASSED: all metric thresholds are satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())