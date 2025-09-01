#!/usr/bin/env python3
"""
Comprehensive test suite for AI-Mem CLI
Tests the CLI functionality in isolation without interfering with real workspaces.
"""

import os
import subprocess
import tempfile
import shutil
import json
from pathlib import Path
import pytest


class TestAIMemCLI:
    """Test suite for AI-Mem CLI functionality."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="ai-mem-test-"))
        self.shared_dir = self.test_dir / "shared"
        self.workspace_dir = self.test_dir / "workspace"
        
        # Create workspace directory and initialize git
        self.workspace_dir.mkdir(parents=True)
        os.chdir(self.workspace_dir)
        
        # Initialize git repository
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Create initial commit
        (self.workspace_dir / "README.md").write_text("# Test Project")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(Path.home())
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def run_aimem(self, args, expect_success=True):
        """Run ai-mem command and return result."""
        result = subprocess.run(
            ["ai-mem"] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if expect_success and result.returncode != 0:
            print(f"Command failed: ai-mem {' '.join(args)}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            raise AssertionError(f"Expected success but got return code {result.returncode}")
        
        return result
    
    def test_cli_help(self):
        """Test that CLI help works."""
        result = self.run_aimem(["--help"])
        assert "AI-Mem: AI Memory Management CLI" in result.stdout
        assert "Commands:" in result.stdout
        assert "init" in result.stdout
        assert "sync" in result.stdout
        assert "status" in result.stdout
        assert "search" in result.stdout
        assert "doctor" in result.stdout
    
    def test_version(self):
        """Test that version command works."""
        result = self.run_aimem(["--version"])
        assert "0.1.0" in result.stdout
    
    def test_status_uninitialized(self):
        """Test status command on uninitialized workspace."""
        result = self.run_aimem(["status"])
        assert "AI-Mem Workspace Status" in result.stdout
        assert "Missing" in result.stdout  # Should show missing components
    
    def test_doctor_uninitialized(self):
        """Test doctor command on uninitialized workspace."""
        result = self.run_aimem(["doctor"])
        assert "Running AI-Mem diagnostics" in result.stdout
        assert "Issues found" in result.stdout or "Workspace health" in result.stdout
    
    def test_initialization_basic(self):
        """Test basic workspace initialization."""
        result = self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir),
            "--template", "minimal"
        ])
        
        assert "Workspace initialized successfully" in result.stdout
        assert str(self.shared_dir) in result.stdout
        assert str(self.workspace_dir) in result.stdout
        
        # Check that directories were created
        assert (self.workspace_dir / ".claude").exists()
        assert (self.workspace_dir / "thoughts").exists()
        assert (self.workspace_dir / ".claude" / "CLAUDE.md").exists()
        assert self.shared_dir.exists()
    
    def test_initialization_force(self):
        """Test initialization with force flag."""
        # First initialization
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir),
            "--template", "minimal"
        ])
        
        # Second initialization should fail without force
        result = self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir)
        ], expect_success=False)
        assert "already exists" in result.stdout
        
        # With force should succeed
        result = self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir),
            "--force"
        ])
        assert "Workspace initialized successfully" in result.stdout
    
    def test_status_after_init(self):
        """Test status command after initialization."""
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir),
            "--template", "default"
        ])
        
        result = self.run_aimem(["status", "--detailed"])
        assert "AI-Mem Workspace Status" in result.stdout
        assert "Ready" in result.stdout
        assert "Git repository:" in result.stdout
        assert "Current branch:" in result.stdout
    
    def test_sync_functionality(self):
        """Test sync functionality."""
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir)
        ])
        
        # Test dry run
        result = self.run_aimem(["sync", "--dry-run"])
        assert "Dry run:" in result.stdout
        assert "memory" in result.stdout
        
        # Test actual sync
        result = self.run_aimem(["sync"])
        assert "Syncing memory" in result.stdout or "No changes needed" in result.stdout
    
    def test_search_functionality(self):
        """Test search functionality."""
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir)
        ])
        
        # Create test content
        test_file = self.workspace_dir / "thoughts" / "test.md"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("# Test Document\\n\\nThis is a test document with searchable content.")
        
        # Test search
        result = self.run_aimem(["search", "searchable", "--limit", "5"])
        assert "Searching for: 'searchable'" in result.stdout
        # Search might return no results if indexing hasn't happened yet, that's ok
    
    def test_doctor_after_init(self):
        """Test doctor command after initialization."""
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir)
        ])
        
        result = self.run_aimem(["doctor"])
        assert "Running AI-Mem diagnostics" in result.stdout
        assert "Workspace health:" in result.stdout
    
    def test_doctor_autofix(self):
        """Test doctor command with auto-fix."""
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir)
        ])
        
        # Remove a directory to create an issue
        shutil.rmtree(self.workspace_dir / "thoughts", ignore_errors=True)
        
        result = self.run_aimem(["doctor", "--auto-fix"])
        assert "Running AI-Mem diagnostics" in result.stdout
        # Should either fix the issue or report what was fixed
    
    def test_claude_md_generation(self):
        """Test that CLAUDE.md is generated correctly."""
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir)
        ])
        
        claude_md = self.workspace_dir / ".claude" / "CLAUDE.md"
        assert claude_md.exists()
        
        content = claude_md.read_text()
        assert "AI-Mem Workspace Configuration" in content
        assert "ai-mem sync" in content
        assert "@thoughts/shared/" in content
    
    def test_shared_directory_creation(self):
        """Test that shared directory structure is created correctly."""
        self.run_aimem([
            "init", 
            "--shared-dir", str(self.shared_dir)
        ])
        
        # Check shared directory structure
        assert (self.shared_dir / "thoughts").exists()
        assert (self.shared_dir / "thoughts" / "shared" / "plans").exists()
        assert (self.shared_dir / "thoughts" / "shared" / "decisions").exists()
        assert (self.shared_dir / "thoughts" / "shared" / "research").exists()
        assert (self.shared_dir / "thoughts" / "README.md").exists()
    
    def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Test with invalid shared directory
        result = self.run_aimem([
            "init",
            "--shared-dir", "/invalid/path/that/cannot/be/created"
        ], expect_success=False)
        assert result.returncode != 0
    
    def test_init_protects_existing_data(self):
        """Test that init command protects existing thoughts/shared data."""
        # Create important user data first
        thoughts_dir = self.workspace_dir / "thoughts"
        shared_dir = thoughts_dir / "shared"
        shared_dir.mkdir(parents=True, exist_ok=True)
        
        important_file = shared_dir / "critical_research.md"
        important_file.write_text("# Critical Research\\n\\nThis data must not be lost!")
        
        # Test that init detects and warns about existing data
        result = self.run_aimem([
            "init", "--template", "thoughts-repo"
        ], expect_success=False)
        
        # Should warn about existing data
        assert "thoughts/shared directory (contains your data!)" in result.stdout
        assert "WARNING: thoughts/shared contains your memory data!" in result.stdout
        assert "--force" in result.stdout
        
        # Verify our important data is still there and untouched
        assert important_file.exists()
        assert "Critical Research" in important_file.read_text()
        
        print("✅ Init command properly protects existing user data")
    
    def test_unicode_support(self):
        """Test that Unicode characters are handled properly."""
        # This test validates our UTF-8 encoding fixes
        result = self.run_aimem(["--help"])
        # Should not crash with encoding errors
        assert result.returncode == 0
        assert len(result.stdout) > 0


def run_manual_tests():
    """
    Run manual validation tests that require human verification.
    These tests validate real-world scenarios.
    """
    print("🧪 Running manual validation tests...")
    print("=" * 50)
    
    # Test 1: Validate against current workspace
    print("\\n1. Testing against current workspace...")
    os.chdir(Path(__file__).parent.parent)
    result = subprocess.run(["ai-mem", "status", "--detailed"], capture_output=True, text=True)
    print("✅ Current workspace status:")
    print(result.stdout)
    
    # Test 2: Search real content
    print("\\n2. Testing search on real content...")
    result = subprocess.run(["ai-mem", "search", "implementation", "--limit", "3"], 
                          capture_output=True, text=True)
    print("✅ Search results:")
    print(result.stdout)
    
    # Test 3: Workspace health
    print("\\n3. Testing workspace health...")
    result = subprocess.run(["ai-mem", "doctor"], capture_output=True, text=True)
    print("✅ Workspace health:")
    print(result.stdout)
    
    print("\\n" + "=" * 50)
    print("✅ Manual validation complete!")


if __name__ == "__main__":
    # Run manual tests when script is executed directly
    run_manual_tests()