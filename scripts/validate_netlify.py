import sys
import tomllib
from pathlib import Path


def validate(path):
    with Path(path).open("rb") as file:
        config = tomllib.load(file)

    if config.get("build", {}).get("publish") != "frontend":
        raise ValueError("Netlify publish directory must be frontend")

    headers = config.get("headers", [])

    if not isinstance(headers, list) or not headers:
        raise ValueError("No Netlify headers blocks found")

    for index, header in enumerate(headers, start=1):
        if not isinstance(header, dict) or not header.get("for"):
            raise ValueError(
                f"Headers block {index} is missing 'for'"
            )

        values = header.get("values", {})
        if not isinstance(values, dict):
            raise ValueError(f"Invalid header values in block {index}")

        csp = values.get("Content-Security-Policy", "")

        for directive in csp.split(";"):
            tokens = directive.strip().split()

            if not tokens:
                continue

            name = tokens[0].lower()

            if name in (
                "default-src",
                "script-src",
                "connect-src",
            ):
                if "*" in tokens[1:]:
                    raise ValueError(
                        f"Wildcard CSP forbidden in {name}"
                    )

    print("PASS: Netlify TOML and CSP validation")


if __name__ == "__main__":
    try:
        validate(
            sys.argv[1]
            if len(sys.argv) > 1
            else "netlify.toml"
        )
    except (ValueError, OSError, tomllib.TOMLDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
