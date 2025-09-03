"""
Progress tracking utilities for downloads with tqdm integration.

This module provides custom progress tracking classes that can monitor
download progress with callback support and customizable display options.
"""

import os
import sys
import time
from typing import Optional, Callable, Dict, Any
from tqdm.auto import tqdm


class CustomProgressTqdm(tqdm):
    """Custom tqdm that tracks progress but completely hides terminal output."""
    
    def __init__(self, *args, **kwargs):
        # Redirect output to devnull to completely suppress terminal output
        kwargs['file'] = open(os.devnull, 'w')
        kwargs['disable'] = False  # Keep enabled for tracking
        kwargs['leave'] = False  # Don't leave progress bar
        super().__init__(*args, **kwargs)
    
    def display(self, msg=None, pos=None):
        # Override display to show nothing
        pass
    
    def write(self, s, file=None, end="\n", nolock=False):
        # Override write to prevent any output
        pass
    
    def close(self):
        # Override close to avoid printing and properly close devnull
        if hasattr(self, 'fp') and self.fp and self.fp != sys.stdout and self.fp != sys.stderr:
            try:
                self.fp.close()
            except:
                pass
        self.disable = True
        super(tqdm, self).close()


class DownloadProgressTracker:
    """Progress tracker for HuggingFace downloads with callback support."""
    
    def __init__(self, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None, show_progress: bool = True):
        self.progress_data: Dict[str, Dict[str, Any]] = {}
        self.total_repo_size = 0
        self.repo_file_count = 0
        self.original_tqdm_update = None
        self.original_tqdm_init = None
        self.original_tqdm_display = None
        self.original_tqdm_write = None
        self.is_tracking = False
        
        # Callback function
        self.progress_callback = progress_callback
        
        # Progress display
        self.show_progress = show_progress
        self.last_display_length = 0
        
        # Speed tracking
        self.last_downloaded = None  # Use None to indicate no previous measurement
        self.last_time = None  # Use None to indicate no previous time measurement
        self.speed_history = []
        self.max_speed_history = 10
        
        # Download status
        self.download_status = "idle"  # idle, downloading, completed, error
        self.error_message = None
        self.download_start_time = None
    
    def set_repo_info(self, total_size: int, file_count: int):
        """Set the total repository size and file count before download."""
        self.total_repo_size = total_size
        self.repo_file_count = file_count
    
    def register_tqdm(self, tqdm_instance):
        """Register a tqdm instance for monitoring."""
        tqdm_id = str(id(tqdm_instance))
        self.progress_data[tqdm_id] = {
            'current': 0,
            'total': getattr(tqdm_instance, 'total', 0) or 0,
            'desc': getattr(tqdm_instance, 'desc', 'Unknown'),
            'tqdm_obj': tqdm_instance
        }
        # Trigger callback when new file is registered
        self._trigger_callback()
    
    def update_progress(self, tqdm_instance, n=1):
        """Update progress for a tqdm instance."""
        tqdm_id = str(id(tqdm_instance))
        if tqdm_id in self.progress_data:
            self.progress_data[tqdm_id]['current'] = getattr(tqdm_instance, 'n', 0)
            self.progress_data[tqdm_id]['total'] = getattr(tqdm_instance, 'total', 0) or 0
            # Trigger callback on every progress update
            self._trigger_callback()
    
    def calculate_speed(self, current_downloaded: int) -> float:
        """Calculate download speed in bytes per second."""
        current_time = time.time()
        
        # Check if we have a previous measurement to compare against
        if self.last_time is not None and self.last_downloaded is not None:
            time_diff = current_time - self.last_time
            
            # Only calculate if we have a meaningful time difference (avoid division by very small numbers)
            if time_diff > 0.5:  # At least 500ms between measurements
                bytes_diff = current_downloaded - self.last_downloaded
                
                # Only calculate speed if bytes actually changed
                if bytes_diff >= 0:  # Allow 0 for periods with no progress
                    speed = bytes_diff / time_diff
                    
                    # Add to speed history for smoothing
                    self.speed_history.append(speed)
                    if len(self.speed_history) > self.max_speed_history:
                        self.speed_history.pop(0)
        
        # Return the average of historical speeds if we have any
        # This ensures we show the last known speed even when skipping updates
        if self.speed_history:
            return sum(self.speed_history) / len(self.speed_history)
        
        return 0.0
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
    def format_speed(self, speed: float) -> str:
        """Format speed to human readable string."""
        if speed == 0:
            return "0 B/s"
        
        for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
            if speed < 1024.0:
                return f"{speed:.1f} {unit}"
            speed /= 1024.0
        return f"{speed:.1f} TB/s"
    
    def get_progress_data(self) -> Dict[str, Any]:
        """Get current progress data."""
        total_downloaded = 0
        active_file_count = 0
        total_file_sizes = 0
        
        for data in self.progress_data.values():
            if data['total'] > 0:
                total_downloaded += data['current']
                total_file_sizes += data['total']
                active_file_count += 1
        
        # Calculate speed
        speed = self.calculate_speed(total_downloaded)
        
        # Update tracking variables
        self.last_downloaded = total_downloaded
        self.last_time = time.time()
        
        # Determine total size - prioritize pre-fetched repo size, then aggregate file sizes
        if self.total_repo_size > 0:
            # Use pre-fetched repository info if available
            total_size = self.total_repo_size
        elif total_file_sizes > 0:
            # Use sum of individual file sizes if available
            total_size = total_file_sizes
        else:
            # Last resort - we don't know the total size yet
            total_size = 0
        
        file_count = self.repo_file_count if self.repo_file_count > 0 else active_file_count
        
        # Calculate percentage - handle unknown total size gracefully
        if total_size > 0:
            percentage = min((total_downloaded / total_size * 100), 100.0)
        else:
            percentage = 0
        
        # Calculate ETA
        eta_seconds = None
        if speed > 0 and total_size > total_downloaded:
            eta_seconds = (total_size - total_downloaded) / speed
        
        # Calculate elapsed time
        elapsed_seconds = None
        if self.download_start_time:
            elapsed_seconds = time.time() - self.download_start_time
        
        return {
            'status': self.download_status,
            'error_message': self.error_message,
            'progress': {
                'total_downloaded': total_downloaded,
                'total_size': total_size,
                'percentage': round(percentage, 2),
                'files_active': active_file_count,
                'files_total': file_count,
                'known_total': total_size > 0
            },
            'speed': {
                'bytes_per_second': speed,
                'formatted': self.format_speed(speed)
            },
            'formatting': {
                'downloaded': self.format_bytes(total_downloaded),
                'total_size': self.format_bytes(total_size)
            },
            'timing': {
                'elapsed_seconds': elapsed_seconds,
                'eta_seconds': eta_seconds,
                'start_time': self.download_start_time
            }
        }
    
    def _display_progress_bar(self, progress_data: Dict[str, Any]):
        """Display a custom unified progress bar."""
        if not self.show_progress:
            return
            
        # Clear previous line
        if self.last_display_length > 0:
            print('\r' + ' ' * self.last_display_length, end='\r')
        
        progress_info = progress_data.get('progress', {})
        speed_info = progress_data.get('speed', {})
        timing_info = progress_data.get('timing', {})
        formatting_info = progress_data.get('formatting', {})
        
        percentage = progress_info.get('percentage', 0)
        downloaded = formatting_info.get('downloaded', '0 B')
        total_size_raw = progress_info.get('total_size', 0)
        total_size = formatting_info.get('total_size', 'Unknown')
        speed = speed_info.get('formatted', '0 B/s')
        known_total = progress_info.get('known_total', False)
        
        # Create progress bar
        bar_width = 30
        if known_total and total_size_raw > 0:
            # Known total size - show actual progress
            filled_width = int(bar_width * min(percentage, 100) / 100)
            bar = '█' * filled_width + '░' * (bar_width - filled_width)
        else:
            # Unknown total size - show animated progress
            animation_pos = int(time.time() * 2) % bar_width
            bar = '░' * animation_pos + '█' + '░' * (bar_width - animation_pos - 1)
        
        # Format the progress line
        status = progress_data.get('status', 'unknown')
        if status == 'downloading':
            if known_total:
                progress_line = f"[{bar}] {percentage:.1f}% | {downloaded}/{total_size} | {speed}"
            else:
                progress_line = f"[{bar}] {downloaded} | {speed} | Calculating size..."
        elif status == 'completed':
            progress_line = f"[{bar}] 100.0% | {downloaded} | Complete!"
        elif status == 'error':
            progress_line = f"Error: {progress_data.get('error_message', 'Unknown error')}"
        else:
            progress_line = f"Starting download..."
        
        # Display and track length for next clear
        print(progress_line, end='', flush=True)
        self.last_display_length = len(progress_line)
    
    def _clear_progress_bar(self):
        """Clear the progress bar display."""
        if self.show_progress and self.last_display_length > 0:
            print('\r' + ' ' * self.last_display_length, end='\r')
            print()  # Move to next line
            self.last_display_length = 0
    
    def _trigger_callback(self):
        """Trigger the progress callback if one is set."""
        progress_data = self.get_progress_data()
        
        if self.progress_callback:
            try:
                self.progress_callback(progress_data)
            except Exception as e:
                print(f"Error in progress callback: {e}")
        
        # Show custom progress bar only if callback is enabled and show_progress is True
        if self.progress_callback and self.show_progress:
            self._display_progress_bar(progress_data)
    
    def start_tracking(self):
        """Start progress tracking (monkey patch tqdm)."""
        if self.is_tracking:
            return
        
        # Store original methods
        self.original_tqdm_update = tqdm.update
        self.original_tqdm_init = tqdm.__init__
        self.original_tqdm_display = tqdm.display
        self.original_tqdm_write = tqdm.write
        
        # Create references to self for the nested functions
        tracker = self
        
        def patched_init(self_tqdm, *args, **kwargs):
            # Suppress tqdm display by redirecting to devnull
            kwargs['file'] = open(os.devnull, 'w')
            kwargs['disable'] = False  # Keep enabled for tracking
            kwargs['leave'] = False  # Don't leave progress bar
            
            result = tracker.original_tqdm_init(self_tqdm, *args, **kwargs)
            tracker.register_tqdm(self_tqdm)
            return result
        
        def patched_update(self_tqdm, n=1):
            result = tracker.original_tqdm_update(self_tqdm, n)
            tracker.update_progress(self_tqdm, n)
            return result
        
        def patched_display(self_tqdm, msg=None, pos=None):
            # Override display to show nothing
            pass
        
        def patched_write(self_tqdm, s, file=None, end="\n", nolock=False):
            # Override write to prevent any output
            pass
        
        # Apply patches
        tqdm.__init__ = patched_init
        tqdm.update = patched_update
        tqdm.display = patched_display
        tqdm.write = patched_write
        
        self.is_tracking = True
        self.download_status = "downloading"
        self.download_start_time = time.time()
        
        # Trigger initial callback
        self._trigger_callback()
    
    def stop_tracking(self):
        """Stop progress tracking and restore original tqdm."""
        if not self.is_tracking:
            return
        
        # Restore original tqdm methods
        if self.original_tqdm_update:
            tqdm.update = self.original_tqdm_update
        if self.original_tqdm_init:
            tqdm.__init__ = self.original_tqdm_init
        if hasattr(self, 'original_tqdm_display') and self.original_tqdm_display:
            tqdm.display = self.original_tqdm_display
        if hasattr(self, 'original_tqdm_write') and self.original_tqdm_write:
            tqdm.write = self.original_tqdm_write
        
        # Clean up any open devnull file handles from tqdm instances
        for data in self.progress_data.values():
            if 'tqdm_obj' in data and hasattr(data['tqdm_obj'], 'fp'):
                try:
                    fp = data['tqdm_obj'].fp
                    if fp and fp != sys.stdout and fp != sys.stderr and not fp.closed:
                        fp.close()
                except:
                    pass
        
        self.is_tracking = False
        if self.download_status == "downloading":
            self.download_status = "completed"
        
        # Trigger final callback and clear progress bar
        self._trigger_callback()
        self._clear_progress_bar()
    
    def set_error(self, error_message: str):
        """Set error status and trigger callback."""
        self.download_status = "error"
        self.error_message = error_message
        self._trigger_callback()
        self._clear_progress_bar()