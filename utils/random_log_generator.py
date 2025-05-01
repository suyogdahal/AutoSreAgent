import random
import time
import datetime
import uuid
import sys
import socket


class BankLogGenerator:
    def __init__(self):
        self.users = [f"user_{i}" for i in range(1000, 1050)]
        self.session_ids = {}
        self.transaction_types = [
            "DEPOSIT",
            "WITHDRAW",
            "TRANSFER",
            "BILL_PAYMENT",
            "CHECK_BALANCE",
        ]
        self.endpoints = [
            "/api/accounts",
            "/api/transactions",
            "/api/balance",
            "/api/statements",
            "/api/payments",
            "/api/profile",
            "/api/auth",
            "/api/settings",
        ]
        self.error_types = [
            "DatabaseConnectionError",
            "AuthenticationFailure",
            "InvalidTransactionAmount",
            "InsufficientFunds",
            "ServiceUnavailable",
            "RateLimitExceeded",
            "InvalidAccountNumber",
            "SecurityViolation",
            "TimeoutError",
        ]
        self.http_methods = ["GET", "POST", "PUT", "DELETE"]
        self.http_status = [200, 201, 400, 401, 403, 404, 500, 502, 504]

        self.log_levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def get_random_ip(self):
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

    def get_session_id(self, username):
        if username not in self.session_ids or random.random() < 0.1:
            self.session_ids[username] = str(uuid.uuid4())
        return self.session_ids[username]

    def get_transaction_id(self):
        return str(uuid.uuid4()).replace("-", "")[:16].upper()

    def get_account_number(self):
        return f"ACCT-{random.randint(10000000, 99999999)}"

    def generate_normal_log(self):
        username = random.choice(self.users)
        endpoint = random.choice(self.endpoints)
        method = random.choice(self.http_methods)
        session_id = self.get_session_id(username)
        ip_address = self.get_random_ip()
        status_code = random.choices(
            [200, 201, 204, 400, 401, 404, 500], weights=[85, 5, 3, 3, 2, 1, 1]
        )[0]

        response_time = round(random.uniform(0.01, 2.5), 3)

        if status_code >= 400:
            log_level = "ERROR" if status_code >= 500 else "WARNING"
        else:
            log_level = "INFO"

        log_data = {
            "timestamp": self.get_timestamp(),
            "level": log_level,
            "request_id": str(uuid.uuid4()),
            "method": method,
            "endpoint": endpoint,
            "username": username,
            "session_id": session_id,
            "ip_address": ip_address,
            "status_code": status_code,
            "response_time": response_time,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

        return (
            f"[{log_data['timestamp']}] [{log_data['level']}] [RequestID: {log_data['request_id']}] {method} {endpoint} - "
            f"User: {username} - Session: {session_id} - IP: {ip_address} - Status: {status_code} - Time: {response_time}ms"
        )

    def generate_transaction_log(self):
        username = random.choice(self.users)
        transaction_type = random.choice(self.transaction_types)
        amount = round(random.uniform(10.0, 5000.0), 2)
        transaction_id = self.get_transaction_id()
        account = self.get_account_number()
        target_account = (
            self.get_account_number() if transaction_type == "TRANSFER" else None
        )

        success = random.random() < 0.95
        status = "SUCCESS" if success else "FAILED"
        log_level = "INFO" if success else "WARNING"

        log_data = {
            "timestamp": self.get_timestamp(),
            "level": log_level,
            "transaction_id": transaction_id,
            "type": transaction_type,
            "username": username,
            "account": account,
            "amount": f"${amount:.2f}",
            "status": status,
        }

        if target_account:
            log_data["target_account"] = target_account

        if transaction_type == "TRANSFER" and target_account:
            message = (
                f"[{log_data['timestamp']}] [{log_level}] [TransactionID: {transaction_id}] {username} {transaction_type} "
                f"{log_data['amount']} from {account} to {target_account} - {status}"
            )
        else:
            message = (
                f"[{log_data['timestamp']}] [{log_level}] [TransactionID: {transaction_id}] {username} {transaction_type} "
                f"{log_data['amount']} in account {account} - {status}"
            )

        return message

    def generate_auth_log(self):
        username = random.choice(self.users)
        ip_address = self.get_random_ip()
        success = random.random() < 0.9
        event_type = "LOGIN_SUCCESS" if success else "LOGIN_FAILURE"
        log_level = "INFO" if success else "WARNING"

        log_data = {
            "timestamp": self.get_timestamp(),
            "level": log_level,
            "event": event_type,
            "username": username,
            "ip_address": ip_address,
        }

        if success:
            self.session_ids[username] = str(uuid.uuid4())
            log_data["session_id"] = self.session_ids[username]
            message = f"[{log_data['timestamp']}] [{log_level}] [Auth] User {username} successfully logged in from {ip_address} - Session: {log_data['session_id']}"
        else:
            reason = random.choice(
                [
                    "Invalid password",
                    "Account locked",
                    "2FA failed",
                    "Suspicious location",
                ]
            )
            log_data["reason"] = reason
            message = f"[{log_data['timestamp']}] [{log_level}] [Auth] Failed login attempt for user {username} from {ip_address} - Reason: {reason}"

        return message

    def generate_system_log(self):
        components = [
            "DatabasePool",
            "AuthService",
            "TransactionProcessor",
            "NotificationService",
            "APIGateway",
            "CacheService",
            "FraudDetection",
            "ReportingEngine",
        ]
        component = random.choice(components)
        log_level = random.choices(
            list(self.log_levels.keys()), weights=[5, 65, 15, 10, 5]
        )[0]

        system_events = {
            "DEBUG": [
                "Detailed connection pool stats: active=5, idle=10, waiting=2",
                "Cache hit ratio: 0.89",
                "Query execution plan: INDEX SCAN on users WHERE username='user_1032'",
                "Thread pool status: active=12, queued=3, completed=1456",
                "Memory usage: heap=1.2GB, non-heap=384MB",
            ],
            "INFO": [
                f"{component} service started successfully",
                "Database connection pool initialized with 20 connections",
                "Successfully processed batch of 100 transactions",
                "Scheduled maintenance completed in 1.5 seconds",
                "Configuration reloaded with 15 updated parameters",
            ],
            "WARNING": [
                "High CPU utilization detected: 85%",
                "Database connection pool nearing capacity: 18/20 used",
                "Slow query detected: execution time 3.5s",
                f"Rate limiting applied to IP {self.get_random_ip()}",
                "Deprecated API endpoint accessed: /api/v1/legacy",
            ],
            "ERROR": [
                "Failed to connect to database after 3 retries",
                "Transaction processing timeout after 30 seconds",
                "External payment gateway returned error code E4502",
                "Unable to send email notifications: SMTP connection refused",
                "API rate limit exceeded for service 'reporting'",
            ],
            "CRITICAL": [
                "Database cluster failover initiated",
                "Security breach detected: unauthorized access attempt to admin panel",
                "Disk space critical: 98% used on /data volume",
                "Multiple payment processing failures detected - entering fallback mode",
                "System-wide performance degradation detected",
            ],
        }

        message = random.choice(system_events[log_level])
        host = socket.gethostname()
        pid = random.randint(1000, 9999)

        return f"[{self.get_timestamp()}] [{log_level}] [{component}] [{host}] [PID:{pid}] {message}"

    def generate_error_with_traceback(self):
        # More SRE-focused error types
        error_types = [
            "ConnectionRefusedError",
            "MemoryError",
            "TimeoutError",
            "ConnectionResetError",
            "InternalServerError",
            "DatabaseDeadlockError",
            "ResourceExhaustionError",
            "ThreadPoolExhaustionError",
            "CircuitBreakerOpenError",
            "DependencyFailureError",
            "KafkaProducerTimeoutError",
            "RedisConnectionError",
            "ElasticsearchClusterHealthError",
        ]
        error_type = random.choice(error_types)
        endpoint = random.choice(self.endpoints)

        # Create context for SRE-relevant errors
        contexts = {
            "ConnectionRefusedError": "Failed to connect to database primary at 10.45.2.8:5432",
            "MemoryError": "JVM heap space exhausted during request processing",
            "TimeoutError": "Request to payment gateway timed out after 30 seconds",
            "ConnectionResetError": "Connection reset by peer while fetching data from cache server",
            "InternalServerError": "Unexpected exception in transaction processing pipeline",
            "DatabaseDeadlockError": "Transaction deadlock detected on table 'accounts'",
            "ResourceExhaustionError": "Worker pool exhausted (100/100 connections in use)",
            "ThreadPoolExhaustionError": "Thread pool rejection - max size reached",
            "CircuitBreakerOpenError": "Circuit breaker open for notifications service",
            "DependencyFailureError": "Critical dependency 'user-profile-service' is unavailable",
            "KafkaProducerTimeoutError": "Failed to produce message to kafka-transactions-topic",
            "RedisConnectionError": "Redis connection pool timeout after 5000ms",
            "ElasticsearchClusterHealthError": "Elasticsearch cluster health is RED (2/5 nodes available)",
        }

        context = contexts.get(error_type, "Unexpected system error occurred")

        # Generate more realistic production application traceback
        frames = [
            f'  File "/app/banking/api/controllers.py", line {random.randint(50, 300)}, in process_request\n    response = await service.execute_transaction(transaction_data)',
            f'  File "/app/banking/service/transaction_service.py", line {random.randint(20, 200)}, in execute_transaction\n    result = await self.repository.commit(validated_data)',
            f'  File "/app/banking/repository/transaction_repo.py", line {random.randint(100, 500)}, in commit\n    async with self.db_pool.acquire() as connection:\n        return await self._execute_transaction(connection, data)',
            f'  File "/app/banking/repository/base.py", line {random.randint(50, 150)}, in _execute_transaction\n    await self._ensure_connection_healthy(conn)',
            f'  File "/app/banking/infrastructure/db/connection.py", line {random.randint(30, 90)}, in _ensure_connection_healthy\n    await conn.execute("SELECT 1")',
            f'  File "/usr/local/lib/python3.9/site-packages/asyncpg/connection.py", line {random.randint(1000, 1500)}, in execute\n    return await self._protocol.query(query, timeout)',
            f'  File "/usr/local/lib/python3.9/site-packages/asyncpg/protocol.py", line {random.randint(200, 400)}, in query\n    raise {error_type}("{context}")',
        ]

        traceback_text = "Traceback (most recent call last):\n" + "\n".join(frames)
        timestamp = self.get_timestamp()
        request_id = str(uuid.uuid4())
        host = socket.gethostname()

        error_message = (
            f"[{timestamp}] [ERROR] [RequestID: {request_id}] [host: {host}] "
            f"Unhandled exception during {endpoint} request processing: {error_type}: {context}\n{traceback_text}"
        )
        return error_message

    def generate_log(self):
        log_type = random.choices(
            ["normal", "transaction", "auth", "system", "error"],
            weights=[40, 30, 15, 10, 5],
        )[0]

        if log_type == "normal":
            return self.generate_normal_log()
        elif log_type == "transaction":
            return self.generate_transaction_log()
        elif log_type == "auth":
            return self.generate_auth_log()
        elif log_type == "system":
            return self.generate_system_log()
        else:
            return self.generate_error_with_traceback()


def main():
    log_generator = BankLogGenerator()

    log_file = "output/logs.log"

    # Make sure output directory exists
    import os

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    print("Generating banking system logs until interrupted...")
    print(f"Logs will be written to: {log_file}")
    print("Press Ctrl+C to stop")

    log_count = 0

    try:
        with open(log_file, "w") as f:
            while True:
                log = log_generator.generate_log()
                log_count += 1
                print(f"[{log_count}] {log}")
                f.write(log + "\n")
                f.flush()  # Ensure log is written to disk immediately

                # Add some delay between logs
                time.sleep(random.uniform(0.1, 4.0))
    except KeyboardInterrupt:
        print(f"\nLog generation stopped. {log_count} logs written to {log_file}")

    print("Done!")


if __name__ == "__main__":
    main()
