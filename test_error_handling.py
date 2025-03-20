#!/usr/bin/env python3
import sys
import logging
import os
import traceback

def setup_logging(debug=False):
    """Configure logging for the application"""
    level = logging.DEBUG if debug else logging.INFO
    
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, "test_log.txt")
    
    try:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        print(f"Logging to {log_file}")
    except (IOError, PermissionError) as e:
        # If log file can't be created, log to console only
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        print(f"Could not create log file at {log_file}: {e}")
    
    return logging.getLogger('test')

def clean_exit(exit_code=0):
    """Clean up before exiting the application"""
    print(f"Exiting with code {exit_code}")
    sys.exit(exit_code)

def test_function_with_error():
    """A function that will raise an error"""
    x = 1 / 0  # Will raise ZeroDivisionError

def main():
    """Main test function"""
    # Setup logging
    logger = setup_logging(debug=True)
    logger.info("Starting test program")
    
    try:
        # Test normal logging
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        
        # Test error handling
        logger.info("About to try a function that will raise an error")
        test_function_with_error()
    except Exception as e:
        logger.critical(f"Caught an error: {e}")
        logger.critical(traceback.format_exc())
        print(f"Error caught: {e}")
        clean_exit(1)
    
    logger.info("Test completed successfully")
    clean_exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Test interrupted by user")
        clean_exit(1)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        try:
            logging.critical(f"Unhandled exception: {e}")
            logging.critical(traceback.format_exc())
        except:
            pass
        clean_exit(1) 