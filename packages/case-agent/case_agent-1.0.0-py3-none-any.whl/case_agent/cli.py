import argparse
from .generator import build_case_profile

def main():
    parser = argparse.ArgumentParser(description="Generate agentic case-profile.yaml")
    parser.add_argument("--client", required=True)
    parser.add_argument("--contact", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--infra", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--constraints", required=False)
    parser.add_argument("--success", required=True)
    parser.add_argument("--payment", required=True)
    parser.add_argument("--dry-run", action="store_true", help="Preview YAML without writing")
    args = parser.parse_args()

    yaml_output = build_case_profile(args)

    if args.dry_run:
        print("🧠 Previewing case-profile.yaml:\n")
        print(yaml_output)
    else:
        with open("case-profile.yaml", "w") as f:
            f.write(yaml_output)
        print("✅ case-profile.yaml written to disk.")

if __name__ == "__main__":
    main()
