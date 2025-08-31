# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-XX

### Added
- Initial release of trading-common package
- Database module with asyncpg wrapper and inbox/outbox tables
- Kafka module with AIOKafka producer/consumer wrappers
- Schema validation module using trading-contracts
- Outbox processing utilities
- Comprehensive test suite
- Example usage in strategy service
- Development tools configuration (black, isort, mypy, pytest)

### Features
- **Database**: Connection pooling, idempotent message processing, outbox pattern
- **Kafka**: Reliable producer/consumer with transaction safety
- **Validation**: Event schema validation through trading-contracts
- **Outbox**: Reliable message publishing with database persistence
