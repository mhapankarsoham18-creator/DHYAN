# Disaster Recovery & Backups

To ensure the safety of the Dhyan production environment, we rely on Supabase's fully managed automated backup and recovery solutions.

## Point-in-Time Recovery (PITR)

For full disaster recovery capability (e.g. recovering from catastrophic data loss, accidental database deletions, or corrupted broker tokens), **Point-in-Time Recovery (PITR)** must be enabled on the production database.

### Enabling PITR
1. Open the [Supabase Dashboard](https://supabase.com/dashboard).
2. Navigate to your production project: `Dhyan-Prod`.
3. Go to **Database** -> **Backups**.
4. Click on **Enable Point-in-Time Recovery**.
   *Note: This requires a Pro plan or higher and specifically the PITR add-on.*
5. Ensure the retention policy is set to the maximum available for your tier (usually 7 days or 28 days).

### Restoring Data
If a disastrous event occurs:
1. Navigate to the **Backups** tab in the Supabase Dashboard.
2. Select the exact date and minute prior to the incident.
3. Click **Restore**. Note that the database will be momentarily unavailable while the recovery is finalized.

## Sentry Log Retention
Ensure Sentry crash data retention is securely masked. We have enabled custom log masking in both the Python Backend and Flutter App (`sentry_masking.dart` & `logging_setup.py`) to scrub PAN numbers, passwords, and connection tokens prior to leaving your infrastructure.
