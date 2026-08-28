from exceptions.config_error import ConfigError


# -------------------------------------------------- AI Config --------------------------------------------------------
# Here you can change your preferences on AI responses.


model_name = "deepseek-v4-flash-0731" # Put the AI model name in here (and don't forget to change your API endpoint in .env if needed).
model_operation_limit = 25 # How many actions (tool calls + reasoning) your model can do from one prompt. Set to -1 for no limit.
github_username: str = "Snupkindeker" # Put your GitHub username here, this is required for the AI GitHub tools to work.
coding_case: str = "snake" # Change to "snake" for snake_case, "camel" for camelCase or "pascal" for PascalCase.
use_markdown: bool = True # Decides whether AI should use Markdown or not.
preferred_languages: list[str] = [] # Put preferred programming languages in the list. Empty means use any language.
language: str = 'en' # Put your language code in here for the interfaces. Supported values: 'en', 'ru'.


# ------------------------------------------------ Config checker -----------------------------------------------------
def check_config():
    errors = []
    if not isinstance(model_name, str) or not model_name:
        errors.append("model_name must be a non-empty string")
    if not isinstance(model_operation_limit, int) or model_operation_limit < 1:
        errors.append("model_operation_limit must be positive integer")
    if not isinstance(github_username, str) or not github_username:
        errors.append("github_username must be a non-empty string")
    if coding_case not in ['snake', 'camel', 'pascal']:
        errors.append("coding_case must be one of: snake, camel, pascal")
    if not isinstance(use_markdown, bool):
        errors.append("use_markdown must be boolean")
    if not isinstance(preferred_languages, list):
        raise ConfigError("Invalid preferred languages setting")
    if len(preferred_languages) > 30:
        raise ConfigError("Too many preferred languages")
    for language in preferred_languages:
        if not isinstance(language, str):
            raise ConfigError("Invalid preferred languages setting")
        if language not in ['assembly', 'bash', 'basic', 'c++', 'cpp', 'c#', 'csharp', 'c', 'go', 'java', 'js', 'javascript', 'kotlin', 'lua', 'pascal', 'php', 'python', 'ruby', 'rust', 'sql', 'sqlite', 'swift', 'typescript', 'visual_basic']:
            raise ConfigError("Invalid preferred languages setting")

# ------------------------------------------------ Set to default -----------------------------------------------------
def set_default_config():
    global model_name, model_operation_limit, github_username, coding_case, use_markdown, preferred_languages, language
    model_name = 'deepseek-v4-flash-0731'
    model_operation_limit = 25
    github_username = ''
    coding_case = 'snake'
    use_markdown = True
    preferred_languages = []
    language = 'en'

# --------------------------------------------------- Testing ---------------------------------------------------------
if __name__ == "__main__":
    try:
        check_config()
    except ConfigError as e:
        print(e)
        set_default_config()
    print(coding_case)