import os
import shutil
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any, List, Union
import functools
from tqdm.auto import tqdm
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError, RepositoryNotFoundError

from .progress_tracker import CustomProgressTqdm, DownloadProgressTracker
from .avatar_fetcher import get_avatar_url_for_repo

# Default path for model storage
DEFAULT_MODEL_SAVING_PATH = "~/.cache/nexa.ai/nexa_sdk/models/"


@dataclass
class DownloadedModel:
    """Data class representing a downloaded model with all its metadata."""
    repo_id: str
    files: List[str]
    folder_type: str  # 'owner_repo' or 'direct_repo'
    local_path: str
    size_bytes: int
    file_count: int
    full_repo_download_complete: bool = True  # True if no incomplete downloads detected
    pipeline_tag: Optional[str] = None  # Pipeline tag from HuggingFace model info
    download_time: Optional[str] = None  # ISO format timestamp of download
    avatar_url: Optional[str] = None  # Avatar URL for the model author
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility."""
        result = {
            'repo_id': self.repo_id,
            'files': self.files,
            'folder_type': self.folder_type,
            'local_path': self.local_path,
            'size_bytes': self.size_bytes,
            'file_count': self.file_count,
            'full_repo_download_complete': self.full_repo_download_complete,
            'pipeline_tag': self.pipeline_tag,
            'download_time': self.download_time,
            'avatar_url': self.avatar_url
        }
        return result


##########################################################################
#                        List downloaded models                          #
##########################################################################


def _check_for_incomplete_downloads(directory_path: str) -> bool:
    """
    Check if there are incomplete downloads in the model directory.
    
    This function checks for the presence of .incomplete or .lock files
    in the .cache/huggingface/download directory within the model folder,
    which indicates that the model download has not completed.
    
    Args:
        directory_path: Path to the model directory
        
    Returns:
        bool: True if download is complete (no incomplete files found), 
              False if incomplete downloads are detected
    """
    # Check for .cache/huggingface/download directory
    cache_dir = os.path.join(directory_path, '.cache', 'huggingface', 'download')
    
    # If the cache directory doesn't exist, assume download is complete
    if not os.path.exists(cache_dir):
        return True
    
    try:
        # Walk through the cache directory to find incomplete or lock files
        for root, dirs, files in os.walk(cache_dir):
            for filename in files:
                # Check for .incomplete or .lock files
                if filename.endswith('.incomplete'):
                    return False  # Found incomplete download
        
        # No incomplete files found
        return True
    except (OSError, IOError):
        # If we can't access the directory, assume download is complete
        return True


def _load_download_metadata(directory_path: str) -> Dict[str, Any]:
    """Load download metadata from download_metadata.json if it exists."""
    metadata_path = os.path.join(directory_path, 'download_metadata.json')
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _save_download_metadata(directory_path: str, metadata: Dict[str, Any]) -> None:
    """Save download metadata to download_metadata.json."""
    metadata_path = os.path.join(directory_path, 'download_metadata.json')
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    except IOError:
        # If we can't save metadata, don't fail the download
        pass


def _get_directory_size_and_files(directory_path: str) -> tuple[int, List[str]]:
    """Get total size and list of files in a directory."""
    total_size = 0
    files = []
    
    try:
        for root, dirs, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    # Store relative path from the directory
                    rel_path = os.path.relpath(file_path, directory_path)
                    files.append(rel_path)
                except (OSError, IOError):
                    # Skip files that can't be accessed
                    continue
    except (OSError, IOError):
        # Skip directories that can't be accessed
        pass
    
    return total_size, files


def _scan_for_repo_folders(base_path: str) -> List[DownloadedModel]:
    """Scan a directory for repository folders and return model information."""
    models = []
    
    try:
        if not os.path.exists(base_path):
            return models
        
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            
            # Skip non-directory items
            if not os.path.isdir(item_path):
                continue
            
            # Check if this might be an owner folder by looking for subdirectories
            has_subdirs = False
            direct_files = []
            
            try:
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if os.path.isdir(subitem_path):
                        has_subdirs = True
                        # This looks like owner/repo structure
                        size_bytes, files = _get_directory_size_and_files(subitem_path)
                        if files:  # Only include if there are files
                            # Check if the download is complete
                            download_complete = _check_for_incomplete_downloads(subitem_path)
                            # Load metadata if it exists
                            metadata = _load_download_metadata(subitem_path)
                            models.append(DownloadedModel(
                                repo_id=f"{item}/{subitem}",
                                files=files,
                                folder_type='owner_repo',
                                local_path=subitem_path,
                                size_bytes=size_bytes,
                                file_count=len(files),
                                full_repo_download_complete=download_complete,
                                pipeline_tag=metadata.get('pipeline_tag'),
                                download_time=metadata.get('download_time'),
                                avatar_url=metadata.get('avatar_url')
                            ))
                    else:
                        direct_files.append(subitem)
            except (OSError, IOError):
                # Skip directories that can't be accessed
                continue
            
            # Direct repo folder (no owner structure)
            if not has_subdirs and direct_files:
                size_bytes, files = _get_directory_size_and_files(item_path)
                if files:  # Only include if there are files
                    # Check if the download is complete
                    download_complete = _check_for_incomplete_downloads(item_path)
                    # Load metadata if it exists
                    metadata = _load_download_metadata(item_path)
                    models.append(DownloadedModel(
                        repo_id=item,
                        files=files,
                        folder_type='direct_repo',
                        local_path=item_path,
                        size_bytes=size_bytes,
                        file_count=len(files),
                        full_repo_download_complete=download_complete,
                        pipeline_tag=metadata.get('pipeline_tag'),
                        download_time=metadata.get('download_time'),
                        avatar_url=metadata.get('avatar_url')
                    ))
    
    except (OSError, IOError):
        # Skip if base path can't be accessed
        pass
    
    return models


def list_downloaded_models(local_dir: Optional[str] = None) -> List[DownloadedModel]:
    """
    List all downloaded models in the specified directory.
    
    This function scans the local directory for downloaded models and returns
    information about each repository including files, size, and folder structure.
    
    It handles different folder naming conventions:
    - Owner/repo structure (e.g., "microsoft/DialoGPT-small")
    - Direct repo folders (repos without owner prefix)
    
    Args:
        local_dir (str, optional): Directory to scan for downloaded models.
                                  If None, uses DEFAULT_MODEL_SAVING_PATH.
    
    Returns:
        List[DownloadedModel]: List of DownloadedModel objects with attributes:
            - repo_id: str - Repository ID (e.g., "owner/repo")
            - files: List[str] - List of relative file paths in the repository
            - folder_type: str - 'owner_repo' or 'direct_repo'
            - local_path: str - Full path to the model directory
            - size_bytes: int - Total size of all files in bytes
            - file_count: int - Number of files in the repository
            - full_repo_download_complete: bool - True if no incomplete downloads detected, 
                                                  False if .incomplete or .lock files exist
            - pipeline_tag: Optional[str] - Pipeline tag from HuggingFace model info
            - download_time: Optional[str] - ISO format timestamp when the model was downloaded
            - avatar_url: Optional[str] - Avatar URL for the model author
    """
    
    # Set up local directory
    if local_dir is None:
        local_dir = os.path.expanduser(DEFAULT_MODEL_SAVING_PATH)
    
    local_dir = os.path.abspath(local_dir)
    
    if not os.path.exists(local_dir):
        return []
    
    # Scan for repository folders
    models = _scan_for_repo_folders(local_dir)
    
    # Sort by repo_id for consistent output
    models.sort(key=lambda x: x.repo_id)
    
    return models


##########################################################################
#                        Remove model functions                          #
##########################################################################


def _parse_model_path(model_path: str) -> tuple[str, str | None]:
    """
    Parse model_path to extract repo_id and optional filename.
    
    Examples:
        "microsoft/DialoGPT-small" -> ("microsoft/DialoGPT-small", None)
        "microsoft/DialoGPT-small/pytorch_model.bin" -> ("microsoft/DialoGPT-small", "pytorch_model.bin") 
        "Qwen/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf" -> ("Qwen/Qwen3-4B-GGUF", "Qwen3-4B-Q4_K_M.gguf")
    
    Args:
        model_path: The model path string
        
    Returns:
        Tuple of (repo_id, filename) where filename can be None
    """
    parts = model_path.strip().split('/')
    
    if len(parts) < 2:
        # Invalid format, assume it's just a repo name without owner
        return model_path, None
    elif len(parts) == 2:
        # Format: "owner/repo"
        return model_path, None
    else:
        # Format: "owner/repo/file" or "owner/repo/subdir/file"
        repo_id = f"{parts[0]}/{parts[1]}"
        filename = '/'.join(parts[2:])
        return repo_id, filename


def _validate_and_parse_input(model_path: str) -> tuple[str, Optional[str]]:
    """Validate input and parse model path."""
    if not model_path or not isinstance(model_path, str) or not model_path.strip():
        raise ValueError("model_path is required and must be a non-empty string")
    
    model_path = model_path.strip()
    return _parse_model_path(model_path)


def _find_target_model(repo_id: str, local_dir: str) -> DownloadedModel:
    """Find and validate the target model exists."""
    downloaded_models = list_downloaded_models(local_dir)
    
    for model in downloaded_models:
        if model.repo_id == repo_id:
            return model
    
    available_repos = [model.repo_id for model in downloaded_models]
    raise FileNotFoundError(
        f"Repository '{repo_id}' not found in downloaded models. "
        f"Available repositories: {available_repos}"
    )


def _clean_empty_owner_directory(target_model: DownloadedModel) -> None:
    """Remove empty owner directory if applicable."""
    if target_model.folder_type != 'owner_repo':
        return
    
    parent_dir = os.path.dirname(target_model.local_path)
    try:
        if os.path.exists(parent_dir) and not os.listdir(parent_dir):
            os.rmdir(parent_dir)
    except OSError:
        pass


def _remove_specific_file(target_model: DownloadedModel, file_name: str, local_dir: str) -> DownloadedModel:
    """Remove a specific file from the repository."""
    # Validate file exists in model
    if file_name not in target_model.files:
        raise FileNotFoundError(
            f"File '{file_name}' not found in repository '{target_model.repo_id}'. "
            f"Available files: {target_model.files[:10]}{'...' if len(target_model.files) > 10 else ''}"
        )
    
    # Construct full file path and validate it exists on disk
    file_path = os.path.join(target_model.local_path, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File does not exist on disk: {file_path}")
    
    # Get file size before removal
    try:
        file_size = os.path.getsize(file_path)
    except OSError:
        file_size = 0
    
    # Remove the file
    try:
        os.remove(file_path)
    except OSError as e:
        raise OSError(f"Failed to remove file '{file_path}': {e}")
    
    # Create updated model object
    updated_files = [f for f in target_model.files if f != file_name]
    updated_size = target_model.size_bytes - file_size
    # Re-check download completeness after file removal
    download_complete = _check_for_incomplete_downloads(target_model.local_path)
    updated_model = DownloadedModel(
        repo_id=target_model.repo_id,
        files=updated_files,
        folder_type=target_model.folder_type,
        local_path=target_model.local_path,
        size_bytes=updated_size,
        file_count=len(updated_files),
        full_repo_download_complete=download_complete
    )
    
    # If no files left, remove the entire directory
    if len(updated_files) == 0:
        try:
            shutil.rmtree(target_model.local_path)
            _clean_empty_owner_directory(target_model)
        except OSError:
            pass
    
    return updated_model


def _remove_entire_repository(target_model: DownloadedModel, local_dir: str) -> DownloadedModel:
    """Remove the entire repository and clean up."""
    # Remove the directory and all its contents
    try:
        shutil.rmtree(target_model.local_path)
    except OSError as e:
        raise OSError(f"Failed to remove directory '{target_model.local_path}': {e}")
    
    # Clean up associated resources
    _clean_empty_owner_directory(target_model)
    
    return target_model


def remove_model_or_file(
    model_path: str,
    local_dir: Optional[str] = None
) -> DownloadedModel:
    """
    Remove a downloaded model or specific file by repository ID or file path.
    
    This function supports two modes:
    1. Remove entire repository: "microsoft/DialoGPT-small" 
    2. Remove specific file: "Qwen/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf"
    
    For entire repository removal, it removes the directory and all files. For specific file removal, it only
    removes that file and updates the repository metadata.
    
    Args:
        model_path (str): Required. Either:
                         - Repository ID (e.g., "microsoft/DialoGPT-small") - removes entire repo
                         - File path (e.g., "Qwen/Qwen3-4B-GGUF/model.gguf") - removes specific file
        local_dir (str, optional): Directory to search for downloaded models.
                                  If None, uses DEFAULT_MODEL_SAVING_PATH.
    
    Returns:
        DownloadedModel: The model object representing what was removed from disk.
                        For file removal, returns updated model info after file removal.
        
    Raises:
        ValueError: If model_path is invalid (empty or None)
        FileNotFoundError: If the repository or file is not found in downloaded models
        OSError: If there's an error removing files from disk
    """
    # Validate input and parse path
    repo_id, file_name = _validate_and_parse_input(model_path)
    
    # Set up local directory
    if local_dir is None:
        local_dir = os.path.expanduser(DEFAULT_MODEL_SAVING_PATH)
    
    local_dir = os.path.abspath(local_dir)
    
    if not os.path.exists(local_dir):
        raise FileNotFoundError(f"Local directory does not exist: {local_dir}")
    
    # Find the target model
    target_model = _find_target_model(repo_id, local_dir)
    
    # Delegate to appropriate removal function
    if file_name:
        return _remove_specific_file(target_model, file_name, local_dir)
    else:
        return _remove_entire_repository(target_model, local_dir)


##########################################################################
#                        Check model existence functions                #
##########################################################################


def check_model_existence(
    model_path: str,
    local_dir: Optional[str] = None
) -> bool:
    """
    Check if a downloaded model or specific file exists locally.
    
    This function supports two modes:
    1. Check entire repository: "microsoft/DialoGPT-small" 
    2. Check specific file: "Qwen/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf"
    
    Args:
        model_path (str): Required. Either:
                         - Repository ID (e.g., "microsoft/DialoGPT-small") - checks entire repo
                         - File path (e.g., "Qwen/Qwen3-4B-GGUF/model.gguf") - checks specific file
        local_dir (str, optional): Directory to search for downloaded models.
                                  If None, uses DEFAULT_MODEL_SAVING_PATH.
    
    Returns:
        bool: True if the requested item exists, False otherwise
        
    Raises:
        ValueError: If model_path is invalid (empty or None)
    """
    # Validate input and parse path
    repo_id, file_name = _validate_and_parse_input(model_path)
    
    # Set up local directory
    if local_dir is None:
        local_dir = os.path.expanduser(DEFAULT_MODEL_SAVING_PATH)
    
    local_dir = os.path.abspath(local_dir)
    
    # Return False if local directory doesn't exist
    if not os.path.exists(local_dir):
        return False
    
    # Get all downloaded models
    downloaded_models = list_downloaded_models(local_dir)
    
    # Find the target model
    for model in downloaded_models:
        if model.repo_id == repo_id:
            # If no specific file requested, repository existence is sufficient
            if file_name is None:
                return True
            else:
                # Check specific file existence
                return file_name in model.files
    
    return False


##########################################################################
#                  HuggingFace Downloader Class                         #
##########################################################################


class HuggingFaceDownloader:
    """Class to handle downloads from HuggingFace Hub with unified API usage."""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        token: Union[bool, str, None] = None,
        enable_transfer: bool = True
    ):
        """
        Initialize the downloader with HuggingFace API.
        
        Args:
            endpoint: Custom endpoint URL (e.g., "https://hf-mirror.com"). 
                     If None, uses default HuggingFace Hub.
            token: Authentication token for private repositories.
            enable_transfer: Whether to enable HF transfer for faster downloads.
        """
        # Always create an HfApi instance - either with custom endpoint or default
        self.token = token if isinstance(token, str) else False # False means disable authentication
        self.api = HfApi(endpoint=endpoint, token=self.token) if endpoint else HfApi(token=self.token)
        self.enable_transfer = enable_transfer
        self.original_hf_transfer = None
        self.endpoint = endpoint  # Store endpoint for avatar fetching
        
    def _create_repo_directory(self, local_dir: str, repo_id: str) -> str:
        """Create a directory structure for the repository following HF convention."""
        if '/' in repo_id:
            # Standard format: owner/repo
            owner, repo = repo_id.split('/', 1)
            repo_dir = os.path.join(local_dir, owner, repo)
        else:
            # Direct repo name without owner
            repo_dir = os.path.join(local_dir, repo_id)
        
        os.makedirs(repo_dir, exist_ok=True)
        return repo_dir
    
    def _created_dir_if_not_exists(self, local_dir: Optional[str]) -> str:
        """Create directory if it doesn't exist and return the expanded path."""
        if local_dir is None:
            local_dir = DEFAULT_MODEL_SAVING_PATH
        
        local_dir = os.path.expanduser(local_dir)
        os.makedirs(local_dir, exist_ok=True)
        return local_dir
    
    def _get_repo_info_for_progress(
        self,
        repo_id: str,
        file_name: Optional[Union[str, List[str]]] = None
    ) -> tuple[int, int]:
        """Get total repository size and file count for progress tracking."""
        try:
            info = self.api.model_info(repo_id, files_metadata=True, token=self.token)
            
            total_size = 0
            file_count = 0
            
            if info.siblings:
                for sibling in info.siblings:
                    # Handle different file_name types
                    if file_name is not None:
                        if isinstance(file_name, str):
                            # Single file - only count if it matches
                            if sibling.rfilename != file_name:
                                continue
                        elif isinstance(file_name, list):
                            # Multiple files - only count if in the list
                            if sibling.rfilename not in file_name:
                                continue
                    
                    # For all matching files (or all files if file_name is None)
                    if hasattr(sibling, 'size') and sibling.size is not None:
                        total_size += sibling.size
                        file_count += 1
                    else:
                        # Count files without size info
                        file_count += 1
            
            return total_size, file_count if file_count > 0 else 1
        except Exception:
            # If we can't get info, return defaults
            return 0, 1
    
    def _validate_and_setup_params(
        self,
        repo_id: str,
        file_name: Optional[Union[str, List[str]]]
    ) -> tuple[str, Optional[Union[str, List[str]]]]:
        """Validate and normalize input parameters."""
        if not repo_id:
            raise ValueError("repo_id is required")
        
        repo_id = repo_id.strip()
        
        # Handle file_name parameter
        if file_name is not None:
            if isinstance(file_name, str):
                file_name = file_name.strip()
                if not file_name:
                    file_name = None
            elif isinstance(file_name, list):
                # Filter out empty strings and strip whitespace
                file_name = [f.strip() for f in file_name if f and f.strip()]
                if not file_name:
                    file_name = None
            else:
                raise ValueError("file_name must be a string, list of strings, or None")
        
        return repo_id, file_name
    
    def _setup_progress_tracker(
        self,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]],
        show_progress: bool,
        repo_id: str,
        file_name: Optional[Union[str, List[str]]]
    ) -> Optional[DownloadProgressTracker]:
        """Initialize progress tracker if callback is provided."""
        if not progress_callback:
            return None
        
        progress_tracker = DownloadProgressTracker(progress_callback, show_progress)
        # Get repo info for progress tracking - now handles all cases
        total_size, file_count = self._get_repo_info_for_progress(repo_id, file_name)
        progress_tracker.set_repo_info(total_size, file_count)
        return progress_tracker
    
    def _setup_hf_transfer_env(self) -> None:
        """Set up HF transfer environment."""
        self.original_hf_transfer = os.environ.get("HF_HUB_ENABLE_HF_TRANSFER")
        if self.enable_transfer:
            os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    
    def _cleanup_hf_transfer_env(self) -> None:
        """Restore original HF transfer environment."""
        if self.original_hf_transfer is not None:
            os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = self.original_hf_transfer
        else:
            os.environ.pop("HF_HUB_ENABLE_HF_TRANSFER", None)
    
    def _validate_repository_and_get_info(
        self,
        repo_id: str,
        progress_tracker: Optional[DownloadProgressTracker]
    ):
        """Validate repository exists and get info."""
        try:
            info = self.api.model_info(repo_id, token=self.token)
            return info
        except RepositoryNotFoundError:
            error_msg = f"Repository '{repo_id}' not found. Please check the repository ID."
            if progress_tracker:
                progress_tracker.set_error(error_msg)
            raise RepositoryNotFoundError(error_msg)
        except HfHubHTTPError as e:
            if e.response.status_code == 404:
                error_msg = f"Repository '{repo_id}' not found. Please check the repository ID."
                if progress_tracker:
                    progress_tracker.set_error(error_msg)
                raise RepositoryNotFoundError(error_msg)
            else:
                error_msg = f"HTTP error while accessing repository '{repo_id}': {e}"
                if progress_tracker:
                    progress_tracker.set_error(error_msg)
                raise HfHubHTTPError(error_msg)
    
    def _validate_file_exists_in_repo(
        self,
        file_name: str,
        info,
        repo_id: str,
        progress_tracker: Optional[DownloadProgressTracker]
    ) -> None:
        """Validate that the file exists in the repository."""
        file_exists = False
        if info.siblings:
            for sibling in info.siblings:
                if sibling.rfilename == file_name:
                    file_exists = True
                    break
        
        if not file_exists:
            available_files = [sibling.rfilename for sibling in info.siblings] if info.siblings else []
            error_msg = (
                f"File '{file_name}' not found in repository '{repo_id}'. "
                f"Available files: {available_files[:10]}{'...' if len(available_files) > 10 else ''}"
            )
            if progress_tracker:
                progress_tracker.set_error(error_msg)
                progress_tracker.stop_tracking()
            raise ValueError(error_msg)
    
    def _check_file_exists_and_valid(
        self,
        file_path: str,
        expected_size: Optional[int] = None
    ) -> bool:
        """Check if a file exists and is valid (non-empty, correct size if known)."""
        if not os.path.exists(file_path):
            return False
        
        # Check file is not empty
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False
        except (OSError, IOError):
            return False
        
        # If we have expected size, check it matches
        if expected_size is not None and file_size != expected_size:
            return False
        
        # If no expected size, just check that file is not empty
        return os.path.getsize(file_path) > 0
    
    def _fetch_and_save_metadata(self, repo_id: str, local_dir: str) -> None:
        """Fetch model info and save metadata after successful download."""
        try:
            # Fetch model info to get pipeline_tag
            info = self.api.model_info(repo_id, token=self.token)
            pipeline_tag = info.pipeline_tag if hasattr(info, 'pipeline_tag') else None
            
            # Get avatar URL
            avatar_url = get_avatar_url_for_repo(repo_id, custom_endpoint=self.endpoint)
            
            # Prepare metadata
            metadata = {
                'pipeline_tag': pipeline_tag,
                'download_time': datetime.now().isoformat(),
                'avatar_url': avatar_url
            }
            
            # Save metadata to the repository directory
            _save_download_metadata(local_dir, metadata)
            
        except Exception:
            # Don't fail the download if metadata fetch fails
            pass
    
    def _download_single_file(
        self,
        repo_id: str,
        file_name: str,
        local_dir: str,
        progress_tracker: Optional[DownloadProgressTracker],
        force_download: bool = False
    ) -> str:
        """Download a single file from the repository using HuggingFace Hub API."""
        # Create repo-specific directory for the single file
        file_local_dir = self._create_repo_directory(local_dir, repo_id)
        
        # Check if file already exists
        local_file_path = os.path.join(file_local_dir, file_name)
        if not force_download and self._check_file_exists_and_valid(local_file_path):
            print(f"✓ File already exists, skipping: {file_name}")
            # Stop progress tracking
            if progress_tracker:
                progress_tracker.stop_tracking()
            return local_file_path
        
        try:
            # Note: hf_hub_download doesn't support tqdm_class parameter
            # Progress tracking works through the global tqdm monkey patching
            downloaded_path = self.api.hf_hub_download(
                repo_id=repo_id,
                filename=file_name,
                local_dir=file_local_dir,
                local_dir_use_symlinks=False,
                token=self.token,
                force_download=force_download
            )
            
            # Stop progress tracking
            if progress_tracker:
                progress_tracker.stop_tracking()
            
            # Save metadata after successful download
            self._fetch_and_save_metadata(repo_id, file_local_dir)
            
            return downloaded_path
            
        except HfHubHTTPError as e:
            error_msg = f"Error downloading file '{file_name}': {e}"
            if progress_tracker:
                progress_tracker.set_error(error_msg)
                progress_tracker.stop_tracking()
            if e.response.status_code == 404:
                raise ValueError(f"File '{file_name}' not found in repository '{repo_id}'")
            else:
                raise HfHubHTTPError(error_msg)
    
    def _download_entire_repository(
        self,
        repo_id: str,
        local_dir: str,
        progress_tracker: Optional[DownloadProgressTracker],
        force_download: bool = False
    ) -> str:
        """Download the entire repository."""
        # Create a subdirectory for this specific repo
        repo_local_dir = self._create_repo_directory(local_dir, repo_id)
        
        # Check if repository already exists (basic check for directory existence)
        if not force_download and os.path.exists(repo_local_dir) and os.listdir(repo_local_dir):
            print(f"✓ Repository already exists, skipping: {repo_id}")
            # Stop progress tracking
            if progress_tracker:
                progress_tracker.stop_tracking()
            return repo_local_dir
        
        try:
            download_kwargs = {
                'repo_id': repo_id,
                'local_dir': repo_local_dir,
                'local_dir_use_symlinks': False,
                'token': self.token,
                'force_download': force_download
            }
            
            # Add tqdm_class if progress tracking is enabled
            if progress_tracker:
                download_kwargs['tqdm_class'] = CustomProgressTqdm
            
            downloaded_path = self.api.snapshot_download(**download_kwargs)
            
            # Stop progress tracking
            if progress_tracker:
                progress_tracker.stop_tracking()
            
            # Save metadata after successful download
            self._fetch_and_save_metadata(repo_id, repo_local_dir)
            
            return downloaded_path
            
        except HfHubHTTPError as e:
            error_msg = f"Error downloading repository '{repo_id}': {e}"
            if progress_tracker:
                progress_tracker.set_error(error_msg)
                progress_tracker.stop_tracking()
            raise HfHubHTTPError(error_msg)
    
    def _download_multiple_files_from_hf(
        self,
        repo_id: str,
        file_names: List[str],
        local_dir: str,
        progress_tracker: Optional[DownloadProgressTracker],
        force_download: bool = False
    ) -> str:
        """Download multiple specific files from HuggingFace Hub."""
        # Create repo-specific directory
        repo_local_dir = self._create_repo_directory(local_dir, repo_id)
        
        # Create overall progress bar for multiple files
        overall_progress = tqdm(
            total=len(file_names),
            unit='file',
            desc=f"Downloading {len(file_names)} files from {repo_id}",
            position=0,
            leave=True
        )
        
        try:
            for file_name in file_names:
                overall_progress.set_postfix_str(f"Current: {os.path.basename(file_name)}")
                
                # Check if file already exists
                local_file_path = os.path.join(repo_local_dir, file_name)
                if not force_download and self._check_file_exists_and_valid(local_file_path):
                    print(f"✓ File already exists, skipping: {file_name}")
                    overall_progress.update(1)
                    continue
                
                # Download each file using hf_hub_download
                self.api.hf_hub_download(
                    repo_id=repo_id,
                    filename=file_name,
                    local_dir=repo_local_dir,
                    local_dir_use_symlinks=False,
                    token=self.token,
                    force_download=force_download
                )
                
                overall_progress.update(1)
            
            overall_progress.close()
            
            # Stop progress tracking
            if progress_tracker:
                progress_tracker.stop_tracking()
            
            # Save metadata after successful download
            self._fetch_and_save_metadata(repo_id, repo_local_dir)
            
            return repo_local_dir
            
        except HfHubHTTPError as e:
            overall_progress.close()
            error_msg = f"Error downloading files from '{repo_id}': {e}"
            if progress_tracker:
                progress_tracker.set_error(error_msg)
                progress_tracker.stop_tracking()
            raise HfHubHTTPError(error_msg)
        except Exception as e:
            overall_progress.close()
            if progress_tracker:
                progress_tracker.set_error(str(e))
                progress_tracker.stop_tracking()
            raise
    
    def download(
        self,
        repo_id: str,
        file_name: Optional[Union[str, List[str]]] = None,
        local_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        show_progress: bool = True,
        force_download: bool = False
    ) -> str:
        """
        Main download method that handles all download scenarios.
        
        Args:
            repo_id: Repository ID to download from
            file_name: Optional file name(s) to download
            local_dir: Local directory to save files
            progress_callback: Callback for progress updates
            show_progress: Whether to show progress bar
            force_download: Force re-download even if files exist
            
        Returns:
            Path to downloaded file or directory
        """
        # Validate and normalize parameters
        repo_id, file_name = self._validate_and_setup_params(repo_id, file_name)
        
        # Set up local directory
        local_dir = self._created_dir_if_not_exists(local_dir)
        
        # Set up progress tracker
        file_name_for_progress = file_name if isinstance(file_name, str) else None
        progress_tracker = self._setup_progress_tracker(
            progress_callback, show_progress, repo_id, file_name_for_progress
        )
        
        # Set up HF transfer environment
        self._setup_hf_transfer_env()
        
        try:
            # Validate repository and get info
            info = self._validate_repository_and_get_info(repo_id, progress_tracker)
            
            # Start progress tracking
            if progress_tracker:
                progress_tracker.start_tracking()
            
            # Choose download strategy based on file_name
            if file_name is None:
                # Download entire repository
                return self._download_entire_repository(
                    repo_id, local_dir, progress_tracker, force_download
                )
            elif isinstance(file_name, str):
                # Download specific single file
                self._validate_file_exists_in_repo(file_name, info, repo_id, progress_tracker)
                return self._download_single_file(
                    repo_id, file_name, local_dir, progress_tracker, force_download
                )
            else:  # file_name is a list
                # Download multiple specific files
                # Validate all files exist
                for fname in file_name:
                    self._validate_file_exists_in_repo(fname, info, repo_id, progress_tracker)
                
                return self._download_multiple_files_from_hf(
                    repo_id, file_name, local_dir, progress_tracker, force_download
                )
        
        except Exception as e:
            # Handle any unexpected errors
            if progress_tracker and progress_tracker.download_status != "error":
                progress_tracker.set_error(str(e))
                progress_tracker.stop_tracking()
            raise
        
        finally:
            # Restore original HF transfer setting
            self._cleanup_hf_transfer_env()


##########################################################################
#                    Public Download Function                           #
##########################################################################


def download_from_huggingface(
    repo_id: str,
    file_name: Optional[Union[str, List[str]]] = None,
    local_dir: Optional[str] = None,
    enable_transfer: bool = True,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_progress: bool = True,
    token: Union[bool, str, None] = None,
    custom_endpoint: Optional[str] = None,
    force_download: bool = False
) -> str:
    """
    Download models or files from HuggingFace Hub or custom mirror endpoints.
    
    Args:
        repo_id (str): Required. The repository ID to download from (e.g., "microsoft/DialoGPT-medium")
        file_name (Union[str, List[str]], optional): Single filename or list of filenames to download.
                                                     If None, downloads entire repo.
        local_dir (str, optional): Local directory to save files. If None, uses DEFAULT_MODEL_SAVING_PATH.
        enable_transfer (bool, optional): Whether to enable HF transfer for faster downloads. Default True.
        progress_callback (Callable, optional): Callback function to receive progress updates. 
                                               Function receives a dict with progress information.
        show_progress (bool, optional): Whether to show a unified progress bar in the terminal. Default True.
                                       Only works when progress_callback is provided.
        token (Union[bool, str, None], optional): A token to be used for the download.
                                                 - If True, the token is read from the HuggingFace config folder.
                                                 - If a string, it's used as the authentication token.
                                                 - If None, uses default behavior.
        custom_endpoint (str, optional): A custom HuggingFace-compatible endpoint URL.
                                        Should be ONLY the base endpoint without any paths.
                                        Examples:
                                        - "https://hf-mirror.com"
                                        - "https://huggingface.co" (default)
                                        The endpoint will be used to initialize HfApi for all downloads.
        force_download (bool, optional): If True, download files even if they already exist locally.
                                        Default False (skip existing files).
    
    Returns:
        str: Path to the downloaded file or directory
        
    Raises:
        ValueError: If repo_id is invalid or file_name doesn't exist in the repo
        RepositoryNotFoundError: If the repository doesn't exist
        HfHubHTTPError: If there's an HTTP error during download
        
    Progress Callback Data Format:
        {
            'status': str,  # 'idle', 'downloading', 'completed', 'error'
            'error_message': str,  # Only present if status is 'error'
            'progress': {
                'total_downloaded': int,  # Bytes downloaded
                'total_size': int,       # Total bytes to download
                'percentage': float,     # Progress percentage (0-100)
                'files_active': int,     # Number of files currently downloading
                'files_total': int,      # Total number of files
                'known_total': bool      # Whether total size is known
            },
            'speed': {
                'bytes_per_second': float,  # Download speed in bytes/sec
                'formatted': str            # Human readable speed (e.g., "1.2 MB/s")
            },
            'formatting': {
                'downloaded': str,  # Human readable downloaded size
                'total_size': str   # Human readable total size
            },
            'timing': {
                'elapsed_seconds': float,  # Time since download started
                'eta_seconds': float,      # Estimated time remaining
                'start_time': float        # Download start timestamp
            }
        }
    """
    # Create downloader instance with custom endpoint if provided
    downloader = HuggingFaceDownloader(
        endpoint=custom_endpoint, 
        token=token, 
        enable_transfer=enable_transfer
    )
    
    # Use the downloader to perform the download
    return downloader.download(
        repo_id=repo_id,
        file_name=file_name,
        local_dir=local_dir,
        progress_callback=progress_callback,
        show_progress=show_progress,
        force_download=force_download
    )


##########################################################################
#                       Auto-download decorator                         #
##########################################################################


def auto_download_model(func: Callable) -> Callable:
    """
    Decorator that automatically downloads models from HuggingFace if they don't exist locally.
    
    This decorator should be applied to __init__ methods that take a name_or_path parameter.
    If name_or_path doesn't exist as a local file/directory, it will attempt to download
    it from HuggingFace Hub using the download_from_huggingface function.
    
    The name_or_path can be in formats like:
    - "microsoft/DialoGPT-small" (downloads entire repo)  
    - "microsoft/DialoGPT-small/pytorch_model.bin" (downloads specific file)
    - "Qwen/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf" (downloads specific file)
    
    Optional kwargs that are extracted and passed to download_from_huggingface:
    - progress_callback: Callback function for download progress updates
    - token: HuggingFace authentication token for private repositories
    
    Args:
        func: The __init__ method to wrap
        
    Returns:
        Wrapped function that handles automatic model downloading
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find name_or_path in arguments
        # Assuming name_or_path is the first argument after self
        if len(args) >= 2:
            name_or_path = args[1]
            args_list = list(args)
            path_index = 1
            is_positional = True
        elif 'name_or_path' in kwargs:
            name_or_path = kwargs['name_or_path']
            path_index = None
            is_positional = False
        else:
            # No name_or_path found, call original function
            return func(*args, **kwargs)
        
        # Extract progress_callback and token from arguments
        progress_callback = None
        if 'progress_callback' in kwargs:
            progress_callback = kwargs.pop('progress_callback')  # Remove from kwargs to avoid passing to original func
        
        token = None
        if 'token' in kwargs:
            token = kwargs.pop('token')  # Remove from kwargs to avoid passing to original func
        
        # Check if name_or_path exists locally (file or directory)
        if os.path.exists(name_or_path):
            # Local path exists, use as-is without downloading
            return func(*args, **kwargs)
        
        # Model path doesn't exist locally, try to download from HuggingFace
        try:
            # Parse name_or_path to extract repo_id and filename
            repo_id, file_name = _parse_model_path(name_or_path)
            
            # Download the model
            downloaded_path = download_from_huggingface(
                repo_id=repo_id,
                file_name=file_name,
                local_dir=None,  # Use default cache directory
                enable_transfer=True,
                progress_callback=progress_callback,  # Use the extracted callback
                show_progress=True,
                token=token  # Use the extracted token
            )
            
            # Replace name_or_path with downloaded path
            if is_positional:
                args_list[path_index] = downloaded_path
                args = tuple(args_list)
            else:
                kwargs['name_or_path'] = downloaded_path
            
        except Exception as e:
            # Only handle download-related errors
            raise RuntimeError(f"Could not load model from '{name_or_path}': {e}")
        
        # Call original function with updated path (outside try-catch to let model creation errors bubble up)
        return func(*args, **kwargs)
    
    return wrapper
