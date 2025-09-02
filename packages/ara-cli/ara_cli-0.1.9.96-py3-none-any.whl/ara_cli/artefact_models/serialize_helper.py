def as_a_serializer(as_a):
    role = as_a.strip()

    exceptions_for_a = ('user', 'university', 'one-time', 'european', 'unit')
    exceptions_for_an = ('hour', 'honest', 'heir')
    role_lower = role.lower()
    as_a_prefix = ""

    if any(role_lower.startswith(e) for e in exceptions_for_a):
        as_a_prefix = "As a"
    elif any(role_lower.startswith(e) for e in exceptions_for_an):
        as_a_prefix = "As an"
    elif role_lower.startswith(('a', 'e', 'i', 'o', 'u')):
        as_a_prefix = "As an"
    else:
        as_a_prefix = "As a"

    return f"{as_a_prefix} {role}".strip()
