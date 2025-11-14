# Dependency Compatibility Matrix
**Quick Reference Guide**

## Current vs Target Versions

```
Package                        Current      →  Target       Risk Level
─────────────────────────────────────────────────────────────────────────
vitest                         1.6.1        →  4.0.8        🔴 HIGH
vite                          5.4.21        →  6.0+         🔴 HIGH (auto)
esbuild                0.17.19 / 0.21.5     →  0.25.4+      🟢 LOW (auto)
wrangler                      3.114.15      →  4.48.0       🟡 MEDIUM
@cloudflare/workers-types    4.20241127.0   →  4.20251113.0 🟢 LOW
postal-mime                   2.3.2         →  2.3.2        ✅ OK
```

## Vulnerability Chain

```
esbuild (GHSA-67mh-4wv8-2f99)
   ├─→ vite
   │    ├─→ vite-node
   │    │    └─→ vitest ⚠️
   │    └─→ vitest ⚠️
   │
   └─→ wrangler ⚠️
        ├─→ @esbuild-plugins/node-globals-polyfill
        └─→ @esbuild-plugins/node-modules-polyfill
```

## Node.js Version Requirements

```
Current Project:   Node ≥18.0.0
vitest v1.6.1:     Node ^18.0.0 || ≥20.0.0  ✅
vitest v4.0.8:     Node ^20.0.0 || ^22.0.0 || ≥24.0.0  ⚠️ (Drops Node 18)
wrangler v4:       Node ≥18.0.0  ✅
```

**Action Required:** Ensure Node 20+ before upgrading vitest to v4

## Peer Dependency Impact

### Wrangler v3 → v4
```diff
+ @cloudflare/workers-types: ^4.20251109.0 (NEW requirement)
```

### Vitest v1 → v4
```diff
  @types/node:
- ^18.0.0 || ≥20.0.0
+ ^20.0.0 || ^22.0.0 || ≥24.0.0

  vite (new hard dependency):
+ ^6.0.0 || ^7.0.0
```

## Upgrade Decision Tree

```
Start: npm audit shows 5 vulnerabilities
│
├─ Quick Fix (1 hour):
│  └─ npm install --save-dev wrangler@4.48.0 @cloudflare/workers-types@latest
│     └─ Fixes: wrangler + esbuild@0.17.19
│        └─ Remaining: vitest vulnerabilities
│
└─ Complete Fix (4-8 hours):
   └─ npm install --save-dev vitest@4.0.8
      ├─ Requires: Node 20+, Vite 6+, config updates
      └─ Fixes: all remaining vulnerabilities
```

## Production Impact Assessment

```
┌─────────────────────────────────┐
│   PRODUCTION RUNTIME            │
│   (Cloudflare Workers)          │
│                                 │
│   Dependencies:                 │
│   ✅ postal-mime (secure)       │
│                                 │
│   NOT included:                 │
│   ❌ esbuild                    │
│   ❌ vite                       │
│   ❌ vitest                     │
│   ❌ wrangler                   │
│                                 │
│   PRODUCTION RISK: ZERO         │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│   DEVELOPMENT ENVIRONMENT       │
│                                 │
│   Affected:                     │
│   ⚠️ npm run dev                │
│   ⚠️ npm test                   │
│   ⚠️ wrangler dev               │
│                                 │
│   DEVELOPMENT RISK: MODERATE    │
└─────────────────────────────────┘
```

## Recommended Action Plan

**Week 1: Wrangler Upgrade (LOW RISK)**
```bash
# 1. Upgrade wrangler
npm install --save-dev wrangler@4.48.0
npm install --save-dev @cloudflare/workers-types@4.20251113.0

# 2. Test deployment
npm run build
npm run deploy:staging

# 3. Verify functionality
wrangler dev
wrangler tail
```

**Week 2-3: Vitest Upgrade (MEDIUM RISK)**
```bash
# 1. Create feature branch
git checkout -b fix/upgrade-vitest

# 2. Upgrade vitest
npm install --save-dev vitest@4.0.8

# 3. Update configuration
# - Update vitest.config.ts
# - Check for API changes in test files

# 4. Run tests
npm test

# 5. Verify and merge
git commit -m "chore: upgrade vitest to v4.0.8"
```

## Testing Checklist

### After Wrangler Upgrade
- [ ] `npm run build` succeeds
- [ ] `npm run typecheck` passes
- [ ] `wrangler dev` starts successfully
- [ ] `wrangler deploy --dry-run` succeeds
- [ ] Deploy to staging environment
- [ ] Verify email routing works
- [ ] Verify SMS sending works
- [ ] Check KV namespace access
- [ ] Verify secrets are accessible

### After Vitest Upgrade
- [ ] `npm test` runs without errors
- [ ] All tests pass
- [ ] No deprecation warnings
- [ ] Coverage reports generate
- [ ] Test watch mode works
- [ ] Integration tests pass

## Risk Mitigation

**Rollback Plan:**
```bash
# If wrangler v4 fails
npm install --save-dev wrangler@3.114.15

# If vitest v4 fails
npm install --save-dev vitest@1.6.1
```

**Staging Environment:**
- Always test in staging first
- Use `--env staging` flag
- Keep production untouched until verified

**Version Pinning:**
```json
{
  "devDependencies": {
    "wrangler": "4.48.0",  // Pin exact version after successful test
    "vitest": "4.0.8"      // Pin exact version after successful test
  }
}
```

---

**Last Updated:** 2025-11-13
**Analyst:** Hive Mind Analyst Agent
**Status:** ✅ Analysis Complete
