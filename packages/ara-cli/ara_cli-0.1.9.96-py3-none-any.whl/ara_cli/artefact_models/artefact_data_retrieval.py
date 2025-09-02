from ara_cli.artefact_models.artefact_model import Artefact


def artefact_content_retrieval(artefact: Artefact):
    content = artefact.serialize()
    return content


def artefact_path_retrieval(artefact: Artefact):
    return artefact.file_path


def artefact_tags_retrieval(artefact: Artefact):
    final_tags = []

    if not artefact:
        return []

    final_tags.extend([f"user_{user}" for user in artefact.users])
    final_tags.append(artefact.status)
    final_tags.extend(artefact.tags)

    return final_tags
