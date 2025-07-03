"""
Logging configuration for AutoTablature.
"""

import logging
import os
from datetime import datetime


def setup_logger(name, level=logging.INFO, log_dir="logs"):
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name (str): Logger name
        level: Logging level
        log_dir (str): Directory for log files
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_filename = os.path.join(log_dir, f"autotablature_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def setup_training_logger(name, run_id, log_dir="logs/training"):
    """
    Set up a logger specifically for training runs.
    
    Args:
        name (str): Logger name
        run_id (str): Unique identifier for this training run
        log_dir (str): Directory for training logs
        
    Returns:
        logging.Logger: Configured training logger
    """
    # Create logger
    logger = logging.getLogger(f"{name}.training.{run_id}")
    logger.setLevel(logging.DEBUG)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Training log file
    log_filename = os.path.join(log_dir, f"training_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for training
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
