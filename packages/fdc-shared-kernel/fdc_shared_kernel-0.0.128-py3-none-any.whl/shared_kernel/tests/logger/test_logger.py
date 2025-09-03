import unittest
import logging
import os
from shared_kernel.logger import Logger


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.logger_name = "test_logger"
        self.log_file = "test_logs.log"
        self.log_directory = "./test_logs"
        self.logger = Logger(name=self.logger_name)

    def test_singleton_pattern(self):
        """
        Test that Logger follows the singleton pattern.
        """
        another_logger = Logger(name=self.logger_name)
        self.assertIs(self.logger, another_logger)

    def test_logger_initialization(self):
        """
        Test logger initialization with default parameters.
        """
        logger = Logger()
        self.assertEqual(logger.logger.name, "test_logger")
        self.assertEqual(logger.logger.level, logging.DEBUG)

    def test_configure_logger(self):
        """
        Test that configure_logger adds handlers correctly.
        """
        self.assertEqual(len(self.logger.logger.handlers), 4)
        self.logger.configure_logger()
        self.assertGreaterEqual(len(self.logger.logger.handlers), 2)

    def test_add_stream_handler(self):
        """
        Test adding a stream handler.
        """
        original_handlers_count = len(self.logger.logger.handlers)
        self.logger.add_stream_handler()
        self.assertEqual(len(self.logger.logger.handlers), original_handlers_count + 1)

    def test_add_file_handler(self):
        """
        Test adding a file handler and creation of log directory if it doesn't exist.
        """
        original_handlers_count = len(self.logger.logger.handlers)
        self.logger.add_file_handler(log_file=self.log_file, log_directory=self.log_directory)
        self.assertEqual(len(self.logger.logger.handlers), original_handlers_count + 1)
        self.assertTrue(os.path.exists(self.log_directory))

    def test_log_methods(self):
        """
        Test logging methods (info, error, debug, warning).
        """
        # Since the logger writes to stdout and a file, we can't easily capture output in tests.
        # Instead, ensure that calling these methods doesn't raise exceptions.
        self.logger.info("Test info message")
        self.logger.error("Test error message")
        self.logger.debug("Test debug message")
        self.logger.warning("Test warning message")


if __name__ == "__main__":
    unittest.main()
