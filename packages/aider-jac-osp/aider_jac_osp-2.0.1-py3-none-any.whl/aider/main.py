import json
import os
import re
import sys
import threading
import traceback
import webbrowser
from dataclasses import fields
from pathlib import Path

try:
    import git
except ImportError:
    git = None

import importlib_resources
import shtab
from dotenv import load_dotenv
from prompt_toolkit.enums import EditingMode

from aider import __version__, models, urls, utils
from aider.analytics import Analytics
from aider.args import get_parser
from aider.coders import Coder
from aider.coders.base_coder import UnknownEditFormat
from aider.commands import Commands, SwitchCoder
from aider.copypaste import ClipboardWatcher
from aider.deprecated import handle_deprecated_model_args
from aider.format_settings import format_settings, scrub_sensitive_info
from aider.history import ChatSummary
from aider.io import InputOutput
from aider.llm import litellm  # noqa: F401; properly init litellm on launch
from aider.models import ModelSettings
from aider.onboarding import offer_openrouter_oauth, select_default_model
from aider.repo import ANY_GIT_ERROR, GitRepo
from aider.report import report_uncaught_exceptions
from aider.versioncheck import check_version, install_from_main_branch, install_upgrade
from aider.watch import FileWatcher

# NEW IMPORTS FOR GENIUS MODE AND JAC INTEGRATION
from aider.genius import GeniusMode, GeniusConfig
from aider.jac_integration import JacIntegration
from aider.sendchat import SendChatManager, AutonomousFlow
from aider.llm import LLMManager, TokenOptimizer

from .dump import dump  # noqa: F401


def check_config_files_for_yes(config_files):
    found = False
    for config_file in config_files:
        if Path(config_file).exists():
            try:
                with open(config_file, "r") as f:
                    for line in f:
                        if line.strip().startswith("yes:"):
                            print("Configuration error detected.")
                            print(f"The file {config_file} contains a line starting with 'yes:'")
                            print("Please replace 'yes:' with 'yes-always:' in this file.")
                            found = True
            except Exception:
                pass
    return found


def get_git_root():
    """Try and guess the git repo, since the conf.yml can be at the repo root"""
    try:
        repo = git.Repo(search_parent_directories=True)
        return repo.working_tree_dir
    except (git.InvalidGitRepositoryError, FileNotFoundError):
        return None


def guessed_wrong_repo(io, git_root, fnames, git_dname):
    """After we parse the args, we can determine the real repo. Did we guess wrong?"""

    try:
        check_repo = Path(GitRepo(io, fnames, git_dname).root).resolve()
    except (OSError,) + ANY_GIT_ERROR:
        return

    # we had no guess, rely on the "true" repo result
    if not git_root:
        return str(check_repo)

    git_root = Path(git_root).resolve()
    if check_repo == git_root:
        return

    return str(check_repo)


def make_new_repo(git_root, io):
    try:
        repo = git.Repo.init(git_root)
        check_gitignore(git_root, io, False)
    except ANY_GIT_ERROR as err:  # issue #1233
        io.tool_error(f"Unable to create git repo in {git_root}")
        io.tool_output(str(err))
        return

    io.tool_output(f"Git repository created in {git_root}")
    return repo


def setup_git(git_root, io):
    if git is None:
        return

    try:
        cwd = Path.cwd()
    except OSError:
        cwd = None

    repo = None

    if git_root:
        try:
            repo = git.Repo(git_root)
        except ANY_GIT_ERROR:
            pass
    elif cwd == Path.home():
        io.tool_warning(
            "You should probably run aider in your project's directory, not your home dir."
        )
        return
    elif cwd and io.confirm_ask(
        "No git repo found, create one to track aider's changes (recommended)?"
    ):
        git_root = str(cwd.resolve())
        repo = make_new_repo(git_root, io)

    if not repo:
        return

    try:
        user_name = repo.git.config("--get", "user.name") or None
    except git.exc.GitCommandError:
        user_name = None

    try:
        user_email = repo.git.config("--get", "user.email") or None
    except git.exc.GitCommandError:
        user_email = None

    if user_name and user_email:
        return repo.working_tree_dir

    with repo.config_writer() as git_config:
        if not user_name:
            git_config.set_value("user", "name", "Your Name")
            io.tool_warning('Update git name with: git config user.name "Your Name"')
        if not user_email:
            git_config.set_value("user", "email", "you@example.com")
            io.tool_warning('Update git email with: git config user.email "you@example.com"')

    return repo.working_tree_dir


def check_gitignore(git_root, io, ask=True):
    if not git_root:
        return

    try:
        repo = git.Repo(git_root)
        patterns_to_add = []

        if not repo.ignored(".aider"):
            patterns_to_add.append(".aider*")

        env_path = Path(git_root) / ".env"
        if env_path.exists() and not repo.ignored(".env"):
            patterns_to_add.append(".env")

        # NEW: Add Jac-related patterns to gitignore
        jac_patterns = [".jac", "*.jac.tmp", ".jac_cache"]
        for pattern in jac_patterns:
            if not repo.ignored(pattern):
                patterns_to_add.append(pattern)

        if not patterns_to_add:
            return

        gitignore_file = Path(git_root) / ".gitignore"
        if gitignore_file.exists():
            try:
                content = io.read_text(gitignore_file)
                if content is None:
                    return
                if not content.endswith("\n"):
                    content += "\n"
            except OSError as e:
                io.tool_error(f"Error when trying to read {gitignore_file}: {e}")
                return
        else:
            content = ""
    except ANY_GIT_ERROR:
        return

    if ask:
        io.tool_output("You can skip this check with --no-gitignore")
        if not io.confirm_ask(f"Add {', '.join(patterns_to_add)} to .gitignore (recommended)?"):
            return

    content += "\n".join(patterns_to_add) + "\n"

    try:
        io.write_text(gitignore_file, content)
        io.tool_output(f"Added {', '.join(patterns_to_add)} to .gitignore")
    except OSError as e:
        io.tool_error(f"Error when trying to write to {gitignore_file}: {e}")
        io.tool_output(
            "Try running with appropriate permissions or manually add these patterns to .gitignore:"
        )
        for pattern in patterns_to_add:
            io.tool_output(f"  {pattern}")


def check_streamlit_install(io):
    return utils.check_pip_install_extra(
        io,
        "streamlit",
        "You need to install the aider browser feature",
        ["aider-chat[browser]"],
    )


def write_streamlit_credentials():
    from streamlit.file_util import get_streamlit_file_path

    # See https://github.com/Aider-AI/aider/issues/772

    credential_path = Path(get_streamlit_file_path()) / "credentials.toml"
    if not os.path.exists(credential_path):
        empty_creds = '[general]\nemail = ""\n'

        os.makedirs(os.path.dirname(credential_path), exist_ok=True)
        with open(credential_path, "w") as f:
            f.write(empty_creds)
    else:
        print("Streamlit credentials already exist.")


def launch_gui(args):
    from streamlit.web import cli

    from aider import gui

    print()
    print("CONTROL-C to exit...")

    # Necessary so streamlit does not prompt the user for an email address.
    write_streamlit_credentials()

    target = gui.__file__

    st_args = ["run", target]

    st_args += [
        "--browser.gatherUsageStats=false",
        "--runner.magicEnabled=false",
        "--server.runOnSave=false",
    ]

    # https://github.com/Aider-AI/aider/issues/2193
    is_dev = "-dev" in str(__version__)

    if is_dev:
        print("Watching for file changes.")
    else:
        st_args += [
            "--global.developmentMode=false",
            "--server.fileWatcherType=none",
            "--client.toolbarMode=viewer",  # minimal?
        ]

    st_args += ["--"] + args

    cli.main(st_args)


def parse_lint_cmds(lint_cmds, io):
    err = False
    res = dict()
    for lint_cmd in lint_cmds:
        if re.match(r"^[a-z]+:.*", lint_cmd):
            pieces = lint_cmd.split(":")
            lang = pieces[0]
            cmd = lint_cmd[len(lang) + 1 :]
            lang = lang.strip()
        else:
            lang = None
            cmd = lint_cmd

        cmd = cmd.strip()

        if cmd:
            res[lang] = cmd
        else:
            io.tool_error(f'Unable to parse --lint-cmd "{lint_cmd}"')
            io.tool_output('The arg should be "language: cmd --args ..."')
            io.tool_output('For example: --lint-cmd "python: flake8 --select=E9"')
            err = True
    if err:
        return
    return res


def generate_search_path_list(default_file, git_root, command_line_file):
    files = []
    files.append(Path.home() / default_file)  # homedir
    if git_root:
        files.append(Path(git_root) / default_file)  # git root
    files.append(default_file)
    if command_line_file:
        files.append(command_line_file)

    resolved_files = []
    for fn in files:
        try:
            resolved_files.append(Path(fn).resolve())
        except OSError:
            pass

    files = resolved_files
    files.reverse()
    uniq = []
    for fn in files:
        if fn not in uniq:
            uniq.append(fn)
    uniq.reverse()
    files = uniq
    files = list(map(str, files))
    files = list(dict.fromkeys(files))

    return files


def register_models(git_root, model_settings_fname, io, verbose=False):
    model_settings_files = generate_search_path_list(
        ".aider.model.settings.yml", git_root, model_settings_fname
    )

    try:
        files_loaded = models.register_models(model_settings_files)
        if len(files_loaded) > 0:
            if verbose:
                io.tool_output("Loaded model settings from:")
                for file_loaded in files_loaded:
                    io.tool_output(f"  - {file_loaded}")  # noqa: E221
        elif verbose:
            io.tool_output("No model settings files loaded")
    except Exception as e:
        io.tool_error(f"Error loading aider model settings: {e}")
        return 1

    if verbose:
        io.tool_output("Searched for model settings files:")
        for file in model_settings_files:
            io.tool_output(f"  - {file}")

    return None


def load_dotenv_files(git_root, dotenv_fname, encoding="utf-8"):
    # Standard .env file search path
    dotenv_files = generate_search_path_list(
        ".env",
        git_root,
        dotenv_fname,
    )

    # Explicitly add the OAuth keys file to the beginning of the list
    oauth_keys_file = Path.home() / ".aider" / "oauth-keys.env"
    if oauth_keys_file.exists():
        # Insert at the beginning so it's loaded first (and potentially overridden)
        dotenv_files.insert(0, str(oauth_keys_file.resolve()))
        # Remove duplicates if it somehow got included by generate_search_path_list
        dotenv_files = list(dict.fromkeys(dotenv_files))

    loaded = []
    for fname in dotenv_files:
        try:
            if Path(fname).exists():
                load_dotenv(fname, override=True, encoding=encoding)
                loaded.append(fname)
        except OSError as e:
            print(f"OSError loading {fname}: {e}")
        except Exception as e:
            print(f"Error loading {fname}: {e}")
    return loaded


def register_litellm_models(git_root, model_metadata_fname, io, verbose=False):
    model_metadata_files = []

    # Add the resource file path
    resource_metadata = importlib_resources.files("aider.resources").joinpath("model-metadata.json")
    model_metadata_files.append(str(resource_metadata))

    model_metadata_files += generate_search_path_list(
        ".aider.model.metadata.json", git_root, model_metadata_fname
    )

    try:
        model_metadata_files_loaded = models.register_litellm_models(model_metadata_files)
        if len(model_metadata_files_loaded) > 0 and verbose:
            io.tool_output("Loaded model metadata from:")
            for model_metadata_file in model_metadata_files_loaded:
                io.tool_output(f"  - {model_metadata_file}")  # noqa: E221
    except Exception as e:
        io.tool_error(f"Error loading model metadata models: {e}")
        return 1


def sanity_check_repo(repo, io):
    if not repo:
        return True

    if not repo.repo.working_tree_dir:
        io.tool_error("The git repo does not seem to have a working tree?")
        return False

    bad_ver = False
    try:
        repo.get_tracked_files()
        if not repo.git_repo_error:
            return True
        error_msg = str(repo.git_repo_error)
    except UnicodeDecodeError as exc:
        error_msg = (
            "Failed to read the Git repository. This issue is likely caused by a path encoded "
            f'in a format different from the expected encoding "{sys.getfilesystemencoding()}".\n'
            f"Internal error: {str(exc)}"
        )
    except ANY_GIT_ERROR as exc:
        error_msg = str(exc)
        bad_ver = "version in (1, 2)" in error_msg
    except AssertionError as exc:
        error_msg = str(exc)
        bad_ver = True

    if bad_ver:
        io.tool_error("Aider only works with git repos with version number 1 or 2.")
        io.tool_output("You may be able to convert your repo: git update-index --index-version=2")
        io.tool_output("Or run aider --no-git to proceed without using git.")
        io.offer_url(urls.git_index_version, "Open documentation url for more info?")
        return False

    io.tool_error("Unable to read git repository, it may be corrupt?")
    io.tool_output(error_msg)
    return False


def initialize_genius_mode(args, io, main_model, repo, analytics):
    """Initialize genius mode if enabled"""
    if not getattr(args, 'genius_mode', False):
        return None
        
    try:
        # Validate genius mode arguments
        max_iter = getattr(args, 'genius_max_iterations', 5)
        if max_iter < 1 or max_iter > 50:
            io.tool_error("--genius-max-iterations must be between 1 and 50")
            return None
            
        threshold = getattr(args, 'genius_complexity_threshold', 0.7)
        if threshold < 0.0 or threshold > 1.0:
            io.tool_error("--genius-complexity-threshold must be between 0.0 and 1.0")
            return None
        
        # Create genius config
        genius_config = GeniusConfig(
            max_iterations=max_iter,
            complexity_threshold=threshold,
            enable_reflection=getattr(args, 'genius_reflection', True),
            enable_planning=getattr(args, 'genius_planning', True),
            enable_validation=getattr(args, 'genius_validation', True),
            token_budget=getattr(args, 'genius_token_budget', None),
        )
        
        # Initialize genius mode
        genius = GeniusMode(
            config=genius_config,
            model=main_model,
            repo=repo,
            io=io,
            analytics=analytics
        )
        
        if getattr(args, 'verbose', False):
            io.tool_output("Genius mode initialized")
            io.tool_output(f"  Max iterations: {genius_config.max_iterations}")
            io.tool_output(f"  Complexity threshold: {genius_config.complexity_threshold}")
            io.tool_output(f"  Reflection enabled: {genius_config.enable_reflection}")
            io.tool_output(f"  Planning enabled: {genius_config.enable_planning}")
            io.tool_output(f"  Validation enabled: {genius_config.enable_validation}")
            
        analytics.event("genius_mode_initialized", config=genius_config.__dict__)
        return genius
        
    except Exception as e:
        io.tool_error(f"Failed to initialize genius mode: {e}")
        if getattr(args, 'verbose', False):
            io.tool_output(f"Full exception: {traceback.format_exc()}")
        return None


def initialize_jac_integration(args, io, analytics):
    """Initialize Jac integration if enabled"""
    if not getattr(args, 'jac_enabled', False):
        return None
        
    try:
        # Validate Jac arguments
        jac_path = getattr(args, 'jac_path', None)
        if jac_path and not os.path.exists(jac_path):
            io.tool_error(f"Jac path does not exist: {jac_path}")
            return None
            
        jac_config = {
            'jac_path': jac_path,
            'jac_cache_dir': getattr(args, 'jac_cache_dir', '.jac_cache'),
            'jac_auto_compile': getattr(args, 'jac_auto_compile', True),
            'jac_debug': getattr(args, 'jac_debug', False),
        }
        
        jac = JacIntegration(
            jac_path=jac_config['jac_path'],
            cache_dir=jac_config['jac_cache_dir'],
            auto_compile=jac_config['jac_auto_compile'],
            debug=jac_config['jac_debug'],
            io=io
        )
        
        if getattr(args, 'verbose', False):
            io.tool_output("Jac integration initialized")
            io.tool_output(f"  Jac path: {jac_config['jac_path']}")
            io.tool_output(f"  Cache dir: {jac_config['jac_cache_dir']}")
            io.tool_output(f"  Auto compile: {jac_config['jac_auto_compile']}")
            io.tool_output(f"  Debug mode: {jac_config['jac_debug']}")
            
        analytics.event("jac_integration_initialized", config=jac_config)
        return jac
        
    except Exception as e:
        io.tool_error(f"Failed to initialize Jac integration: {e}")
        if getattr(args, 'verbose', False):
            io.tool_output(f"Full exception: {traceback.format_exc()}")
        return None


def initialize_sendchat_manager(args, io, main_model, analytics):
    """Initialize SendChat manager for autonomous flows"""
    try:
        # Validate SendChat arguments
        max_iter = getattr(args, 'sendchat_max_iterations', 10)
        if max_iter < 1 or max_iter > 100:
            io.tool_error("--sendchat-max-iterations must be between 1 and 100")
            return None
            
        threshold = getattr(args, 'sendchat_confirmation_threshold', 0.8)
        if threshold < 0.0 or threshold > 1.0:
            io.tool_error("--sendchat-confirmation-threshold must be between 0.0 and 1.0")
            return None
        
        sendchat_config = {
            'max_auto_iterations': max_iter,
            'enable_autonomous': getattr(args, 'sendchat_autonomous', False),
            'confirmation_threshold': threshold,
            'safety_checks': getattr(args, 'sendchat_safety_checks', True),
        }
        
        sendchat = SendChatManager(
            model=main_model,
            io=io,
            analytics=analytics,
            **sendchat_config
        )
        
        if getattr(args, 'verbose', False):
            io.tool_output("SendChat manager initialized")
            io.tool_output(f"  Max iterations: {sendchat_config['max_auto_iterations']}")
            io.tool_output(f"  Autonomous mode: {sendchat_config['enable_autonomous']}")
            io.tool_output(f"  Confirmation threshold: {sendchat_config['confirmation_threshold']}")
            io.tool_output(f"  Safety checks: {sendchat_config['safety_checks']}")
            
        analytics.event("sendchat_manager_initialized", config=sendchat_config)
        return sendchat
        
    except Exception as e:
        io.tool_error(f"Failed to initialize SendChat manager: {e}")
        if getattr(args, 'verbose', False):
            io.tool_output(f"Full exception: {traceback.format_exc()}")
        return None


def initialize_llm_manager(args, main_model, io, analytics):
    """Initialize LLM manager with token optimization"""
    try:
        # Validate LLM manager arguments
        token_budget = getattr(args, 'llm_token_budget', None)
        if token_budget is not None and (token_budget < 1000 or token_budget > 1000000):
            io.tool_error("--llm-token-budget must be between 1000 and 1000000")
            return None
        
        llm_config = {
            'enable_optimization': getattr(args, 'llm_optimize', True),
            'token_budget': token_budget,
            'optimization_strategy': getattr(args, 'llm_optimization_strategy', 'adaptive'),
            'cache_enabled': getattr(args, 'cache_prompts', False),
        }
        
        # Initialize token optimizer
        token_optimizer = TokenOptimizer(
            model=main_model,
            strategy=llm_config['optimization_strategy'],
            token_budget=llm_config['token_budget'],
            io=io
        )
        
        # Initialize LLM manager
        llm_manager = LLMManager(
            model=main_model,
            token_optimizer=token_optimizer,
            cache_enabled=llm_config['cache_enabled'],
            io=io,
            analytics=analytics
        )
        
        if getattr(args, 'verbose', False):
            io.tool_output("LLM manager initialized")
            io.tool_output(f"  Optimization enabled: {llm_config['enable_optimization']}")
            io.tool_output(f"  Token budget: {llm_config['token_budget']}")
            io.tool_output(f"  Optimization strategy: {llm_config['optimization_strategy']}")
            io.tool_output(f"  Cache enabled: {llm_config['cache_enabled']}")
            
        analytics.event("llm_manager_initialized", config=llm_config)
        return llm_manager
        
    except Exception as e:
        io.tool_error(f"Failed to initialize LLM manager: {e}")
        if getattr(args, 'verbose', False):
            io.tool_output(f"Full exception: {traceback.format_exc()}")
        return None


def main(argv=None, input=None, output=None, force_git_root=None, return_coder=False):
    report_uncaught_exceptions()

    if argv is None:
        argv = sys.argv[1:]

    if git is None:
        git_root = None
    elif force_git_root:
        git_root = force_git_root
    else:
        git_root = get_git_root()

    conf_fname = Path(".aider.conf.yml")

    default_config_files = []
    try:
        default_config_files += [conf_fname.resolve()]  # CWD
    except OSError:
        pass

    if git_root:
        git_conf = Path(git_root) / conf_fname  # git root
        if git_conf not in default_config_files:
            default_config_files.append(git_conf)
    default_config_files.append(Path.home() / conf_fname)  # homedir
    default_config_files = list(map(str, default_config_files))

    parser = get_parser(default_config_files, git_root)
    try:
        args, unknown = parser.parse_known_args(argv)
    except AttributeError as e:
        if all(word in str(e) for word in ["bool", "object", "has", "no", "attribute", "strip"]):
            if check_config_files_for_yes(default_config_files):
                return 1
        raise e

    if args.verbose:
        print("Config files search order, if no --config:")
        for file in default_config_files:
            exists = "(exists)" if Path(file).exists() else ""
            print(f"  - {file} {exists}")

    default_config_files.reverse()

    parser = get_parser(default_config_files, git_root)

    args, unknown = parser.parse_known_args(argv)

    # Load the .env file specified in the arguments
    loaded_dotenvs = load_dotenv_files(git_root, args.env_file, args.encoding)

    # Parse again to include any arguments that might have been defined in .env
    args = parser.parse_args(argv)

    if args.shell_completions:
        # Ensure parser.prog is set for shtab, though it should be by default
        parser.prog = "aider"
        print(shtab.complete(parser, shell=args.shell_completions))
        sys.exit(0)

    if git is None:
        args.git = False

    if args.analytics_disable:
        analytics = Analytics(permanently_disable=True)
        print("Analytics have been permanently disabled.")

    # Initialize analytics if not disabled
    if not getattr(args, 'analytics_disable', False):
        analytics = Analytics()
    else:
        analytics = Analytics(permanently_disable=True)

    if not args.verify_ssl:
        import httpx

        os.environ["SSL_VERIFY"] = ""
        litellm._load_litellm()
        litellm._lazy_module.client_session = httpx.Client(verify=False)
        litellm._lazy_module.aclient_session = httpx.AsyncClient(verify=False)
        # Set verify_ssl on the model_info_manager
        models.model_info_manager.set_verify_ssl(False)

    if args.timeout:
        models.request_timeout = args.timeout

    if args.dark_mode:
        args.user_input_color = "#32FF32"
        args.tool_error_color = "#FF3333"
        args.tool_warning_color = "#FFFF00"
        args.assistant_output_color = "#00FFFF"
        args.code_theme = "monokai"

    if args.light_mode:
        args.user_input_color = "green"
        args.tool_error_color = "red"
        args.tool_warning_color = "#FFA500"
        args.assistant_output_color = "blue"
        args.code_theme = "default"

    if return_coder and args.yes_always is None:
        args.yes_always = True

    editing_mode = EditingMode.VI if args.vim else EditingMode.EMACS

    def get_io(pretty):
        return InputOutput(
            pretty,
            args.yes_always,
            args.input_history_file,
            args.chat_history_file,
            input=input,
            output=output,
            user_input_color=args.user_input_color,
            tool_output_color=args.tool_output_color,
            tool_warning_color=args.tool_warning_color,
            tool_error_color=args.tool_error_color,
            completion_menu_color=args.completion_menu_color,
            completion_menu_bg_color=args.completion_menu_bg_color,
            completion_menu_current_color=args.completion_menu_current_color,
            completion_menu_current_bg_color=args.completion_menu_current_bg_color,
            assistant_output_color=args.assistant_output_color,
            code_theme=args.code_theme,
            dry_run=args.dry_run,
            encoding=args.encoding,
            line_endings=args.line_endings,
            llm_history_file=args.llm_history_file,
            editingmode=editing_mode,
            fancy_input=args.fancy_input,
            multiline_mode=args.multiline,
            notifications=args.notifications,
            notifications_command=args.notifications_command,
        )

    io = get_io(args.pretty)
    try:
        io.rule()
    except UnicodeEncodeError as err:
        if not io.pretty:
            raise err
        io = get_io(False)
        io.tool_warning("Terminal does not support pretty output (UnicodeDecodeError)")

    # Process any environment variables set via --set-env
    if args.set_env:
        for env_setting in args.set_env:
            try:
                name, value = env_setting.split("=", 1)
                os.environ[name.strip()] = value.strip()
            except ValueError:
                io.tool_error(f"Invalid --set-env format: {env_setting}")
                io.tool_output("Format should be: ENV_VAR_NAME=value")
                return 1

    # Process any API keys set via --api-key
    if args.api_key:
        for api_setting in args.api_key:
            try:
                provider, key = api_setting.split("=", 1)
                env_var = f"{provider.strip().upper()}_API_KEY"
                os.environ[env_var] = key.strip()
            except ValueError:
                io.tool_error(f"Invalid --api-key format: {api_setting}")
                io.tool_output("Format should be: provider=key")
                return 1

    if args.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = args.anthropic_api_key

    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key

    # Handle deprecated model shortcut args
    handle_deprecated_model_args(args, io)
    if args.openai_api_base:
        os.environ["OPENAI_API_BASE"] = args.openai_api_base
    if args.openai_api_version:
        io.tool_warning(
            "--openai-api-version is deprecated, use --set-env OPENAI_API_VERSION=<value>"
        )
        os.environ["OPENAI_API_VERSION"] = args.openai_api_version
    if args.openai_api_type:
        io.tool_warning("--openai-api-type is deprecated, use --set-env OPENAI_API_TYPE=<value>")
        os.environ["OPENAI_API_TYPE"] = args.openai_api_type
    if args.openai_organization_id:
        io.tool_warning(
            "--openai-organization-id is deprecated, use --set-env OPENAI_ORG_ID=<value>"
        )
        os.environ["OPENAI_ORG_ID"] = args.openai_organization_id

    # Handle GUI launch
    if args.gui:
        if not check_streamlit_install(io):
            return 1
        launch_gui(argv)
        return

    # Version check
    if args.check_update:
        check_version(args.verbose, io)
        return

    if args.just_check_update:
        check_version(args.verbose, io, just_check=True)
        return

    if args.install_main_branch:
        install_from_main_branch(io)
        return

    if args.upgrade:
        install_upgrade(io)
        return

    # Load model settings and metadata
    if register_models(git_root, args.model_settings_file, io, verbose=args.verbose):
        return 1

    register_litellm_models(git_root, args.model_metadata_file, io, verbose=args.verbose)

    # Model selection and validation
    if args.models:
        models.Model.print_matching_models(args.models, io)
        return

    if args.list_models:
        models.Model.print_matching_models("", io)
        return

    if args.openai_api_key and not args.model:
        args.model = models.GPT_4O_MINI

    if not args.model:
        if args.message or args.chat_history_file or args.resume:
            # Using aider directly, need a model
            io.tool_error("Please specify a model with --model")
            return 1
        else:
            # Interactive mode, can use onboarding
            args.model = select_default_model(io)
            if not args.model:
                return 1

    # Initialize the main model
    try:
        main_model = models.Model.create(
            args.model,
            weak_model=args.weak_model,
            editor_model=args.editor_model,
            editor_edit_format=args.editor_edit_format,
            io=io,
            **{key: getattr(args, key, None) for key in models.Model.get_model_kwargs().keys()}
        )
    except Exception as err:
        if "ValueError: The model" in str(err) and "is not supported" in str(err):
            io.tool_error(str(err))
            io.tool_output("Run `aider --models` to see available models")
            return 1
        raise err

    if not main_model:
        io.tool_error("Unable to initialize model")
        return 1

    # OAuth flow handling
    if main_model.info.get("supports_openrouter_oauth"):
        offer_openrouter_oauth(io)

    if args.verbose:
        io.tool_output(f"Model: {main_model.name}")
        if main_model.weak_model:
            io.tool_output(f"Weak model: {main_model.weak_model.name}")
        if main_model.editor_model:
            io.tool_output(f"Editor model: {main_model.editor_model.name}")

    # Set up file handling and linting
    if args.encoding:
        utils.set_default_encoding(args.encoding)

    lint_cmds = parse_lint_cmds(args.lint_cmd, io)
    if lint_cmds is None:
        return 1

    # Determine the actual git root after parsing files
    guessed_git_root = guessed_wrong_repo(io, git_root, args.file, args.git_dname)
    if guessed_git_root:
        git_root = guessed_git_root

    # Initialize repository
    repo = None
    if args.git:
        git_root = setup_git(git_root, io)
        if not git_root:
            io.tool_error("Unable to initialize git repository")
            if not args.no_git:
                return 1
        else:
            try:
                repo = GitRepo(
                    io,
                    args.file,
                    args.git_dname,
                    args.gitignore,
                    args.aiderignore,
                    args.subtree_only,
                    check_gitignore_enabled=not args.no_gitignore,
                )
                
                if not sanity_check_repo(repo, io):
                    return 1
                    
            except Exception as err:
                io.tool_error(f"Unable to initialize git repository: {err}")
                if args.verbose:
                    io.tool_output(f"Full exception: {traceback.format_exc()}")
                return 1

    # Initialize new features
    genius_mode = initialize_genius_mode(args, io, main_model, repo, analytics)
    jac_integration = initialize_jac_integration(args, io, analytics)
    sendchat_manager = initialize_sendchat_manager(args, io, main_model, analytics)
    llm_manager = initialize_llm_manager(args, main_model, io, analytics)

    # Create the main coder instance
    try:
        coder = Coder.create(
            main_model,
            args.edit_format,
            io,
            skip_model_availabily_check=args.skip_model_availabily_check,
            args=args,
        )

        # Integrate new components with the coder
        if genius_mode:
            coder.genius_mode = genius_mode
        if jac_integration:
            coder.jac_integration = jac_integration
        if sendchat_manager:
            coder.sendchat_manager = sendchat_manager
        if llm_manager:
            coder.llm_manager = llm_manager

    except UnknownEditFormat as err:
        io.tool_error(str(err))
        return 1
    except Exception as err:
        io.tool_error(f"Unable to create coder: {err}")
        if args.verbose:
            io.tool_output(f"Full exception: {traceback.format_exc()}")
        return 1

    # Set up additional coder properties
    if repo:
        coder.repo = repo

    if lint_cmds:
        coder.lint_cmds = lint_cmds

    coder.verbose = args.verbose

    # Handle file watching
    file_watcher = None
    if args.watch_files and repo:
        try:
            file_watcher = FileWatcher(coder, io)
            file_watcher.start()
        except Exception as err:
            io.tool_error(f"Unable to start file watcher: {err}")

    # Set up clipboard watching
    clipboard_watcher = None
    if args.watch_clipboard:
        try:
            clipboard_watcher = ClipboardWatcher(coder, io)
            clipboard_watcher.start()
        except Exception as err:
            io.tool_error(f"Unable to start clipboard watcher: {err}")

    # Handle commit-related commands
    if args.commit:
        if not repo:
            io.tool_error("--commit requires git repository")
            return 1
        commit_result = coder.commit(message=args.commit_message)
        if not commit_result:
            io.tool_error("No changes to commit")
        return 0 if commit_result else 1

    if args.dry_run_commit:
        if not repo:
            io.tool_error("--dry-run-commit requires git repository")
            return 1
        return coder.dry_run_commit(args.commit_message)

    # Handle show-related commands
    if args.show_repo_map:
        if repo:
            io.tool_output(coder.get_repo_map())
        return

    if args.show_prompts:
        coder.show_prompts()
        return

    # Initialize Commands with all the integrated components
    commands = Commands(
        io, 
        coder,
        genius_mode=genius_mode,
        jac_integration=jac_integration,
        sendchat_manager=sendchat_manager,
        llm_manager=llm_manager
    )

    # Handle one-shot message mode
    if args.message:
        # Check if this is a genius mode command
        if genius_mode and (args.message.startswith('/genius') or 
                           getattr(args, 'auto_genius', False)):
            try:
                # For auto-genius, check if query is complex enough
                if not args.message.startswith('/genius') and getattr(args, 'auto_genius', False):
                    if hasattr(genius_mode, 'assess_complexity'):
                        complexity = genius_mode.assess_complexity(args.message)
                        threshold = getattr(genius_mode.config, 'complexity_threshold', 0.7)
                        if complexity < threshold:
                            # Not complex enough, use standard processing
                            coder.run_one(args.message, preproc=False)
                            return 0
                        else:
                            io.tool_output("Auto-activating Genius mode for complex query...")
                
                result = genius_mode.handle_request(args.message)
                if result:
                    io.tool_output("Genius mode completed successfully")
                    return 0
                else:
                    io.tool_error("Genius mode failed")
                    return 1
            except Exception as err:
                io.tool_error(f"Genius mode error: {err}")
                if getattr(args, 'verbose', False):
                    io.tool_output(f"Full exception: {traceback.format_exc()}")
                return 1

        # Check if this is a Jac command
        elif jac_integration and args.message.startswith('/jac'):
            try:
                result = jac_integration.handle_command(args.message)
                return 0 if result else 1
            except Exception as err:
                io.tool_error(f"Jac integration error: {err}")
                if getattr(args, 'verbose', False):
                    io.tool_output(f"Full exception: {traceback.format_exc()}")
                return 1

        # Check for autonomous mode
        elif sendchat_manager and getattr(args, 'sendchat_autonomous', False):
            # Use autonomous flow
            try:
                autonomous_flow = AutonomousFlow(
                    sendchat_manager, 
                    coder, 
                    io, 
                    analytics
                )
                result = autonomous_flow.execute(args.message)
                return 0 if result else 1
            except Exception as err:
                io.tool_error(f"Autonomous flow error: {err}")
                if getattr(args, 'verbose', False):
                    io.tool_output(f"Full exception: {traceback.format_exc()}")
                return 1
        
        # Standard message handling
        else:
            try:
                coder.run_one(args.message, preproc=False)
                return 0
            except KeyboardInterrupt:
                return 1
            except Exception as err:
                io.tool_error(f"Error processing message: {err}")
                if getattr(args, 'verbose', False):
                    io.tool_output(f"Full exception: {traceback.format_exc()}")
                return 1

    # Return coder if requested (for API usage)
    if return_coder:
        return coder

    # Start interactive mode
    try:
        # Display startup information
        if not args.no_pretty:
            show_version = not args.just_check_update and not args.check_update
            if show_version:
                io.tool_output(f"Aider v{__version__}")
                
            if main_model:
                io.tool_output(f"Model: {main_model.name}")
                
            if repo:
                io.tool_output(f"Git repo: {repo.root}")
                
            # Show enabled features
            enabled_features = []
            if genius_mode:
                config = getattr(genius_mode, 'config', None)
                if config:
                    enabled_features.append(f"Genius Mode (max_iter={config.max_iterations})")
                else:
                    enabled_features.append("Genius Mode")
            if jac_integration:
                cache_dir = getattr(jac_integration, 'cache_dir', 'unknown')
                enabled_features.append(f"Jac Integration (cache={cache_dir})")
            if sendchat_manager:
                autonomous = getattr(args, 'sendchat_autonomous', False)
                max_iter = getattr(args, 'sendchat_max_iterations', 10)
                if autonomous:
                    enabled_features.append(f"Autonomous Chat (max_iter={max_iter})")
                else:
                    enabled_features.append("SendChat Manager")
            if llm_manager:
                optimize = getattr(args, 'llm_optimize', True)
                budget = getattr(args, 'llm_token_budget', None)
                if optimize and budget:
                    enabled_features.append(f"LLM Optimization (budget={budget})")
                elif optimize:
                    enabled_features.append("LLM Optimization")
                else:
                    enabled_features.append("LLM Manager")
                
            if enabled_features:
                io.tool_output(f"Features: {', '.join(enabled_features)}")
                
            io.rule()

        # Resume chat history if requested
        if args.resume:
            coder.resume_chat_history()

        # Load chat history if specified
        if args.chat_history_file:
            try:
                ChatSummary(
                    coder.chat_history_file,
                    coder.main_model,
                    coder.io,
                ).load_and_summarize_chat_history()
            except Exception as err:
                io.tool_error(f"Error loading chat history: {err}")

        # Start main chat loop
        coder.run()
        
    except KeyboardInterrupt:
        io.tool_output("\nExiting...")
    except Exception as err:
        io.tool_error(f"Unexpected error: {err}")
        if args.verbose:
            io.tool_output(f"Full exception: {traceback.format_exc()}")
        return 1
    finally:
        # Clean up watchers first
        if file_watcher:
            try:
                file_watcher.stop()
                if getattr(args, 'verbose', False):
                    io.tool_output("✓ File watcher stopped")
            except Exception as e:
                io.tool_error(f"Error stopping file watcher: {e}")
                
        if clipboard_watcher:
            try:
                clipboard_watcher.stop()
                if getattr(args, 'verbose', False):
                    io.tool_output("✓ Clipboard watcher stopped")
            except Exception as e:
                io.tool_error(f"Error stopping clipboard watcher: {e}")
            
        # Clean up integrations in proper dependency order
        cleanup_errors = []
        
        # Cleanup order: most dependent first, least dependent last
        components = [
            ("Genius Mode", genius_mode),
            ("SendChat Manager", sendchat_manager),
            ("Jac Integration", jac_integration), 
            ("LLM Manager", llm_manager),
        ]
        
        for name, component in components:
            if component:
                try:
                    if hasattr(component, 'cleanup'):
                        component.cleanup()
                        if getattr(args, 'verbose', False):
                            io.tool_output(f"✓ {name} cleaned up successfully")
                except Exception as e:
                    error_msg = f"Error cleaning up {name}: {e}"
                    cleanup_errors.append(error_msg)
                    io.tool_error(error_msg)
                    if getattr(args, 'verbose', False):
                        io.tool_output(f"Full {name} cleanup exception: {traceback.format_exc()}")
        
        # Report cleanup issues if any
        if cleanup_errors and getattr(args, 'verbose', False):
            io.tool_warning(f"Cleanup completed with {len(cleanup_errors)} issues")

    return 0


if __name__ == "__main__":
    sys.exit(main())