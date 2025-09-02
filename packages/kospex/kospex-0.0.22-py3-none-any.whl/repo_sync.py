"""
Repository synchronization module for Kospex.

This module contains a refactored implementation of repository synchronization
functionality, extracted from kospex_core.py. It provides a more modular,
testable approach to syncing git repositories to database tables.

Classes:
    RepoSyncConfig: Configuration management for synchronization
    GitLogParser: Parse git log output into structured data
    RepoSyncDatabase: Handle database operations
    RepoSync: Main synchronization orchestrator
"""

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from sqlite_utils import Database

import kospex_utils as KospexUtils
import kospex_schema as KospexSchema
from kospex_git import KospexGit


class RepoSyncConfig:
    """Configuration management for repository synchronization."""

    def __init__(self,
                 db_path: Optional[str] = None,
                 use_scc: bool = True,
                 batch_size: int = 500,
                 timeout: int = 300,
                 progress_interval: int = 80):
        """
        Initialize synchronization configuration.

        Args:
            db_path: Path to SQLite database file. If None, uses default spike DB.
            use_scc: Whether to use scc for file metadata analysis.
            batch_size: Number of commits to process before progress update.
            timeout: Timeout in seconds for git commands.
            progress_interval: How often to print progress indicators.
        """
        self.db_path = db_path or os.path.expanduser("~/kospex/repo_sync_spike.db")
        self.use_scc = use_scc
        self.batch_size = batch_size
        self.timeout = timeout
        self.progress_interval = progress_interval

        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RepoSyncConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary."""
        return {
            'db_path': self.db_path,
            'use_scc': self.use_scc,
            'batch_size': self.batch_size,
            'timeout': self.timeout,
            'progress_interval': self.progress_interval
        }


class GitLogParser:
    """Parse git log output into structured commit and file data."""

    @staticmethod
    def parse_log_output(git_output: str) -> List[Dict[str, Any]]:
        """
        Parse git log --numstat output into commits list.

        Args:
            git_output: Raw output from git log command.

        Returns:
            List of commit dictionaries with file changes.
        """
        lines = git_output.strip().split('\n')
        commits = []
        current_commit = {}

        for line in lines:
            if line:
                if '\t' in line and len(line.split('\t')) == 3:
                    # File stats line: additions\tdeletions\tfilename
                    if 'filenames' in current_commit:
                        file_info = GitLogParser.parse_file_line(line)
                        current_commit['filenames'].append(file_info)
                elif '#' in line:
                    # Commit header line
                    if current_commit:  # Save previous commit
                        commits.append(current_commit)
                    current_commit = GitLogParser.parse_commit_line(line)
                    current_commit['filenames'] = []
                else:
                    # Handle edge cases or additional file info
                    if 'filenames' in current_commit:
                        current_commit['filenames'].append({
                            'file_path': line,
                            'additions': 0,
                            'deletions': 0,
                            'path_change': None
                        })
            else:
                # Empty line, end of current commit
                if current_commit:
                    commits.append(current_commit)
                current_commit = {}

        # Don't forget the last commit
        if current_commit:
            commits.append(current_commit)

        return commits

    @staticmethod
    def parse_commit_line(line: str) -> Dict[str, str]:
        """
        Parse commit header line with format: hash#author_date#committer_date#author_name#author_email#committer_name#committer_email

        Args:
            line: Commit header line from git log.

        Returns:
            Dictionary with commit metadata.
        """
        parts = line.split('#', 6)
        if len(parts) != 7:
            raise ValueError(f"Invalid commit line format: {line}")

        hash_value, author_datetime, committer_datetime, author_name, author_email, committer_name, committer_email = parts

        return {
            'hash': hash_value,
            'author_when': author_datetime,
            'committer_when': committer_datetime,
            'author_name': author_name,
            'author_email': author_email,
            'committer_name': committer_name,
            'committer_email': committer_email
        }

    @staticmethod
    def parse_file_line(line: str) -> Dict[str, Any]:
        """
        Parse file change line with format: additions\tdeletions\tfilename

        Args:
            line: File stats line from git log --numstat.

        Returns:
            Dictionary with file change information.
        """
        additions, deletions, filename = line.split('\t', 2)

        # Handle git rename events
        if "=>" in filename:
            file_path = KospexUtils.parse_git_rename_event(filename)
            path_change = filename
        else:
            file_path = filename
            path_change = None

        return {
            'file_path': file_path,
            'path_change': path_change,
            'additions': int(additions) if additions != '-' else 0,
            'deletions': int(deletions) if deletions != '-' else 0
        }


class RepoSyncDatabase:
    """Handle database operations for repository synchronization."""

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self.db: Optional[Database] = None

    def connect(self) -> None:
        """Connect to database and create tables if needed."""
        self.db = Database(self.db_path)

        # Create tables using existing schema
        self.db.execute(KospexSchema.SQL_CREATE_COMMITS)
        self.db.execute(KospexSchema.SQL_CREATE_COMMIT_FILES)
        self.db.execute(KospexSchema.SQL_CREATE_REPOS)

    def get_latest_commit_datetime(self, repo_id: str) -> Optional[str]:
        """
        Get the latest commit datetime for the given repo_id.

        Args:
            repo_id: Repository identifier.

        Returns:
            Latest commit datetime string or None if no commits found.
        """
        if not self.db:
            raise RuntimeError("Database not connected")

        cursor = self.db.execute(
            'SELECT MAX(committer_when) FROM commits WHERE _repo_id = ?',
            (repo_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def upsert_commits(self, commits_data: List[Dict[str, Any]]) -> None:
        """
        Upsert commit data to commits table.

        Args:
            commits_data: List of commit dictionaries.
        """
        if not self.db:
            raise RuntimeError("Database not connected")

        self.db.table(KospexSchema.TBL_COMMITS).upsert_all(
            commits_data,
            pk=['_repo_id', 'hash']
        )

    def upsert_commit_files(self, commit_files_data: List[Dict[str, Any]]) -> None:
        """
        Upsert commit file data to commit_files table.

        Args:
            commit_files_data: List of commit file dictionaries.
        """
        if not self.db:
            raise RuntimeError("Database not connected")

        self.db.table(KospexSchema.TBL_COMMIT_FILES).upsert_all(
            commit_files_data,
            pk=['file_path', '_repo_id', 'hash']
        )

    def update_repo_status(self, repo_data: Dict[str, Any]) -> None:
        """
        Update repository status and metadata.

        Args:
            repo_data: Repository metadata dictionary.
        """
        if not self.db:
            raise RuntimeError("Database not connected")

        self.db.table(KospexSchema.TBL_REPOS).upsert(
            repo_data,
            pk=['_repo_id']
        )

    def close(self) -> None:
        """Close database connection."""
        if self.db:
            self.db.close()
            self.db = None


class RepoSync:
    """Main repository synchronization orchestrator."""

    def __init__(self, config: Optional[RepoSyncConfig] = None):
        """
        Initialize repository synchronizer.

        Args:
            config: Synchronization configuration. If None, uses default config.
        """
        self.config = config or RepoSyncConfig()
        self.db = RepoSyncDatabase(self.config.db_path)
        self.git = KospexGit()
        self.parser = GitLogParser()
        self.original_cwd: Optional[str] = None
        self.repo_directory: Optional[str] = None

    def sync_repository(self,
                       repo_path: str,
                       limit: Optional[int] = None,
                       from_date: Optional[str] = None,
                       to_date: Optional[str] = None) -> int:
        """
        Main synchronization method.

        Args:
            repo_path: Path to git repository.
            limit: Maximum number of commits to sync.
            from_date: Start date for sync (ISO format).
            to_date: End date for sync (ISO format).

        Returns:
            Number of commits synchronized.
        """
        try:
            # Setup
            self._setup_repo(repo_path)
            self.db.connect()

            # Get repo information
            repo_id = self.git.get_repo_id()

            # Determine sync range
            if not from_date:
                latest_datetime = self.db.get_latest_commit_datetime(repo_id)
                if latest_datetime:
                    from_date = latest_datetime

            # Build and execute git command
            git_cmd = self._build_git_command(from_date, to_date, limit)
            git_output = self._execute_git_command(git_cmd)

            # Parse commits
            commits = self.parser.parse_log_output(git_output)

            if not commits:
                print("No new commits to sync.")
                return 0

            # Process commits
            commits_synced = self._process_commits(commits, repo_id)

            # Update repository status
            self._update_repo_status()

            print(f"Synced {commits_synced} total commits")
            return commits_synced

        finally:
            self._cleanup()

    def _setup_repo(self, repo_path: str) -> None:
        """Setup repository for synchronization."""
        if not KospexUtils.is_git(repo_path):
            raise ValueError(f"{repo_path} is not a git repository")

        fullpath = os.path.abspath(repo_path)
        self.original_cwd = os.getcwd()
        self.git.set_repo(fullpath)
        self.repo_directory = fullpath
        os.chdir(fullpath)

    def _build_git_command(self,
                          from_date: Optional[str],
                          to_date: Optional[str],
                          limit: Optional[int]) -> List[str]:
        """Build git log command with appropriate filters."""
        cmd = ['git', 'log', '--pretty=format:%H#%aI#%cI#%aN#%aE#%cN#%cE', '--numstat']

        if from_date and to_date:
            cmd += [f'--since={from_date}', f'--until={to_date}']
            print(f'Syncing commits from {from_date} to {to_date}...')
        elif from_date:
            cmd += [f'--since={from_date}']
            print(f"Syncing commits from {from_date}...")
        elif limit:
            cmd += ['-n', str(limit)]
            print(f'Syncing {limit} commits...')
        else:
            print('Syncing all commits...')

        return cmd

    def _execute_git_command(self, cmd: List[str]) -> str:
        """Execute git command and return output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                check=True
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Git command timed out after {self.config.timeout} seconds")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")

    def _process_commits(self, commits: List[Dict[str, Any]], repo_id: str) -> int:
        """Process and insert commit data to database."""
        print("About to insert commits into the database...")

        commits_data = []
        commit_files_data = []
        counter = 0

        for commit in commits:
            counter += 1

            # Prepare commit data
            files_count = len(commit['filenames'])
            commit['_files'] = files_count
            commit = self.git.add_git_to_dict(commit)

            # Extract file data before removing from commit
            commit_files = commit['filenames']
            del commit['filenames']

            commits_data.append(commit)

            # Prepare commit files data
            for file_info in commit_files:
                file_info = self.git.add_git_to_dict(file_info)
                file_info['hash'] = commit['hash']
                file_info['_ext'] = KospexUtils.get_extension(file_info['file_path'])
                file_info['committer_when'] = commit['committer_when']
                commit_files_data.append(file_info)

            # Progress indication
            self._display_progress(counter)

            # Batch processing
            if counter % self.config.batch_size == 0:
                self._batch_insert(commits_data, commit_files_data)
                commits_data = []
                commit_files_data = []
                print(f'\nSynced {counter} commits so far ...\n')

        # Insert remaining data
        if commits_data or commit_files_data:
            self._batch_insert(commits_data, commit_files_data)

        print()  # Final newline after progress indicators
        return counter

    def _batch_insert(self, commits_data: List[Dict[str, Any]], commit_files_data: List[Dict[str, Any]]) -> None:
        """Insert batch of commits and commit files."""
        if commits_data:
            self.db.upsert_commits(commits_data)
        if commit_files_data:
            self.db.upsert_commit_files(commit_files_data)

    def _display_progress(self, count: int) -> None:
        """Display sync progress to user."""
        print('+', end='')
        if count % self.config.progress_interval == 0:
            print()

    def _update_repo_status(self) -> None:
        """Update repository status with sync timestamp."""
        if not self.repo_directory:
            return

        last_sync = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()

        details = {
            'file_path': self.repo_directory,
            'last_sync': last_sync,
            'first_seen': KospexUtils.get_first_commit_date(self.repo_directory),
            'last_seen': KospexUtils.get_last_commit_date(self.repo_directory),
            'git_remote': self.git.get_remote_url()
        }

        details = self.git.add_git_to_dict(details)
        self.db.update_repo_status(details)

    def _cleanup(self) -> None:
        """Cleanup resources and restore working directory."""
        if self.original_cwd:
            os.chdir(self.original_cwd)
        self.db.close()


# Convenience function for simple usage
def sync_repo(repo_path: str,
              db_path: Optional[str] = None,
              **kwargs) -> int:
    """
    Convenience function to sync a repository.

    Args:
        repo_path: Path to git repository.
        db_path: Path to database file (optional).
        **kwargs: Additional sync parameters (limit, from_date, to_date).

    Returns:
        Number of commits synchronized.
    """
    config = RepoSyncConfig(db_path=db_path)
    syncer = RepoSync(config)
    return syncer.sync_repository(repo_path, **kwargs)
