import contextlib
import os
import time
from pathlib import Path, PurePosixPath
import re

try:
    import git

    ANY_GIT_ERROR = [
        git.exc.ODBError,
        git.exc.GitError,
        git.exc.InvalidGitRepositoryError,
        git.exc.GitCommandNotFound,
    ]
except ImportError:
    git = None
    ANY_GIT_ERROR = []

import pathspec

from aider import prompts, utils

from .dump import dump  # noqa: F401
from .waiting import WaitingSpinner

ANY_GIT_ERROR += [
    OSError,
    IndexError,
    BufferError,
    TypeError,
    ValueError,
    AttributeError,
    AssertionError,
    TimeoutError,
]
ANY_GIT_ERROR = tuple(ANY_GIT_ERROR)


@contextlib.contextmanager
def set_git_env(var_name, value, original_value):
    """Temporarily set a Git environment variable."""
    os.environ[var_name] = value
    try:
        yield
    finally:
        if original_value is not None:
            os.environ[var_name] = original_value
        elif var_name in os.environ:
            del os.environ[var_name]


class GitRepo:
    repo = None
    aider_ignore_file = None
    aider_ignore_spec = None
    aider_ignore_ts = 0
    aider_ignore_last_check = 0
    subtree_only = False
    ignore_file_cache = {}
    git_repo_error = None

    def __init__(
        self,
        io,
        fnames,
        git_dname,
        aider_ignore_file=None,
        models=None,
        attribute_author=True,
        attribute_committer=True,
        attribute_commit_message_author=False,
        attribute_commit_message_committer=False,
        commit_prompt=None,
        subtree_only=False,
        git_commit_verify=True,
        attribute_co_authored_by=False,  # Added parameter
    ):
        self.io = io
        self.models = models

        self.normalized_path = {}
        self.tree_files = {}

        # Repo map caches
        self.file_metadata_cache = {}
        self.repo_structure_cache = None
        self.repo_structure_cache_time = 0

        self.attribute_author = attribute_author
        self.attribute_committer = attribute_committer
        self.attribute_commit_message_author = attribute_commit_message_author
        self.attribute_commit_message_committer = attribute_commit_message_committer
        self.attribute_co_authored_by = attribute_co_authored_by  # Assign from parameter
        self.commit_prompt = commit_prompt
        self.subtree_only = subtree_only
        self.git_commit_verify = git_commit_verify
        self.ignore_file_cache = {}

        if git_dname:
            check_fnames = [git_dname]
        elif fnames:
            check_fnames = fnames
        else:
            check_fnames = ["."]

        repo_paths = []
        for fname in check_fnames:
            fname = Path(fname)
            fname = fname.resolve()

            if not fname.exists() and fname.parent.exists():
                fname = fname.parent

            try:
                repo_path = git.Repo(fname, search_parent_directories=True).working_dir
                repo_path = utils.safe_abs_path(repo_path)
                repo_paths.append(repo_path)
            except ANY_GIT_ERROR:
                pass

        num_repos = len(set(repo_paths))

        if num_repos == 0:
            raise FileNotFoundError
        if num_repos > 1:
            self.io.tool_error("Files are in different git repos.")
            raise FileNotFoundError

        # https://github.com/gitpython-developers/GitPython/issues/427
        self.repo = git.Repo(repo_paths.pop(), odbt=git.GitDB)
        self.root = utils.safe_abs_path(self.repo.working_tree_dir)

        if aider_ignore_file:
            self.aider_ignore_file = Path(aider_ignore_file)

    # ========== REPO MAP METHODS ==========

    def get_repo_map(self, current_files=None, include_content=True, max_tokens_per_file=None, extensions=None):
        """
        Get structured repository map for LLM/editor integration.
        
        Args:
            current_files: List of files being actively edited (prioritized)
            include_content: Whether to include file content or just metadata
            max_tokens_per_file: Token limit per file for LLM usage
            extensions: List of file extensions to filter by (e.g., ['.py', '.js'])
        
        Returns:
            dict: {
                'current_files': {...},  # Files being edited
                'other_files': {...},    # Rest of repository
                'structure': {...},      # Directory structure
                'metadata': {...}        # Repo metadata
            }
        """
        current_files = current_files or []
        all_files = self.get_tracked_files()
        
        if extensions:
            all_files = [f for f in all_files if any(f.endswith(ext) for ext in extensions)]
        
        current_file_set = set(self.normalize_path(f) for f in current_files)
        other_files = [f for f in all_files if f not in current_file_set]
        
        repo_map = {
            'current_files': self._build_file_map(current_files, include_content, max_tokens_per_file),
            'other_files': self._build_file_map(other_files, include_content, max_tokens_per_file),
            'structure': self.get_repo_structure(),
            'metadata': {
                'root': self.root,
                'total_files': len(all_files),
                'current_count': len(current_files),
                'other_count': len(other_files),
                'dirty_files': self.get_dirty_files()
            }
        }
        
        return repo_map

    def _build_file_map(self, file_list, include_content=True, max_tokens_per_file=None):
        """Build file map with content and metadata."""
        file_map = {}
        
        for filepath in file_list:
            try:
                abs_path = self.abs_root_path(filepath)
                if not abs_path.exists():
                    continue
                
                file_info = {
                    'path': filepath,
                    'abs_path': str(abs_path),
                    'size': abs_path.stat().st_size,
                    'modified': abs_path.stat().st_mtime,
                    'extension': abs_path.suffix,
                    'is_dirty': self.is_dirty(filepath)
                }
                
                if include_content:
                    if max_tokens_per_file:
                        token_count = self.estimate_file_tokens(filepath)
                        if token_count > max_tokens_per_file:
                            file_info['content'] = self.get_file_summary(filepath)
                            file_info['is_summary'] = True
                            file_info['full_token_count'] = token_count
                        else:
                            file_info['content'] = self.get_file_content_safe(filepath)
                            file_info['is_summary'] = False
                    else:
                        file_info['content'] = self.get_file_content_safe(filepath)
                        file_info['is_summary'] = False
                    
                    file_info['token_count'] = self.estimate_file_tokens(filepath)
                
                file_map[filepath] = file_info
                
            except (OSError, ValueError) as e:
                self.io.tool_warning(f"Error processing file {filepath}: {e}")
                continue
        
        return file_map

    def get_repo_structure(self):
        """Get cached repository directory structure."""
        current_time = time.time()
        if (self.repo_structure_cache and 
            current_time - self.repo_structure_cache_time < 30):  # Cache for 30 seconds
            return self.repo_structure_cache
        
        structure = {}
        all_files = self.get_tracked_files()
        
        for filepath in all_files:
            parts = Path(filepath).parts
            current_level = structure
            
            # Build nested structure
            for part in parts[:-1]:  # All but the filename
                if part not in current_level:
                    current_level[part] = {'type': 'directory', 'children': {}}
                current_level = current_level[part]['children']
            
            # Add the file
            filename = parts[-1] if parts else filepath
            current_level[filename] = {
                'type': 'file',
                'path': filepath,
                'extension': Path(filepath).suffix
            }
        
        self.repo_structure_cache = structure
        self.repo_structure_cache_time = current_time
        return structure

    def get_file_content_safe(self, filepath, max_size=1024*1024):  # 1MB default limit
        """Safely read file content with error handling."""
        try:
            abs_path = self.abs_root_path(filepath)
            if abs_path.stat().st_size > max_size:
                return self.get_file_summary(filepath)
            
            # Try to read as text
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                # Try with different encodings
                for encoding in ['latin-1', 'cp1252']:
                    try:
                        with open(abs_path, 'r', encoding=encoding) as f:
                            return f.read()
                    except UnicodeDecodeError:
                        continue
                
                # If all encodings fail, treat as binary
                return f"<Binary file: {filepath}>"
                
        except (OSError, IOError) as e:
            return f"<Error reading file: {e}>"

    def get_file_summary(self, filepath, max_lines=50):
        """Get truncated summary of large files."""
        try:
            abs_path = self.abs_root_path(filepath)
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if len(lines) <= max_lines:
                return ''.join(lines)
            
            # Take first and last portions
            first_part = max_lines // 2
            last_part = max_lines - first_part
            
            summary_lines = (
                lines[:first_part] + 
                [f"\n... ({len(lines) - max_lines} lines omitted) ...\n\n"] +
                lines[-last_part:]
            )
            
            return ''.join(summary_lines)
            
        except (OSError, UnicodeDecodeError):
            return f"<Unable to summarize file: {filepath}>"

    def estimate_file_tokens(self, filepath):
        """Estimate token count for file (rough approximation)."""
        cache_key = f"{filepath}:{self.abs_root_path(filepath).stat().st_mtime}"
        
        if cache_key in self.file_metadata_cache:
            return self.file_metadata_cache[cache_key]['tokens']
        
        try:
            content = self.get_file_content_safe(filepath)
            if content.startswith('<'):  # Binary or error content
                tokens = 0
            else:
                # Rough token estimation: ~4 characters per token
                tokens = len(content) // 4
            
            self.file_metadata_cache[cache_key] = {'tokens': tokens}
            return tokens
            
        except Exception:
            return 0

    def get_related_files(self, target_files, max_related=10):
        """Find files related to target files based on imports and references."""
        if not target_files:
            return []
        
        all_files = self.get_tracked_files()
        related_files = set()
        
        # Extract imports and references from target files
        patterns_to_find = set()
        
        for target_file in target_files:
            try:
                content = self.get_file_content_safe(target_file)
                
                # Python imports
                import_matches = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
                for match in import_matches:
                    module = match[0] or match[1]
                    if module:
                        patterns_to_find.add(module.replace('.', '/'))
                
                # General file references (simple heuristic)
                file_refs = re.findall(r'["\']([^"\']*\.[a-zA-Z]{2,4})["\']', content)
                patterns_to_find.update(file_refs)
                
            except Exception:
                continue
        
        # Find files matching patterns
        for filepath in all_files:
            if filepath in target_files:
                continue
                
            for pattern in patterns_to_find:
                if pattern in filepath:
                    related_files.add(filepath)
                    if len(related_files) >= max_related:
                        break
            
            if len(related_files) >= max_related:
                break
        
        return list(related_files)

    def filter_files_by_extension(self, extensions, exclude=False):
        """Filter tracked files by extensions."""
        all_files = self.get_tracked_files()
        
        if exclude:
            return [f for f in all_files if not any(f.endswith(ext) for ext in extensions)]
        else:
            return [f for f in all_files if any(f.endswith(ext) for ext in extensions)]

    def get_file_context(self, filepath, context_lines=5):
        """Get file with context for LLM (function/class boundaries)."""
        try:
            content = self.get_file_content_safe(filepath)
            lines = content.split('\n')
            
            # For Python files, try to identify function/class boundaries
            if filepath.endswith('.py'):
                enhanced_lines = []
                for i, line in enumerate(lines):
                    enhanced_line = line
                    if re.match(r'^\s*(def|class|async def)', line):
                        enhanced_line = f"# Line {i+1}\n{line}"
                    enhanced_lines.append(enhanced_line)
                return '\n'.join(enhanced_lines)
            
            return content
            
        except Exception:
            return self.get_file_content_safe(filepath)

    # ========== ORIGINAL METHODS (unchanged) ==========

    def commit(self, fnames=None, context=None, message=None, aider_edits=False, coder=None):
        """
        Commit the specified files or all dirty files if none are specified.

        Args:
            fnames (list, optional): List of filenames to commit. Defaults to None (commit all
                                     dirty files).
            context (str, optional): Context for generating commit message. Defaults to None.
            message (str, optional): Explicit commit message. Defaults to None (generate message).
            aider_edits (bool, optional): Whether the changes were made by Aider. Defaults to False.
                                          This affects attribution logic.
            coder (Coder, optional): The Coder instance, used for config and model info.
                                     Defaults to None.

        Returns:
            tuple(str, str) or None: The commit hash and commit message if successful,
                                     else None.

        Attribution Logic:
        ------------------
        This method handles Git commit attribution based on configuration flags and whether
        Aider generated the changes (`aider_edits`).

        Key Concepts:
        - Author: The person who originally wrote the code changes.
        - Committer: The person who last applied the commit to the repository.
        - aider_edits=True: Changes were generated by Aider (LLM).
        - aider_edits=False: Commit is user-driven (e.g., /commit manually staged changes).
        - Explicit Setting: A flag (--attribute-...) is set to True or False
          via command line or config file.
        - Implicit Default: A flag is not explicitly set, defaulting to None in args, which is
          interpreted as True unless overridden by other logic.

        Flags:
        - --attribute-author: Modify Author name to "User Name (aider)".
        - --attribute-committer: Modify Committer name to "User Name (aider)".
        - --attribute-co-authored-by: Add
          "Co-authored-by: aider (<model>) <aider@aider.chat>" trailer to commit message.

        Behavior Summary:

        1. When aider_edits = True (AI Changes):
           - If --attribute-co-authored-by=True:
             - Co-authored-by trailer IS ADDED.
             - Author/Committer names are NOT modified by default (co-authored-by takes precedence).
             - EXCEPTION: If --attribute-author/--attribute-committer is EXPLICITLY True, the
               respective name IS modified (explicit overrides precedence).
           - If --attribute-co-authored-by=False:
             - Co-authored-by trailer is NOT added.
             - Author/Committer names ARE modified by default (implicit True).
             - EXCEPTION: If --attribute-author/--attribute-committer is EXPLICITLY False,
               the respective name is NOT modified.

        2. When aider_edits = False (User Changes):
           - --attribute-co-authored-by is IGNORED (trailer never added).
           - Author name is NEVER modified (--attribute-author ignored).
           - Committer name IS modified by default (implicit True, as Aider runs `git commit`).
           - EXCEPTION: If --attribute-committer is EXPLICITLY False, the name is NOT modified.

        Resulting Scenarios:
        - Standard AI edit (defaults): Co-authored-by=False -> Author=You(aider),
          Committer=You(aider)
        - AI edit with Co-authored-by (default): Co-authored-by=True -> Author=You,
          Committer=You, Trailer added
        - AI edit with Co-authored-by + Explicit Author: Co-authored-by=True,
          --attribute-author -> Author=You(aider), Committer=You, Trailer added
        - User commit (defaults): aider_edits=False -> Author=You, Committer=You(aider)
        - User commit with explicit no-committer: aider_edits=False,
          --no-attribute-committer -> Author=You, Committer=You
        """
        if not fnames and not self.repo.is_dirty():
            return

        diffs = self.get_diffs(fnames)
        if not diffs:
            return

        if message:
            commit_message = message
        else:
            user_language = None
            if coder:
                user_language = coder.commit_language
                if not user_language:
                    user_language = coder.get_user_language()
            commit_message = self.get_commit_message(diffs, context, user_language)

        # Retrieve attribute settings, prioritizing coder.args if available
        if coder and hasattr(coder, "args"):
            attribute_author = coder.args.attribute_author
            attribute_committer = coder.args.attribute_committer
            attribute_commit_message_author = coder.args.attribute_commit_message_author
            attribute_commit_message_committer = coder.args.attribute_commit_message_committer
            attribute_co_authored_by = coder.args.attribute_co_authored_by
        else:
            # Fallback to self attributes (initialized from config/defaults)
            attribute_author = self.attribute_author
            attribute_committer = self.attribute_committer
            attribute_commit_message_author = self.attribute_commit_message_author
            attribute_commit_message_committer = self.attribute_commit_message_committer
            attribute_co_authored_by = self.attribute_co_authored_by

        # Determine explicit settings (None means use default behavior)
        author_explicit = attribute_author is not None
        committer_explicit = attribute_committer is not None

        # Determine effective settings (apply default True if not explicit)
        effective_author = True if attribute_author is None else attribute_author
        effective_committer = True if attribute_committer is None else attribute_committer

        # Determine commit message prefixing
        prefix_commit_message = aider_edits and (
            attribute_commit_message_author or attribute_commit_message_committer
        )

        # Determine Co-authored-by trailer
        commit_message_trailer = ""
        if aider_edits and attribute_co_authored_by:
            model_name = "unknown-model"
            if coder and hasattr(coder, "main_model") and coder.main_model.name:
                model_name = coder.main_model.name
            commit_message_trailer = f"\n\nCo-authored-by: aider ({model_name}) <aider@aider.chat>"

        # Determine if author/committer names should be modified
        # Author modification applies only to aider edits.
        # It's used if effective_author is True AND
        # (co-authored-by is False OR author was explicitly set).
        use_attribute_author = (
            aider_edits and effective_author and (not attribute_co_authored_by or author_explicit)
        )

        # Committer modification applies regardless of aider_edits (based on tests).
        # It's used if effective_committer is True AND
        # (it's not an aider edit with co-authored-by OR committer was explicitly set).
        use_attribute_committer = effective_committer and (
            not (aider_edits and attribute_co_authored_by) or committer_explicit
        )

        if not commit_message:
            commit_message = "(no commit message provided)"

        if prefix_commit_message:
            commit_message = "aider: " + commit_message

        full_commit_message = commit_message + commit_message_trailer

        cmd = ["-m", full_commit_message]
        if not self.git_commit_verify:
            cmd.append("--no-verify")
        if fnames:
            fnames = [str(self.abs_root_path(fn)) for fn in fnames]
            for fname in fnames:
                try:
                    self.repo.git.add(fname)
                except ANY_GIT_ERROR as err:
                    self.io.tool_error(f"Unable to add {fname}: {err}")
            cmd += ["--"] + fnames
        else:
            cmd += ["-a"]

        original_user_name = self.repo.git.config("--get", "user.name")
        original_committer_name_env = os.environ.get("GIT_COMMITTER_NAME")
        original_author_name_env = os.environ.get("GIT_AUTHOR_NAME")
        committer_name = f"{original_user_name} (aider)"

        try:
            # Use context managers to handle environment variables
            with contextlib.ExitStack() as stack:
                if use_attribute_committer:
                    stack.enter_context(
                        set_git_env(
                            "GIT_COMMITTER_NAME", committer_name, original_committer_name_env
                        )
                    )
                if use_attribute_author:
                    stack.enter_context(
                        set_git_env("GIT_AUTHOR_NAME", committer_name, original_author_name_env)
                    )

                # Perform the commit
                self.repo.git.commit(cmd)
                commit_hash = self.get_head_commit_sha(short=True)
                self.io.tool_output(f"Commit {commit_hash} {commit_message}", bold=True)
                return commit_hash, commit_message

        except ANY_GIT_ERROR as err:
            self.io.tool_error(f"Unable to commit: {err}")
            # No return here, implicitly returns None

    def get_rel_repo_dir(self):
        try:
            return os.path.relpath(self.repo.git_dir, os.getcwd())
        except (ValueError, OSError):
            return self.repo.git_dir

    def get_commit_message(self, diffs, context, user_language=None):
        diffs = "# Diffs:\n" + diffs

        content = ""
        if context:
            content += context + "\n"
        content += diffs

        system_content = self.commit_prompt or prompts.commit_system

        language_instruction = ""
        if user_language:
            language_instruction = f"\n- Is written in {user_language}."
        system_content = system_content.format(language_instruction=language_instruction)

        commit_message = None
        for model in self.models:
            spinner_text = f"Generating commit message with {model.name}"
            with WaitingSpinner(spinner_text):
                if model.system_prompt_prefix:
                    current_system_content = model.system_prompt_prefix + "\n" + system_content
                else:
                    current_system_content = system_content

                messages = [
                    dict(role="system", content=current_system_content),
                    dict(role="user", content=content),
                ]

                num_tokens = model.token_count(messages)
                max_tokens = model.info.get("max_input_tokens") or 0

                if max_tokens and num_tokens > max_tokens:
                    continue

                commit_message = model.simple_send_with_retries(messages)
                if commit_message:
                    break  # Found a model that could generate the message

        if not commit_message:
            self.io.tool_error("Failed to generate commit message!")
            return

        commit_message = commit_message.strip()
        if commit_message and commit_message[0] == '"' and commit_message[-1] == '"':
            commit_message = commit_message[1:-1].strip()

        return commit_message

    def get_diffs(self, fnames=None):
        # We always want diffs of index and working dir

        current_branch_has_commits = False
        try:
            active_branch = self.repo.active_branch
            try:
                commits = self.repo.iter_commits(active_branch)
                current_branch_has_commits = any(commits)
            except ANY_GIT_ERROR:
                pass
        except (TypeError,) + ANY_GIT_ERROR:
            pass

        if not fnames:
            fnames = []

        diffs = ""
        for fname in fnames:
            if not self.path_in_repo(fname):
                diffs += f"Added {fname}\n"

        try:
            if current_branch_has_commits:
                args = ["HEAD", "--"] + list(fnames)
                diffs += self.repo.git.diff(*args, stdout_as_string=False).decode(
                    self.io.encoding, "replace"
                )
                return diffs

            wd_args = ["--"] + list(fnames)
            index_args = ["--cached"] + wd_args

            diffs += self.repo.git.diff(*index_args, stdout_as_string=False).decode(
                self.io.encoding, "replace"
            )
            diffs += self.repo.git.diff(*wd_args, stdout_as_string=False).decode(
                self.io.encoding, "replace"
            )

            return diffs
        except ANY_GIT_ERROR as err:
            self.io.tool_error(f"Unable to diff: {err}")

    def diff_commits(self, pretty, from_commit, to_commit):
        args = []
        if pretty:
            args += ["--color"]
        else:
            args += ["--color=never"]

        args += [from_commit, to_commit]
        diffs = self.repo.git.diff(*args, stdout_as_string=False).decode(
            self.io.encoding, "replace"
        )

        return diffs

    def get_tracked_files(self):
        if not self.repo:
            return []

        try:
            commit = self.repo.head.commit
        except ValueError:
            commit = None
        except ANY_GIT_ERROR as err:
            self.git_repo_error = err
            self.io.tool_error(f"Unable to list files in git repo: {err}")
            self.io.tool_output("Is your git repo corrupted?")
            return []

        files = set()
        if commit:
            if commit in self.tree_files:
                files = self.tree_files[commit]
            else:
                try:
                    iterator = commit.tree.traverse()
                    blob = None  # Initialize blob
                    while True:
                        try:
                            blob = next(iterator)
                            if blob.type == "blob":  # blob is a file
                                files.add(blob.path)
                        except IndexError:
                            # Handle potential index error during tree traversal
                            # without relying on potentially unassigned 'blob'
                            self.io.tool_warning(
                                "GitRepo: Index error encountered while reading git tree object."
                                " Skipping."
                            )
                            continue
                        except StopIteration:
                            break
                except ANY_GIT_ERROR as err:
                    self.git_repo_error = err
                    self.io.tool_error(f"Unable to list files in git repo: {err}")
                    self.io.tool_output("Is your git repo corrupted?")
                    return []
                files = set(self.normalize_path(path) for path in files)
                self.tree_files[commit] = set(files)

        # Add staged files
        index = self.repo.index
        try:
            staged_files = [path for path, _ in index.entries.keys()]
            files.update(self.normalize_path(path) for path in staged_files)
        except ANY_GIT_ERROR as err:
            self.io.tool_error(f"Unable to read staged files: {err}")

        res = [fname for fname in files if not self.ignored_file(fname)]

        return res

    def normalize_path(self, path):
        orig_path = path
        res = self.normalized_path.get(orig_path)
        if res:
            return res

        path = str(Path(PurePosixPath((Path(self.root) / path).relative_to(self.root))))
        self.normalized_path[orig_path] = path
        return path

    def refresh_aider_ignore(self):
        if not self.aider_ignore_file:
            return

        current_time = time.time()
        if current_time - self.aider_ignore_last_check < 1:
            return

        self.aider_ignore_last_check = current_time

        if not self.aider_ignore_file.is_file():
            return

        mtime = self.aider_ignore_file.stat().st_mtime
        if mtime != self.aider_ignore_ts:
            self.aider_ignore_ts = mtime
            self.ignore_file_cache = {}
            lines = self.aider_ignore_file.read_text().splitlines()
            self.aider_ignore_spec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern,
                lines,
            )

    def git_ignored_file(self, path):
        if not self.repo:
            return
        try:
            if self.repo.ignored(path):
                return True
        except ANY_GIT_ERROR:
            return False

    def ignored_file(self, fname):
        self.refresh_aider_ignore()

        if fname in self.ignore_file_cache:
            return self.ignore_file_cache[fname]

        result = self.ignored_file_raw(fname)
        self.ignore_file_cache[fname] = result
        return result

    def ignored_file_raw(self, fname):
        if self.subtree_only:
            try:
                fname_path = Path(self.normalize_path(fname))
                cwd_path = Path.cwd().resolve().relative_to(Path(self.root).resolve())
            except ValueError:
                # Issue #1524
                # ValueError: 'C:\\dev\\squid-certbot' is not in the subpath of
                # 'C:\\dev\\squid-certbot'
                # Clearly, fname is not under cwd... so ignore it
                return True

            if cwd_path not in fname_path.parents and fname_path != cwd_path:
                return True

        if not self.aider_ignore_file or not self.aider_ignore_file.is_file():
            return False

        try:
            fname = self.normalize_path(fname)
        except ValueError:
            return True

        return self.aider_ignore_spec.match_file(fname)

    def path_in_repo(self, path):
        if not self.repo:
            return
        if not path:
            return

        tracked_files = set(self.get_tracked_files())
        return self.normalize_path(path) in tracked_files

    def abs_root_path(self, path):
        res = Path(self.root) / path
        return utils.safe_abs_path(res)

    def get_dirty_files(self):
        """
        Returns a list of all files which are dirty (not committed), either staged or in the working
        directory.
        """
        dirty_files = set()

        # Get staged files
        staged_files = self.repo.git.diff("--name-only", "--cached").splitlines()
        dirty_files.update(staged_files)

        # Get unstaged files
        unstaged_files = self.repo.git.diff("--name-only").splitlines()
        dirty_files.update(unstaged_files)

        return list(dirty_files)

    def is_dirty(self, path=None):
        if path and not self.path_in_repo(path):
            return True

        return self.repo.is_dirty(path=path)

    def get_head_commit(self):
        try:
            return self.repo.head.commit
        except (ValueError,) + ANY_GIT_ERROR:
            return None

    def get_head_commit_sha(self, short=False):
        commit = self.get_head_commit()
        if not commit:
            return
        if short:
            return commit.hexsha[:7]
        return commit.hexsha

    def get_head_commit_message(self, default=None):
        commit = self.get_head_commit()
        if not commit:
            return default
        return commit.message