"""Read a local service owner's grant from the existing private configuration."""
import json
import os
import stat

MODEL_ACTIONS = frozenset({"ai_reply", "plan_generate"})
FORMAL_ACTIONS = frozenset({"formal_create", "formal_dispatch", "formal_observe", "formal_hold"})


def load_service_settings(file):
    try:
        before = file.lstat()
        fd = os.open(file, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        return json.loads(file.read_text(encoding="utf-8")), None
    with os.fdopen(fd, encoding="utf-8") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("The Dashboard configuration must be a regular file")
        settings = json.load(stream)
    grant = settings.get("operator")
    if (
        stat.S_ISREG(before.st_mode)
        and (before.st_dev, before.st_ino) == (opened.st_dev, opened.st_ino)
        and before.st_uid == opened.st_uid == os.geteuid()
        and stat.S_IMODE(before.st_mode) == stat.S_IMODE(opened.st_mode) == 0o600
        and isinstance(grant, dict)
    ):
        return settings, grant
    return settings, None
