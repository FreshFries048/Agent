import os
import json
from mutation_utils import mutate_template


def mutate_templates_in_config(config_path: str) -> None:
    """Mutate templates in the given market targets config using mutate_template."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    # If buyer_personas exists, mutate each persona's template
    if 'buyer_personas' in config:
        if isinstance(config['buyer_personas'], list):
            for persona in config['buyer_personas']:
                if isinstance(persona, dict) and 'template' in persona:
                    persona['template'] = mutate_template(persona['template'])
    # Also mutate global template if present
    if 'template' in config:
        config['template'] = mutate_template(config['template'])
    # Write the updated config back to file
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


def main() -> None:
    # Compute path to market_targets.json relative to this script
    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, '..', 'ghostreach', 'market_targets.json')
    config_path = os.path.abspath(config_path)
    mutate_templates_in_config(config_path)


if __name__ == "__main__":
    main()
