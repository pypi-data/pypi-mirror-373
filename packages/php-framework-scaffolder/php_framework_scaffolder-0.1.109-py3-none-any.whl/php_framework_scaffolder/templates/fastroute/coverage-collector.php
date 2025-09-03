<?php
declare(strict_types=1);

/**
 * Code Coverage Handler
 *
 * Handles code coverage collection using Xdebug for individual requests
 */
class CoverageHandler
{
    /** @var string Directory for storing coverage data */
    private const COVERAGE_DIR = '/tmp/coverage';

    /** @var string Filename for error logs */
    private const ERROR_LOG_FILE = 'coverage_errors.log';

    /** @var string[] Required subdirectories */
    private const REQUIRED_SUBDIRECTORIES = ['requests', 'logs'];

    /** @var string Unique identifier for the current request */
    private string $requestId;

    /** @var string Path to the current request's coverage file */
    private string $requestCoverageFilePath;

    /** @var string Experiment ID for the current request */
    private string $experimentId;

    /**
     * Initialize the coverage handler
     *
     * @throws RuntimeException If initialization fails
     */
    public function __construct()
    {
        try {
            $this->requestId = self::generateUuid();
            $this->experimentId = $_SERVER['HTTP_X_EXPERIMENT_ID'] ?? "default";
            $this->initializePaths();
            $this->ensureDirectoryStructure();
            $this->startCoverage();

            header("X-Request-ID: {$this->requestId}");
        } catch (Exception $e) {
            $this->logError($e, 'Initialization failed');
            throw $e;
        }
    }

    /**
     * Generate a new UUID v4 with optimized performance
     *
     * @return string UUID v4 string
     */
    private static function generateUuid(): string
    {
        $data = random_bytes(16);
        // Set version to 0100
        $data[6] = chr(ord($data[6]) & 0x0f | 0x40);
        // Set bits 6-7 to 10
        $data[8] = chr(ord($data[8]) & 0x3f | 0x80);

        $hex = bin2hex($data);
        return substr($hex, 0, 8) . '-' .
               substr($hex, 8, 4) . '-' .
               substr($hex, 12, 4) . '-' .
               substr($hex, 16, 4) . '-' .
               substr($hex, 20, 12);
    }

    /**
     * Initialize file paths for coverage data
     */
    private function initializePaths(): void
    {
        // Get CPU ticks for monotonically increasing value
        $cpuTicks = hrtime(true); // nanosecond precision as integer

        // Include CPU ticks in filename to ensure uniqueness
        $this->requestCoverageFilePath = self::COVERAGE_DIR . '/requests/' . $this->experimentId . '/' . $cpuTicks . '_' . $this->requestId . '.json';
    }

    /**
     * Ensure all required coverage directories exist
     *
     * @throws RuntimeException If directory creation fails
     */
    private function ensureDirectoryStructure(): void
    {
        // Create base directory
        self::createDirectoryIfNotExists(self::COVERAGE_DIR);

        // Create subdirectories
        foreach (self::REQUIRED_SUBDIRECTORIES as $subdir) {
            self::createDirectoryIfNotExists(self::COVERAGE_DIR . '/' . $subdir);
        }
    }

    /**
     * Create directory if it doesn't exist
     *
     * @param string $dir Directory path
     * @throws RuntimeException If directory creation fails
     */
    private static function createDirectoryIfNotExists(string $dir): void
    {
        if (!is_dir($dir) && !@mkdir($dir, 0755, true)) {
            throw new RuntimeException("Failed to create directory: $dir");
        }
    }

    /**
     * Start code coverage collection
     *
     * @throws RuntimeException If Xdebug extension is not loaded
     */
    private function startCoverage(): void
    {
        if (!extension_loaded('xdebug')) {
            throw new RuntimeException('Xdebug extension is not loaded');
        }
        xdebug_start_code_coverage(XDEBUG_CC_UNUSED | XDEBUG_CC_DEAD_CODE);
    }

    /**
     * Collect and store coverage data
     */
    public function dumpCoverage(): void
    {
        try {
            $currentCoverage = xdebug_get_code_coverage();
            xdebug_stop_code_coverage();

            // Save current request coverage
            $this->saveRequestCoverage($currentCoverage);
        } catch (Exception $e) {
            $this->logError($e, 'Failed to dump coverage');
        }
    }

    /**
     * Save coverage data for current request with additional metadata
     *
     * @param array $coverage Raw coverage data from Xdebug
     * @throws RuntimeException If file writing fails
     */
    private function saveRequestCoverage(array $coverage): void
    {
        $coverageData = [
            'timestamp' => (int)(microtime(true) * 1000),
            'experiment_id' => $this->experimentId,
            'request_id' => $this->requestId,
            'superglobals' => $this->captureSuperglobals(),
            'coverage' => $coverage
        ];

        self::writeJsonFile($this->requestCoverageFilePath, $coverageData);
    }

    /**
     * Capture relevant superglobals for debugging
     *
     * @return array Captured superglobals
     */
    private function captureSuperglobals(): array
    {
        return [
            'server' => $_SERVER,
            'get' => $_GET,
            'post' => $_POST,
            'files' => $_FILES,
            'cookie' => $_COOKIE,
            'request' => $_REQUEST,
            'env' => $_ENV,
        ];
    }

    /**
     * Get the request ID
     *
     * @return string Current request ID
     */
    public function getRequestId(): string
    {
        return $this->requestId;
    }

    /**
     * Log error information in JSON format
     *
     * @param Exception $exception The exception to log
     * @param string $context Context information about where the error occurred
     */
    private function logError(Exception $exception, string $context = ''): void
    {
        $logFile = self::COVERAGE_DIR . '/logs/' . self::ERROR_LOG_FILE;

        $errorData = [
            'timestamp' => date('Y-m-d H:i:s'),
            'context' => $context,
            'message' => $exception->getMessage(),
            'code' => $exception->getCode(),
            'file' => $exception->getFile(),
            'line' => $exception->getLine(),
            'trace' => $exception->getTraceAsString(),
            'request_id' => $this->requestId ?? 'unknown',
            'request_info' => $this->captureRequestInfo()
        ];

        $json = @json_encode($errorData) . "\n";
        @file_put_contents($logFile, $json, FILE_APPEND);
        error_log('Coverage handler error: ' . $exception->getMessage());
    }

    /**
     * Capture basic request information for debugging
     *
     * @return array Request information
     */
    private function captureRequestInfo(): array
    {
        return [
            'uri' => $_SERVER['REQUEST_URI'] ?? 'unknown',
            'method' => $_SERVER['REQUEST_METHOD'] ?? 'unknown',
            'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
            'get' => $_GET,
            'post' => $_POST,
        ];
    }

    /**
     * Write data to a JSON file
     *
     * @param string $filePath Path to target file
     * @param mixed $data Data to encode and write
     * @throws RuntimeException If encoding or writing fails
     */
    private static function writeJsonFile(string $filePath, $data): void
    {
        // create directory if it doesn't exist
        $dir = dirname($filePath);
        if (!is_dir($dir) && !@mkdir($dir, 0755, true)) {
            $error = error_get_last();
            throw new RuntimeException("Failed to create directory: $dir. Error: " . ($error ? $error['message'] : 'Unknown error'));
        }

        $json = @json_encode($data);
        if ($json === false) {
            throw new RuntimeException('Failed to encode JSON data: ' . json_last_error_msg());
        }

        if (@file_put_contents($filePath, $json) === false) {
            $error = error_get_last();
            throw new RuntimeException("Failed to write file: $filePath. Error: " . ($error ? $error['message'] : 'Unknown error'));
        }
    }

    /**
     * Static method to log errors occurring outside the class instance
     *
     * @param Exception $exception The exception to log
     * @param string $context Context information
     */
    public static function logStaticError(Exception $exception, string $context = ''): void
    {
        try {
            $logDir = self::COVERAGE_DIR . '/logs';
            self::createDirectoryIfNotExists(self::COVERAGE_DIR);
            self::createDirectoryIfNotExists($logDir);

            $logFile = $logDir . '/' . self::ERROR_LOG_FILE;

            $errorData = [
                'timestamp' => date('Y-m-d H:i:s'),
                'context' => $context,
                'message' => $exception->getMessage(),
                'code' => $exception->getCode(),
                'file' => $exception->getFile(),
                'line' => $exception->getLine(),
                'trace' => $exception->getTraceAsString(),
                'request_info' => [
                    'uri' => $_SERVER['REQUEST_URI'] ?? 'unknown',
                    'method' => $_SERVER['REQUEST_METHOD'] ?? 'unknown',
                    'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
                    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
                    'get' => $_GET,
                    'post' => $_POST,
                ]
            ];

            $json = @json_encode($errorData) . "\n";
            @file_put_contents($logFile, $json, FILE_APPEND);
        } catch (Exception $e) {
            // Last resort error reporting
            error_log('Critical coverage handler error: ' . $e->getMessage());
        }

        error_log('Coverage handler error: ' . $exception->getMessage());
    }
}

// Initialize coverage handler and register shutdown function
try {
    $coverageHandler = new CoverageHandler();
    register_shutdown_function([$coverageHandler, 'dumpCoverage']);
} catch (Exception $e) {
    CoverageHandler::logStaticError($e, 'Initialization error');
}
