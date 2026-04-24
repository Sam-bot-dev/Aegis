# This folder holds local development secrets:
#   - service-account.json       (Google Cloud service account key)
#   - firebase-adminsdk.json     (Firebase Admin SDK key)
#
# Both are gitignored. See SETUP.md Part 3 and Part 4 for how to generate them.
#
# NEVER commit anything in this folder. If you think a key leaked,
# rotate it immediately:
#   gcloud iam service-accounts keys list --iam-account=<sa-email>
#   gcloud iam service-accounts keys delete <KEY_ID> --iam-account=<sa-email>
