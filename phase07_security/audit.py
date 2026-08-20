import logging


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)


logger = logging.getLogger("mcp.audit")


def audit(
    *,
    actor: str,
    role: str,
    operation: str,
    success: bool,
    details: str = "",
) -> None:

    logger.info(
        "actor=%s role=%s operation=%s success=%s details=%s",
        actor,
        role,
        operation,
        success,
        details,
    )