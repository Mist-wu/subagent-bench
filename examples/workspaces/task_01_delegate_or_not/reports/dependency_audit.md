# Dependency Audit

- `src/payments/legacy.ts` still imports a deprecated helper.
- `src/auth/token.ts` uses an old signing package.
- `src/worker/scheduler.ts` relies on a deprecated retry wrapper.
