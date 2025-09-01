"""Logging utilities for NetIntel-OCR processing with per-file log storage."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import traceback


class ProcessingLogger:
    """Logger that writes to both console and file for each processed document."""
    
    def __init__(self, output_dir: str, filename: str, verbose: bool = True):
        """
        Initialize the processing logger.
        
        Args:
            output_dir: Base output directory for the document
            filename: Name of the file being processed
            verbose: Whether to show detailed console output
        """
        self.output_dir = Path(output_dir)
        self.filename = filename
        self.verbose = verbose
        
        # Create logs directory
        self.log_dir = self.output_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file path
        log_filename = f"{Path(filename).stem}.log"
        self.log_file = self.log_dir / log_filename
        
        # Initialize logger
        self.logger = self._setup_logger()
        
        # Processing metrics
        self.start_time = datetime.now()
        self.page_times = []
        self.errors = []
        self.warnings = []
        self.processing_steps = []
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers."""
        # Create unique logger name based on file
        logger_name = f"netintel_ocr.{self.filename}_{id(self)}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        logger.handlers = []
        
        # File handler - detailed logging
        file_handler = logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler - based on verbosity
        if self.verbose:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_start(self):
        """Log the start of processing."""
        self.logger.info("=" * 70)
        self.logger.info(f"Starting processing: {self.filename}")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 70)
    
    def log_page_start(self, page_num: int, total_pages: int):
        """Log the start of page processing."""
        self.current_page_start = datetime.now()
        self.logger.info(f"\n--- Processing Page {page_num}/{total_pages} ---")
        self.processing_steps = []
    
    def log_page_end(self, page_num: int, success: bool = True):
        """Log the end of page processing."""
        if hasattr(self, 'current_page_start'):
            elapsed = (datetime.now() - self.current_page_start).total_seconds()
            self.page_times.append(elapsed)
            status = "Success" if success else "Failed"
            self.logger.info(f"Page {page_num} {status} - Time: {elapsed:.2f}s")
    
    def log_step(self, step: str, details: Optional[str] = None):
        """Log a processing step."""
        self.processing_steps.append(step)
        msg = f"  → {step}"
        if details:
            msg += f": {details}"
        self.logger.info(msg)
    
    def log_detection(self, detection_type: str, confidence: float, result: str):
        """Log detection results."""
        self.logger.info(f"  Detection: {detection_type}")
        self.logger.info(f"    Confidence: {confidence:.2%}")
        self.logger.info(f"    Result: {result}")
    
    def log_extraction(self, extraction_type: str, element_count: int, details: Optional[Dict] = None):
        """Log extraction results."""
        self.logger.info(f"  Extraction: {extraction_type}")
        self.logger.info(f"    Elements found: {element_count}")
        if details:
            for key, value in details.items():
                self.logger.info(f"    {key}: {value}")
    
    def log_model_call(self, model: str, prompt_type: str, response_time: Optional[float] = None):
        """Log model API calls."""
        self.logger.debug(f"  Model Call: {model}")
        self.logger.debug(f"    Prompt: {prompt_type}")
        if response_time:
            self.logger.debug(f"    Response time: {response_time:.2f}s")
    
    def log_error(self, error: str, exception: Optional[Exception] = None, page_num: Optional[int] = None):
        """Log an error."""
        error_entry = {
            'time': datetime.now().isoformat(),
            'error': error,
            'page': page_num
        }
        
        if exception:
            error_entry['exception'] = str(exception)
            error_entry['traceback'] = traceback.format_exc()
            self.logger.error(f"ERROR: {error}")
            self.logger.error(f"  Exception: {exception}")
            self.logger.debug(f"  Traceback:\n{traceback.format_exc()}")
        else:
            self.logger.error(f"ERROR: {error}")
        
        self.errors.append(error_entry)
    
    def log_warning(self, warning: str, page_num: Optional[int] = None):
        """Log a warning."""
        warning_entry = {
            'time': datetime.now().isoformat(),
            'warning': warning,
            'page': page_num
        }
        self.warnings.append(warning_entry)
        self.logger.warning(f"WARNING: {warning}")
    
    def log_mermaid_generation(self, success: bool, syntax_errors: Optional[list] = None):
        """Log Mermaid diagram generation results."""
        if success:
            self.logger.info("  Mermaid generation: Success")
        else:
            self.logger.warning("  Mermaid generation: Failed")
            if syntax_errors:
                for error in syntax_errors:
                    self.logger.warning(f"    Syntax error: {error}")
    
    def log_output_created(self, output_type: str, file_path: str):
        """Log creation of output files."""
        self.logger.info(f"  Created {output_type}: {file_path}")
    
    def log_summary(self, total_pages: int, successful_pages: int, 
                    diagrams_found: int = 0, tables_found: int = 0):
        """Log processing summary."""
        elapsed_total = (datetime.now() - self.start_time).total_seconds()
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info("PROCESSING SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"File: {self.filename}")
        self.logger.info(f"Total pages: {total_pages}")
        self.logger.info(f"Successful pages: {successful_pages}")
        self.logger.info(f"Failed pages: {total_pages - successful_pages}")
        
        if diagrams_found > 0:
            self.logger.info(f"Diagrams found: {diagrams_found}")
        if tables_found > 0:
            self.logger.info(f"Tables found: {tables_found}")
        
        self.logger.info(f"Total errors: {len(self.errors)}")
        self.logger.info(f"Total warnings: {len(self.warnings)}")
        
        if self.page_times:
            avg_time = sum(self.page_times) / len(self.page_times)
            self.logger.info(f"Average time per page: {avg_time:.2f}s")
        
        self.logger.info(f"Total processing time: {elapsed_total:.2f}s")
        self.logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Write summary JSON
        self._write_summary_json(total_pages, successful_pages, diagrams_found, tables_found)
    
    def _write_summary_json(self, total_pages: int, successful_pages: int,
                           diagrams_found: int, tables_found: int):
        """Write a JSON summary file for programmatic access."""
        summary = {
            'filename': self.filename,
            'output_dir': str(self.output_dir),
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_time_seconds': (datetime.now() - self.start_time).total_seconds(),
            'pages': {
                'total': total_pages,
                'successful': successful_pages,
                'failed': total_pages - successful_pages
            },
            'findings': {
                'diagrams': diagrams_found,
                'tables': tables_found
            },
            'performance': {
                'page_times': self.page_times,
                'average_page_time': sum(self.page_times) / len(self.page_times) if self.page_times else 0
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'processing_steps': self.processing_steps
        }
        
        summary_file = self.log_dir / f"{Path(self.filename).stem}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"\nSummary JSON written to: {summary_file}")
    
    def log_debug(self, message: str):
        """Log debug information."""
        self.logger.debug(message)
    
    def log_info(self, message: str):
        """Log general information."""
        self.logger.info(message)
    
    def close(self):
        """Close the logger and clean up handlers."""
        # Remove all handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


class BatchProcessingLogger:
    """Logger for batch processing multiple files."""
    
    def __init__(self, batch_output_dir: str):
        """Initialize batch processing logger."""
        self.batch_output_dir = Path(batch_output_dir)
        self.batch_log_file = self.batch_output_dir / "batch_processing.log"
        
        # Ensure directory exists
        self.batch_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = self._setup_logger()
        self.start_time = datetime.now()
        self.file_results = []
    
    def _setup_logger(self) -> logging.Logger:
        """Setup batch logger."""
        logger = logging.getLogger(f"netintel_ocr.batch_{id(self)}")
        logger.setLevel(logging.INFO)
        logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(self.batch_log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_batch_start(self, total_files: int):
        """Log batch processing start."""
        self.logger.info("=" * 70)
        self.logger.info("BATCH PROCESSING STARTED")
        self.logger.info("=" * 70)
        self.logger.info(f"Total files to process: {total_files}")
        self.logger.info(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("")
    
    def log_file_complete(self, filename: str, success: bool, 
                         processing_time: float, error: Optional[str] = None):
        """Log completion of a file."""
        status = "✓" if success else "✗"
        self.logger.info(f"{status} {filename} - {processing_time:.2f}s")
        
        if error:
            self.logger.info(f"  Error: {error}")
        
        self.file_results.append({
            'filename': filename,
            'success': success,
            'time': processing_time,
            'error': error
        })
    
    def log_batch_complete(self):
        """Log batch processing completion."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        successful = sum(1 for r in self.file_results if r['success'])
        failed = len(self.file_results) - successful
        
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("BATCH PROCESSING COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info(f"Total files: {len(self.file_results)}")
        self.logger.info(f"Successful: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Total time: {elapsed:.2f}s")
        self.logger.info(f"Average time per file: {elapsed/len(self.file_results):.2f}s")
        
        # Write batch summary
        summary = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_time': elapsed,
            'files': self.file_results,
            'statistics': {
                'total': len(self.file_results),
                'successful': successful,
                'failed': failed
            }
        }
        
        summary_file = self.batch_output_dir / "batch_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"\nBatch summary written to: {summary_file}")