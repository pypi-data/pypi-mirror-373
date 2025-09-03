# -*- coding: utf-8 -*-

"""Core constants shared across the nac-test framework."""

import os

# Retry configuration - Generic retry logic used by multiple components
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1.0
RETRY_MAX_DELAY = 60.0
RETRY_EXPONENTIAL_BASE = 2.0

# General timeouts
DEFAULT_TEST_TIMEOUT = 21600  # 6 hours per test
CONNECTION_CLOSE_DELAY = 0.25  # seconds

# Concurrency limits - Can be used by both PyATS and Robot
# Can be overridden via NAC_API_CONCURRENCY environment variable
DEFAULT_API_CONCURRENCY = int(os.environ.get("NAC_API_CONCURRENCY", "55"))
DEFAULT_SSH_CONCURRENCY = int(os.environ.get("NAC_SSH_CONCURRENCY", "20"))

# Progress reporting
PROGRESS_UPDATE_INTERVAL = 0.5  # seconds
