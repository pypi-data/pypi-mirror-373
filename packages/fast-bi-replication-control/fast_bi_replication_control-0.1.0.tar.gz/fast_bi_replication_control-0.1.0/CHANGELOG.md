# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-01

### Added
- **Beta Release** Initial beta release of Fast.BI Replication Control
- **AirbyteApiHook**: Comprehensive hook for Airbyte API interactions
- **AirbyteJobMonitorSensor**: Sensor for monitoring Airbyte job status
- **AirbyteJobMonitorOperator**: Operator for monitoring and canceling long-running jobs
- **JobTracker**: Advanced job tracking with cross-worker persistence
- **trackAndMonitorJobs**: Utility function for job monitoring
- **createJobTracker**: Factory function for job tracker creation

### Features
- Advanced job tracking with Airflow Variables persistence
- Worker consistency through queue pinning
- Accurate duration calculation from stored start times
- Full context provision (connection names, workspace info)
- Smart job discovery using API filters
- Configurable time limits per connection
- Dry run mode for safety
- Robust error handling and logging

### Technical
- Multi-layered persistence strategy (Variables + XCom fallback)
- HPA scaling compatibility
- Worker restart resilience
- Comprehensive error handling
- Detailed logging and monitoring

## [Unreleased]

### Planned
- Additional Airbyte job types support
- Enhanced monitoring dashboards
- Performance optimizations
- Extended configuration options
