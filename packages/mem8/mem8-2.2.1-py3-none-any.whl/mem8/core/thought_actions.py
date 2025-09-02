"""Safe action execution engine for thought lifecycle operations."""

import shutil
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional
from .config import Config
from .thought_entity import ThoughtEntity


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


class ThoughtActionEngine:
    """Safely executes actions on thought entities with backup and audit."""
    
    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = config.data_dir / "thought_backups"
        self.audit_log = config.data_dir / "thought_audit.jsonl"
        self.ensure_backup_structure()
        
    def ensure_backup_structure(self):
        """Ensure backup and audit structure exists."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def delete_thoughts(self, entities: List[ThoughtEntity], dry_run: bool = False) -> Dict[str, Any]:
        """Safely delete thought entities with backup."""
        if dry_run:
            return self._preview_delete(entities)
            
        results = {
            'success': [],
            'errors': [],
            'backups': [],
        }
        
        for entity in entities:
            try:
                # Create backup before deletion
                backup_path = self._create_backup(entity, "delete")
                
                # Perform deletion
                entity.path.unlink()
                
                # Log the action
                self._log_action("delete", entity, backup_path=str(backup_path))
                
                results['success'].append(str(entity.path))
                results['backups'].append(str(backup_path))
                
            except Exception as e:
                results['errors'].append({
                    'path': str(entity.path),
                    'error': str(e)
                })
                
        return results
        
    def archive_thoughts(self, entities: List[ThoughtEntity], target_dir: Optional[Path] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Archive thought entities by moving to archive directory."""
        if dry_run:
            return self._preview_archive(entities, target_dir)
            
        # Determine archive location
        if not target_dir:
            target_dir = self.config.thoughts_dir / "archive"
            
        target_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'success': [],
            'errors': [],
            'archived_to': [],
        }
        
        for entity in entities:
            try:
                # Determine target path preserving directory structure
                try:
                    rel_path = entity.path.relative_to(self.config.thoughts_dir)
                except ValueError:
                    # If path is not relative to thoughts_dir, use just the filename
                    rel_path = entity.path.name
                
                target_path = target_dir / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(entity.path), str(target_path))
                
                # Log the action
                self._log_action("archive", entity, target_path=str(target_path))
                
                results['success'].append(str(entity.path))
                results['archived_to'].append(str(target_path))
                
            except Exception as e:
                results['errors'].append({
                    'path': str(entity.path),
                    'error': str(e)
                })
                
        return results
        
    def promote_thoughts(self, entities: List[ThoughtEntity], from_scope: str, to_scope: str, dry_run: bool = False) -> Dict[str, Any]:
        """Promote thoughts between scopes (personal <-> shared <-> team)."""
        if dry_run:
            return self._preview_promote(entities, from_scope, to_scope)
            
        results = {
            'success': [],
            'errors': [],
            'promoted_to': [],
        }
        
        for entity in entities:
            try:
                if entity.scope != from_scope:
                    results['errors'].append({
                        'path': str(entity.path),
                        'error': f"Entity scope is '{entity.scope}', not '{from_scope}'"
                    })
                    continue
                    
                # Determine target path based on scope
                target_path = self._calculate_promotion_path(entity, to_scope)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(entity.path), str(target_path))
                
                # Log the action
                self._log_action("promote", entity, 
                                target_path=str(target_path),
                                from_scope=from_scope, 
                                to_scope=to_scope)
                
                results['success'].append(str(entity.path))
                results['promoted_to'].append(str(target_path))
                
            except Exception as e:
                results['errors'].append({
                    'path': str(entity.path),
                    'error': str(e)
                })
                
        return results
    
    def _create_backup(self, entity: ThoughtEntity, action: str) -> Path:
        """Create backup of entity before destructive action."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{entity.path.stem}_{action}_{timestamp}.md"
        backup_path = self.backup_dir / backup_name
        
        # Copy file with metadata
        shutil.copy2(entity.path, backup_path)
        
        # Create backup metadata
        backup_meta = backup_path.with_suffix('.meta.json')
        metadata = {
            'original_path': str(entity.path),
            'backup_timestamp': timestamp,
            'action': action,
            'entity_metadata': entity.metadata,
            'entity_type': entity.type,
            'entity_scope': entity.scope,
        }
        
        with open(backup_meta, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, cls=DateTimeEncoder)
            
        return backup_path
    
    def _log_action(self, action: str, entity: ThoughtEntity, **kwargs):
        """Log action to audit trail."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'entity_path': str(entity.path),
            'entity_type': entity.type,
            'entity_scope': entity.scope,
            'metadata': entity.metadata,
            **kwargs
        }
        
        with open(self.audit_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, cls=DateTimeEncoder) + '\n')
    
    def _preview_delete(self, entities: List[ThoughtEntity]) -> Dict[str, Any]:
        """Preview delete operation."""
        return {
            'operation': 'delete',
            'entities': [str(e.path) for e in entities],
            'will_backup': True,
            'backup_location': str(self.backup_dir),
            'reversible': True
        }
    
    def _preview_archive(self, entities: List[ThoughtEntity], target_dir: Optional[Path]) -> Dict[str, Any]:
        """Preview archive operation."""
        if not target_dir:
            target_dir = self.config.thoughts_dir / "archive"
        
        preview_paths = []
        for entity in entities:
            try:
                rel_path = entity.path.relative_to(self.config.thoughts_dir)
            except ValueError:
                rel_path = entity.path.name
            target_path = target_dir / rel_path
            preview_paths.append({
                'from': str(entity.path),
                'to': str(target_path)
            })
        
        return {
            'operation': 'archive',
            'moves': preview_paths,
            'archive_directory': str(target_dir),
            'reversible': True
        }
    
    def _preview_promote(self, entities: List[ThoughtEntity], from_scope: str, to_scope: str) -> Dict[str, Any]:
        """Preview promote operation."""
        preview_paths = []
        for entity in entities:
            target_path = self._calculate_promotion_path(entity, to_scope)
            preview_paths.append({
                'from': str(entity.path),
                'to': str(target_path),
                'scope_change': f"{from_scope} -> {to_scope}"
            })
        
        return {
            'operation': 'promote',
            'moves': preview_paths,
            'from_scope': from_scope,
            'to_scope': to_scope,
            'reversible': True
        }
    
    def _calculate_promotion_path(self, entity: ThoughtEntity, to_scope: str) -> Path:
        """Calculate target path for scope promotion."""
        thoughts_dir = self.config.thoughts_dir
        
        if to_scope == 'shared':
            # Move to shared directory
            target_base = thoughts_dir / "shared"
            # Preserve type-based directory structure
            if entity.type in ['plan', 'research', 'ticket', 'decision']:
                target_dir = target_base / f"{entity.type}s"
            else:
                target_dir = target_base
        elif to_scope == 'personal':
            # Move to user's personal directory
            import os
            username = os.environ.get('USERNAME', os.environ.get('USER', 'user'))
            target_dir = thoughts_dir / username
        else:
            # Default fallback
            target_dir = thoughts_dir / to_scope
        
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / entity.path.name
    
    def restore_from_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Restore a thought from backup."""
        try:
            # Load backup metadata
            meta_path = backup_path.with_suffix('.meta.json')
            if not meta_path.exists():
                return {
                    'success': False,
                    'error': f"Backup metadata not found: {meta_path}"
                }
            
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            original_path = Path(metadata['original_path'])
            
            # Check if target location exists
            if original_path.exists():
                return {
                    'success': False,
                    'error': f"Target path already exists: {original_path}"
                }
            
            # Ensure target directory exists
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore the file
            shutil.copy2(backup_path, original_path)
            
            # Log restoration
            self._log_action("restore", None, 
                            backup_path=str(backup_path),
                            restored_to=str(original_path))
            
            return {
                'success': True,
                'restored_to': str(original_path),
                'backup_metadata': metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Restore failed: {e}"
            }
    
    def list_backups(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.md"):
            meta_file = backup_file.with_suffix('.meta.json')
            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    backups.append({
                        'backup_path': str(backup_file),
                        'original_path': metadata['original_path'],
                        'timestamp': metadata['backup_timestamp'],
                        'action': metadata['action'],
                        'entity_type': metadata.get('entity_type', 'unknown')
                    })
                except Exception:
                    continue
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return backups[:limit]