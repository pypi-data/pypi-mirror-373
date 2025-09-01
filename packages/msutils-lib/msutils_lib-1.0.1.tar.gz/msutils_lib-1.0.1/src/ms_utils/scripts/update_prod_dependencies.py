import re

import tomlkit


def strip_extras(pkg: str) -> str:
    return re.split(r"\[.*\]", pkg)[0]


def main():
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        data = tomlkit.parse(f.read())

    with open("requirements-lock.txt", "r") as f:
        installed_packages = f.read().splitlines()

    # Normalize package names in the lock file
    package_versions = {
        pkg.split("==")[0].replace("_", "-"): pkg.split("==")[1]
        for pkg in installed_packages
        if "==" in pkg
    }

    if (
        "project" in data
        and "optional-dependencies" in data["project"]
        and "lock" in data["project"]["optional-dependencies"]
    ):
        updated_lock_deps = []
        for dep in data["project"]["optional-dependencies"]["lock"]:
            original = dep
            # Extract base name and extras
            match = re.match(r"([^\[=]+)(\[.*\])?", dep)
            name = match.group(1)
            extras = match.group(2) or ""

            normalized_name = name.replace("_", "-")

            if normalized_name in package_versions:
                updated_lock_deps.append(
                    f"{name}{extras}=={package_versions[normalized_name]}"
                )
            else:
                updated_lock_deps.append(original)

        lock_list = tomlkit.array(updated_lock_deps)
        lock_list.multiline(True)
        data["project"]["optional-dependencies"]["lock"] = lock_list

    with open("pyproject.toml", "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(data))


if __name__ == "__main__":
    main()
