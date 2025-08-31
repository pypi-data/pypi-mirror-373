"""Checkpoint management for resumable document processing."""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Any
import hashlib


class CheckpointManager:
    """Manages checkpoints for resumable PDF processing."""
    
    def __init__(self, output_dir: Path, pdf_path: str, md5_checksum: str):
        """
        Initialize checkpoint manager.
        
        Args:
            output_dir: Base output directory
            pdf_path: Path to the PDF file
            md5_checksum: MD5 checksum of the PDF
        """
        self.output_dir = Path(output_dir)
        self.pdf_path = pdf_path
        self.md5_checksum = md5_checksum
        self.checkpoint_dir = self.output_dir / md5_checksum / ".checkpoint"
        self.checkpoint_file = self.checkpoint_dir / "processing_state.json"
        self.pages_dir = self.checkpoint_dir / "completed_pages"
        
        # Create checkpoint directories
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, state: Dict[str, Any]) -> None:
        """
        Save current processing state to checkpoint.
        
        Args:
            state: Dictionary containing processing state
        """
        checkpoint_data = {
            "pdf_path": self.pdf_path,
            "md5_checksum": self.md5_checksum,
            "timestamp": datetime.now().isoformat(),
            "state": state
        }
        
        # Write checkpoint atomically
        temp_file = self.checkpoint_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        # Atomic rename
        temp_file.replace(self.checkpoint_file)
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint if it exists and is valid.
        
        Returns:
            Checkpoint data or None if not found/invalid
        """
        if not self.checkpoint_file.exists():
            return None
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # Validate checkpoint
            if checkpoint_data.get('md5_checksum') != self.md5_checksum:
                print(f"Warning: Checkpoint MD5 mismatch. Starting fresh.")
                return None
            
            return checkpoint_data.get('state')
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load checkpoint: {e}")
            return None
    
    def mark_page_complete(self, page_number: int, page_data: Dict[str, Any]) -> None:
        """
        Mark a page as successfully processed.
        
        Args:
            page_number: Page number that was completed
            page_data: Data about the processed page
        """
        page_file = self.pages_dir / f"page_{page_number:03d}.json"
        
        page_info = {
            "page_number": page_number,
            "completed_at": datetime.now().isoformat(),
            "data": page_data
        }
        
        with open(page_file, 'w', encoding='utf-8') as f:
            json.dump(page_info, f, indent=2)
    
    def get_completed_pages(self) -> List[int]:
        """
        Get list of successfully completed page numbers.
        
        Returns:
            List of completed page numbers
        """
        completed = []
        for page_file in self.pages_dir.glob("page_*.json"):
            try:
                page_num = int(page_file.stem.split('_')[1])
                completed.append(page_num)
            except (ValueError, IndexError):
                continue
        
        return sorted(completed)
    
    def is_page_complete(self, page_number: int) -> bool:
        """
        Check if a specific page has been completed.
        
        Args:
            page_number: Page number to check
            
        Returns:
            True if page is complete, False otherwise
        """
        page_file = self.pages_dir / f"page_{page_number:03d}.json"
        return page_file.exists()
    
    def get_page_data(self, page_number: int) -> Optional[Dict[str, Any]]:
        """
        Get saved data for a completed page.
        
        Args:
            page_number: Page number to retrieve
            
        Returns:
            Page data or None if not found
        """
        page_file = self.pages_dir / f"page_{page_number:03d}.json"
        if not page_file.exists():
            return None
        
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                page_info = json.load(f)
                return page_info.get('data')
        except (json.JSONDecodeError, IOError):
            return None
    
    def clear_checkpoint(self) -> None:
        """Remove all checkpoint data after successful completion."""
        import shutil
        if self.checkpoint_dir.exists():
            shutil.rmtree(self.checkpoint_dir)
    
    def get_resume_info(self) -> Dict[str, Any]:
        """
        Get information about what can be resumed.
        
        Returns:
            Dictionary with resume information
        """
        state = self.load_checkpoint()
        completed_pages = self.get_completed_pages()
        
        return {
            "has_checkpoint": state is not None,
            "completed_pages": completed_pages,
            "total_completed": len(completed_pages),
            "last_page": max(completed_pages) if completed_pages else 0,
            "state": state
        }


class ProcessingState:
    """Tracks the current state of document processing."""
    
    def __init__(self, checkpoint_manager: CheckpointManager):
        """
        Initialize processing state.
        
        Args:
            checkpoint_manager: Checkpoint manager instance
        """
        self.checkpoint_manager = checkpoint_manager
        self.start_page = 1
        self.end_page = 1
        self.current_page = 1
        self.total_pages = 0
        self.completed_pages = []
        self.failed_pages = []
        self.network_diagrams_found = 0
        self.regular_pages = 0
        self.processing_start_time = None
        self.models = {}
        self.settings = {}
    
    def initialize(self, start: int, end: int, total: int, models: Dict, settings: Dict) -> None:
        """
        Initialize processing state.
        
        Args:
            start: Start page number
            end: End page number
            total: Total pages in document
            models: Model configuration
            settings: Processing settings
        """
        self.start_page = start
        self.end_page = end
        self.total_pages = total
        self.models = models
        self.settings = settings
        self.processing_start_time = datetime.now().isoformat()
        
        # Load completed pages from checkpoint
        self.completed_pages = self.checkpoint_manager.get_completed_pages()
    
    def should_process_page(self, page_number: int) -> bool:
        """
        Check if a page should be processed.
        
        Args:
            page_number: Page number to check
            
        Returns:
            True if page should be processed, False if already complete
        """
        return not self.checkpoint_manager.is_page_complete(page_number)
    
    def mark_page_complete(self, page_number: int, is_network_diagram: bool = False,
                          has_errors: bool = False, processing_time: float = 0,
                          has_tables: bool = False) -> None:
        """
        Mark a page as complete and save checkpoint.
        
        Args:
            page_number: Completed page number
            is_network_diagram: Whether page contains network diagram
            has_errors: Whether page had errors
            processing_time: Time taken to process page
            has_tables: Whether page contains tables
        """
        self.current_page = page_number
        
        if not has_errors:
            self.completed_pages.append(page_number)
            if is_network_diagram:
                self.network_diagrams_found += 1
            else:
                self.regular_pages += 1
            
            if has_tables:
                self.tables_found = getattr(self, 'tables_found', 0) + 1
        else:
            self.failed_pages.append(page_number)
        
        # Save page data
        page_data = {
            "is_network_diagram": is_network_diagram,
            "has_errors": has_errors,
            "processing_time": processing_time,
            "has_tables": has_tables
        }
        self.checkpoint_manager.mark_page_complete(page_number, page_data)
        
        # Update main checkpoint
        self.save_checkpoint()
    
    def save_checkpoint(self) -> None:
        """Save current state to checkpoint."""
        state = {
            "current_page": self.current_page,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "total_pages": self.total_pages,
            "completed_pages": self.completed_pages,
            "failed_pages": self.failed_pages,
            "network_diagrams_found": self.network_diagrams_found,
            "regular_pages": self.regular_pages,
            "tables_found": getattr(self, 'tables_found', 0),
            "processing_start_time": self.processing_start_time,
            "models": self.models,
            "settings": self.settings
        }
        self.checkpoint_manager.save_checkpoint(state)
    
    def load_from_checkpoint(self) -> bool:
        """
        Load state from checkpoint.
        
        Returns:
            True if checkpoint loaded successfully, False otherwise
        """
        state = self.checkpoint_manager.load_checkpoint()
        if not state:
            return False
        
        self.current_page = state.get("current_page", 1)
        self.start_page = state.get("start_page", 1)
        self.end_page = state.get("end_page", 1)
        self.total_pages = state.get("total_pages", 0)
        self.completed_pages = state.get("completed_pages", [])
        self.failed_pages = state.get("failed_pages", [])
        self.network_diagrams_found = state.get("network_diagrams_found", 0)
        self.regular_pages = state.get("regular_pages", 0)
        self.tables_found = state.get("tables_found", 0)
        self.processing_start_time = state.get("processing_start_time")
        self.models = state.get("models", {})
        self.settings = state.get("settings", {})
        
        return True
    
    def get_resume_summary(self) -> str:
        """
        Get a summary of what will be resumed.
        
        Returns:
            Human-readable summary string
        """
        completed = len(self.completed_pages)
        remaining = self.end_page - self.start_page + 1 - completed
        
        summary = f"""
╔════════════════════════════════════════════════════════════╗
║                  RESUME CHECKPOINT FOUND                   ║
╠════════════════════════════════════════════════════════════╣
║ Previous Processing:                                        ║
║   • Pages completed: {completed}/{self.end_page - self.start_page + 1}
║   • Network diagrams found: {self.network_diagrams_found}
║   • Tables found: {getattr(self, 'tables_found', 0)}
║   • Regular pages: {self.regular_pages}
║   • Failed pages: {len(self.failed_pages)}
║                                                            ║
║ Resume Information:                                        ║
║   • Will skip {completed} already processed pages
║   • Will process {remaining} remaining pages
║   • Starting from page {max(self.completed_pages) + 1 if self.completed_pages else self.start_page}
╚════════════════════════════════════════════════════════════╝
"""
        return summary