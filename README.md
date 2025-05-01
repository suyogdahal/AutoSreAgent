# Automated SRE Agent

An automated SRE tool that monitors application logs, detects errors, and handles incident management (for now just creates jira tickets).

## Features

- Continuous log monitoring for error detection
- Error fingerprinting to avoid duplicate issue processing
- Automatic error investigation using StackExchange
- Jira ticket creation for identified issues
- Intelligent oncall employee routing

## Configuration

Set the following api keys:

```
OPENAI_API_KEY=your_openai_key
JIRA_API_TOKEN=your_jira_token
STACKEXCHANGE_KEY=your_stackexchange_key
```

Also set the following config env files:
`MONITORING_INTERVAL` to control check frequency (default: 60 seconds)
`LOG_FILE_PATH` to target specific log files

## Testing

If you do not have a log file, xthere is a helper file in `utils/random_log_generator.py` which kind of does what its name says ;)

## Footnotes

This was created as a part of course project requirement for CS 595 - TCPS: MLOps for Generative AI.
