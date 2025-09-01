import freeds.setup as setup
import freeds.setup.utils as utils
import freeds.utils.log as log

logger = log.setup_logging(__name__)


def main() -> bool:
    utils.log_header("Setting up The Free Data Stack (FreeDS)", "=")
    # Directory setup
    if not setup.setup_root_dir():
        return False
    if not utils.prompt_yesno(description="FreeDS directory setup is completed", question="continue to docker setup"):
        return False

    # Docker setup
    if not setup.setup_docker():
        return False
    if not utils.prompt_yesno(description="FreeDS docker setup is completed", question="continue to credentials setup"):
        return False

    # Credentials setup
    if not setup.setup_credentials():
        return False
    if not utils.prompt_yesno(
        description=(
            "Credential setup is completed, next step is to create and start the FreeDS plugins in docker.\n"
            "This is the point of no return in regards to some of the config. The process so far can be re-run and new credentials entered and so on.\n"
            "Next step will create users from the credentials and they cannot be updated by simply modifiying the config files."
        ),
        question="Move on to initilise the FreeDS plugins",
    ):
        return False

    return True
