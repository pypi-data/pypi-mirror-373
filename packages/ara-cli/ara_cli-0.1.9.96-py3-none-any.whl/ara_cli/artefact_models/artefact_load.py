from ara_cli.artefact_models.artefact_mapping import title_prefix_to_artefact_class


def artefact_from_content(content):
    lines = content.splitlines()
    
    # Look through more lines to find the title, skipping empty lines
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        if line.startswith('@'):  # Skip tag lines
            continue
            
        for prefix, artefact_class in title_prefix_to_artefact_class.items():
            if line.startswith(prefix):
                return artefact_class.deserialize(content)
    return None
