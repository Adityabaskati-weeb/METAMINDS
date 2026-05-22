# Demo Mode

Demo mode exists to prove one believable operational workflow:

1. Seed benign baseline.
2. Complete one live PayEasy/Razorpay test payment.
3. Show trust-state transition and typed evidence.
4. Show queue update and Telegram alert.
5. Open Trust Replay.

## Hard Rules

- Run only from `C:\Projects\Rayzaa`.
- Do not run replay before the live payment.
- Do not reuse a dirty demo database.
- Do not allow lazy model retraining during the judge flow.

## Startup

```powershell
cd C:\Projects\Rayzaa
.\scripts\start_demo.ps1
```

`start_demo.ps1` now:

- resets the demo DB
- validates and prewarms the locked model bundle
- runs a bounded frontend build
- starts the API and frontend
- seeds the benign PayEasy baseline

## Replay Sequence

Open Trust Replay only after:

- one live payment has reached the queue
- the Evidence Lens shows the typed evidence update
- Telegram has either delivered or truthfully reported its fallback state

## Fallback

If Razorpay is unavailable:

- do not fake a payment
- use the seeded baseline plus deterministic replay
- state clearly that the live payment path is unavailable in this environment
