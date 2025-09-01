# P1 Code Review Rules - Security and Stability (Critical)

**Priority Level:** P1 (Critical)
**Focus:** Security and Stability

## 1. Security Vulnerabilities

- No hardcoded secrets, API keys, or passwords
- No SQL injection vulnerabilities
- No exposed sensitive data in logs or error messages
- Proper input validation and sanitization
- Secure handling of user data and authentication

## 2. Critical Stability Issues

- No infinite loops or potential deadlocks
- Proper error handling for all external dependencies
- Memory leak prevention
- Thread safety in concurrent code
- Graceful handling of resource exhaustion

## 3. Data Integrity

- No data corruption risks
- Proper transaction management
- Backup and recovery considerations
- Data validation before persistence

## Review Guidelines

**STOP THE REVIEW** if any P1 issues are found. These must be fixed before proceeding with other review priorities.

**Security Checklist:**
- [ ] No hardcoded credentials or secrets
- [ ] Input validation implemented
- [ ] Authentication/authorization properly handled
- [ ] Sensitive data not exposed in logs
- [ ] No obvious injection vulnerabilities

**Stability Checklist:**
- [ ] No infinite loops or deadlock potential
- [ ] External dependencies have proper error handling
- [ ] Memory management is appropriate
- [ ] Concurrent code is thread-safe
- [ ] Resource exhaustion scenarios handled

**Data Integrity Checklist:**
- [ ] Data validation before persistence
- [ ] Transaction boundaries are correct
- [ ] No data corruption risks
- [ ] Backup/recovery considerations addressed