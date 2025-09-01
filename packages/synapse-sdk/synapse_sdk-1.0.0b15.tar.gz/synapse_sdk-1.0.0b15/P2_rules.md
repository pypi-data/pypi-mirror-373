# P2 Code Review Rules - Core Functionality (High)

**Priority Level:** P2 (High)
**Focus:** Core functionality and architecture

## 1. Functional Correctness

- Code works as intended and meets requirements
- All edge cases are handled properly
- Business logic is implemented correctly
- Integration with existing systems is correct

## 2. Testing Requirements

- All new functionality has comprehensive tests
- Tests pass locally and in CI/CD pipeline
- Test coverage meets project standards (aim for >90%)
- Both positive and negative test cases included
- Mock external dependencies appropriately

## 3. Architecture and Design

- Follows established architectural patterns
- Proper separation of concerns
- Dependencies are managed correctly
- APIs are well-designed and consistent
- Plugin system integration follows standards

## 4. Performance

- No obvious performance bottlenecks
- Efficient algorithms and data structures
- Database queries are optimized
- Memory usage is reasonable
- Response times meet requirements

## Review Guidelines

**Functional Correctness Checklist:**
- [ ] Code implements requirements correctly
- [ ] Edge cases are handled
- [ ] Business logic is sound
- [ ] Integration points work properly
- [ ] Error scenarios are covered

**Testing Checklist:**
- [ ] New functionality has tests
- [ ] Tests pass locally and in CI
- [ ] Test coverage is adequate (>90%)
- [ ] Both success and failure cases tested
- [ ] External dependencies are mocked

**Architecture Checklist:**
- [ ] Follows established patterns
- [ ] Proper separation of concerns
- [ ] Dependencies well-managed
- [ ] APIs are consistent
- [ ] Plugin integration follows standards

**Performance Checklist:**
- [ ] No obvious bottlenecks
- [ ] Algorithms are efficient
- [ ] Database queries optimized
- [ ] Memory usage reasonable
- [ ] Response times acceptable