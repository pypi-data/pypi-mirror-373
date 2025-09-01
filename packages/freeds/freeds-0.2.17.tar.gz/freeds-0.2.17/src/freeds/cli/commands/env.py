from freeds.config import get_env

def env()->None:
    """Print the export statements for freeds env values, allowing you to set the env values in a sceipt; `source <(freeds env)`. """
    for key, value in get_env().items():
        print(f'export {key}="{value}"')
