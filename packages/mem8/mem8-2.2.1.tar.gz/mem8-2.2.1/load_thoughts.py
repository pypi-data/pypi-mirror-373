#!/usr/bin/env python3
"""Load existing thought files into the database."""

import os
import hashlib
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from mem8_api.models.thought import Thought
from mem8_api.database import get_database
from sqlalchemy.orm import Session


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content."""
    return hashlib.sha256(content.encode()).hexdigest()


def load_thoughts_from_directory(thoughts_dir: Path, db: Session):
    """Load all markdown files from thoughts directory into database."""
    
    for md_file in thoughts_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
            
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Extract title from first line or filename
            lines = content.split('\n')
            title = None
            for line in lines:
                if line.startswith('#'):
                    title = line.lstrip('#').strip()
                    break
            
            if not title:
                title = md_file.stem.replace('-', ' ').title()
            
            # Calculate relative path from thoughts directory
            rel_path = md_file.relative_to(thoughts_dir.parent)
            
            # Calculate content hash
            content_hash = calculate_content_hash(content)
            
            # Check if thought already exists
            existing = db.query(Thought).filter(Thought.content_hash == content_hash).first()
            if existing:
                print(f"Skipping {rel_path} (already exists)")
                continue
            
            # Create new thought
            thought = Thought(
                title=title,
                content=content,
                path=str(rel_path),
                content_hash=content_hash,
                word_count=len(content.split()),
                tags=["imported", "file-system"],
                is_published=True
            )
            
            db.add(thought)
            db.commit()
            print(f"Added: {title} ({rel_path})")
            
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            continue


def main():
    """Main function."""
    thoughts_dir = Path("thoughts")
    
    if not thoughts_dir.exists():
        print("No thoughts directory found")
        return
    
    # Get database session
    db = next(get_database())
    
    try:
        load_thoughts_from_directory(thoughts_dir, db)
        print("✅ Thoughts loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading thoughts: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()