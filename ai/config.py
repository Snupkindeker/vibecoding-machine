from exceptions.config_error import ConfigError


# -------------------------------------------------- AI Config --------------------------------------------------------
# Here you can change your preferences on AI responses.


model_name = "deepseek-v4-flash-0731" # Put the AI model name in here (and don't forget to change your API endpoint in .env if needed).
model_operation_limit = 25 # How many actions (tool calls + reasoning) your model can do from one prompt. Set to -1 for no limit.
github_username: str = "Snupkindeker" # Put your GitHub username here, this is required for the AI GitHub tools to work.
coding_case: str = "snake" # Change to "snake" for snake_case, "camel" for camelCase or "pascal" for PascalCase.
use_markdown: bool = True # Decides whether AI should use Markdown or not.
preferred_languages: list[str] = [] # Put preferred programming languages in the list. Empty means use any language.


# ------------------------------------------------ Config checker -----------------------------------------------------
def check_config() -> None: # Checks all config values and raises ConfigError if something is wrong
    if type(github_username) != str:
        raise ConfigError("Invalid github username")
    if type(coding_case) != str:
        raise ConfigError("Invalid coding case")
    if coding_case not in ["snake", "camel", "pascal"]:
        raise ConfigError("Invalid coding case")
    if type(use_markdown) != bool:
        raise ConfigError("Invalid markdown usage setting")
    if type(preferred_languages) != list:
        raise ConfigError("Invalid preferred languages setting")
    if len(preferred_languages) > 30:
        raise ConfigError("Too many preferred languages")
    for language in preferred_languages:
        if type(language) != str:
            raise ConfigError("Invalid preferred languages setting")
        if language not in ['assembly', 'bash', 'basic', 'c++', 'cpp', 'c#', 'csharp', 'c', 'go', 'java', 'js', 'javascript', 'kotlin', 'lua', 'pascal', 'php', 'python', 'ruby', 'rust', 'sql', 'sqlite', 'swift', 'typescript', 'visual_basic']:
            raise ConfigError("Invalid preferred languages setting")

# ------------------------------------------------ Set to default -----------------------------------------------------
def set_default_config(reset_username: bool = False) -> None:
    global model_name
    global model_operation_limit
    global github_username
    global coding_case
    global use_markdown
    global preferred_languages

    model_name = "deepseek-v4-flash-0731"
    model_operation_limit = 25
    if reset_username: github_username = "Snupkindeker"
    coding_case = "snake"
    use_markdown = True
    preferred_languages = []


# --------------------------------------------------- Testing ---------------------------------------------------------
if __name__ == "__main__":
    try:
        check_config()
    except ConfigError as e:
        print(e)
        set_default_config()
    print(coding_case)