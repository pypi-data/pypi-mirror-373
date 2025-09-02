"""Synchronization functionality for mem8."""

import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import filecmp
from datetime import datetime

from .config import Config
from .utils import ensure_directory_exists


class SyncManager:
    """Manages synchronization between local and shared memory."""
    
    def __init__(self, config: Config):
        """Initialize sync manager."""
        self.config = config
        self.sync_metadata_file = config.data_dir / "sync_metadata.json"
    
    def sync_memory(
        self, 
        direction: str = 'both',
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Synchronize memory between local and shared locations."""
        try:
            if not self.config.shared_dir or not self.config.shared_dir.exists():
                return {
                    'success': False,
                    'error': 'Shared directory not configured or not accessible'
                }
            
            local_thoughts = self.config.thoughts_dir
            shared_thoughts = self.config.shared_dir / "thoughts"
            
            if not local_thoughts.exists():
                ensure_directory_exists(local_thoughts)
            
            if not shared_thoughts.exists():
                ensure_directory_exists(shared_thoughts)
            
            summary = {
                'pulled': 0,
                'pushed': 0,
                'conflicts': 0,
                'errors': 0,
            }
            
            # Perform sync based on direction
            if direction in ['pull', 'both']:
                pull_result = self._sync_direction(
                    shared_thoughts, local_thoughts, 'pull', dry_run
                )
                summary['pulled'] = pull_result['count']
                summary['conflicts'] += pull_result['conflicts']
                summary['errors'] += pull_result['errors']
            
            if direction in ['push', 'both']:
                push_result = self._sync_direction(
                    local_thoughts, shared_thoughts, 'push', dry_run
                )
                summary['pushed'] = push_result['count']
                summary['conflicts'] += push_result['conflicts']
                summary['errors'] += push_result['errors']
            
            # Update sync metadata
            if not dry_run:
                self._update_sync_metadata()
            
            return {
                'success': True,
                'summary': summary,
                'dry_run': dry_run,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Sync failed: {e}"
            }
    
    def _sync_direction(
        self, 
        source_dir: Path, 
        target_dir: Path,
        direction: str,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Sync files in one direction."""
        count = 0
        conflicts = 0
        errors = 0
        
        try:
            # Get exclude patterns
            exclude_patterns = self.config.get('sync.exclude_patterns', [])
            
            # Walk through source directory
            for source_file in source_dir.rglob("*"):
                if source_file.is_file():
                    # Check if file should be excluded
                    relative_path = source_file.relative_to(source_dir)
                    if self._should_exclude_file(relative_path, exclude_patterns):
                        continue
                    
                    target_file = target_dir / relative_path
                    
                    try:
                        result = self._sync_file(
                            source_file, target_file, direction, dry_run
                        )
                        
                        if result['synced']:
                            count += 1
                        if result['conflict']:
                            conflicts += 1
                            
                    except Exception as e:
                        errors += 1
                        print(f"Error syncing {source_file}: {e}")
            
            return {
                'count': count,
                'conflicts': conflicts, 
                'errors': errors,
            }
            
        except Exception as e:
            return {
                'count': count,
                'conflicts': conflicts,
                'errors': errors + 1,
            }
    
    def _sync_file(
        self,
        source_file: Path,
        target_file: Path,
        direction: str,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Sync a single file."""
        synced = False
        conflict = False
        
        # Ensure target directory exists
        if not dry_run:
            ensure_directory_exists(target_file.parent)
        
        if not target_file.exists():
            # Simple copy - no conflict
            if not dry_run:
                shutil.copy2(source_file, target_file)
            synced = True
        else:
            # File exists - check for conflicts
            if not filecmp.cmp(source_file, target_file, shallow=False):
                # Files are different - handle conflict
                conflict_resolution = self.config.get('sync.conflict_resolution', 'prompt')
                
                if conflict_resolution == 'newest':
                    source_mtime = source_file.stat().st_mtime
                    target_mtime = target_file.stat().st_mtime
                    
                    if source_mtime > target_mtime:
                        if not dry_run:
                            self._backup_file(target_file)
                            shutil.copy2(source_file, target_file)
                        synced = True
                    else:
                        # Target is newer, don't sync
                        pass
                        
                elif conflict_resolution == 'shared':
                    if direction == 'pull':  # Prefer shared version
                        if not dry_run:
                            self._backup_file(target_file)
                            shutil.copy2(source_file, target_file)
                        synced = True
                        
                elif conflict_resolution == 'local':
                    if direction == 'push':  # Prefer local version
                        if not dry_run:
                            self._backup_file(target_file)
                            shutil.copy2(source_file, target_file)
                        synced = True
                        
                else:  # 'prompt' or unknown
                    # For CLI, we'll mark as conflict and let user handle
                    conflict = True
        
        return {
            'synced': synced,
            'conflict': conflict,
        }
    
    def _should_exclude_file(self, relative_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded from sync."""
        path_str = str(relative_path)
        
        for pattern in exclude_patterns:
            if pattern in path_str or relative_path.name == pattern:
                return True
            
            # Handle glob patterns (simplified)
            if pattern.startswith('*.'):
                extension = pattern[2:]
                if path_str.endswith(extension):
                    return True
        
        return False
    
    def _backup_file(self, file_path: Path) -> None:
        """Create a backup of the file before overwriting."""
        if not self.config.get('sync.backup_before_sync', True):
            return
        
        backup_dir = self.config.data_dir / "backups"
        ensure_directory_exists(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
        except Exception:
            pass  # Backup failed, but continue with sync
    
    def _update_sync_metadata(self) -> None:
        """Update sync metadata file."""
        metadata = {
            'last_sync': datetime.now().isoformat(),
            'sync_count': self._get_sync_count() + 1,
        }
        
        try:
            import json
            with open(self.sync_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            pass  # Metadata update failed, but sync was successful
    
    def _get_sync_count(self) -> int:
        """Get the current sync count."""
        try:
            import json
            if self.sync_metadata_file.exists():
                with open(self.sync_metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    return metadata.get('sync_count', 0)
        except Exception:
            pass
        
        return 0
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status."""
        try:
            import json
            if self.sync_metadata_file.exists():
                with open(self.sync_metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                last_sync = metadata.get('last_sync')
                if last_sync:
                    # Convert ISO format to readable format
                    sync_time = datetime.fromisoformat(last_sync)
                    last_sync = sync_time.strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    'last_sync': last_sync,
                    'sync_count': metadata.get('sync_count', 0),
                    'has_synced': True,
                }
        except Exception:
            pass
        
        return {
            'last_sync': None,
            'sync_count': 0,
            'has_synced': False,
        }
    
    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect sync conflicts that need manual resolution."""
        conflicts = []
        
        if not self.config.shared_dir or not self.config.shared_dir.exists():
            return conflicts
        
        local_thoughts = self.config.thoughts_dir
        shared_thoughts = self.config.shared_dir / "thoughts"
        
        if not local_thoughts.exists() or not shared_thoughts.exists():
            return conflicts
        
        # Check for conflicting files
        exclude_patterns = self.config.get('sync.exclude_patterns', [])
        
        for local_file in local_thoughts.rglob("*.md"):
            if local_file.is_file():
                relative_path = local_file.relative_to(local_thoughts)
                
                if self._should_exclude_file(relative_path, exclude_patterns):
                    continue
                
                shared_file = shared_thoughts / relative_path
                
                if shared_file.exists():
                    if not filecmp.cmp(local_file, shared_file, shallow=False):
                        # Files are different
                        local_mtime = local_file.stat().st_mtime
                        shared_mtime = shared_file.stat().st_mtime
                        
                        conflicts.append({
                            'file': str(relative_path),
                            'local_path': local_file,
                            'shared_path': shared_file,
                            'local_modified': datetime.fromtimestamp(local_mtime).isoformat(),
                            'shared_modified': datetime.fromtimestamp(shared_mtime).isoformat(),
                            'newer': 'local' if local_mtime > shared_mtime else 'shared',
                        })
        
        return conflicts
    
    def resolve_conflict(
        self, 
        conflict: Dict[str, Any], 
        resolution: str
    ) -> bool:
        """Resolve a specific conflict."""
        try:
            local_path = Path(conflict['local_path'])
            shared_path = Path(conflict['shared_path'])
            
            if resolution == 'use_local':
                self._backup_file(shared_path)
                shutil.copy2(local_path, shared_path)
            elif resolution == 'use_shared':
                self._backup_file(local_path)
                shutil.copy2(shared_path, local_path)
            elif resolution == 'use_newer':
                if conflict['newer'] == 'local':
                    self._backup_file(shared_path)
                    shutil.copy2(local_path, shared_path)
                else:
                    self._backup_file(local_path)
                    shutil.copy2(shared_path, local_path)
            else:
                return False
            
            return True
            
        except Exception:
            return False