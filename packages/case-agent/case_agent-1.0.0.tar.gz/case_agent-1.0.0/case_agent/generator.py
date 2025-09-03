from datetime import datetime
import yaml

def build_case_profile(args):
    data = {
        "case_id": f"{args.client.lower().replace(' ', '-')}-form-monitor",
        "project_title": f"Form Monitor Agent for {args.client}",
        "prepared_by": "QUEST",
        "date_created": datetime.utcnow().isoformat(),
        "client_profile": {
            "organization": args.client,
            "contact_person": args.contact,
            "email": args.email,
            "infrastructure": args.infra
        },
        "project_scope": {
            "objective": args.objective,
            "constraints": args.constraints.split(",") if args.constraints else [],
            "success_criteria": args.success
        },
        "payment_structure": {
            "milestones": ["Dry-run preview", "Confirmed execution", "Final report"],
            "method": args.payment
        }
    }
    return yaml.dump(data, sort_keys=False)
