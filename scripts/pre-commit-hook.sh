#!/usr/bin/env bash
# HARD RULE: Block commits with real personal data
# JOBS OS — Lily Edition

BLOCKED_FILES=("local_config.json")
STAGED=$(git diff --cached --name-only)

for f in "${BLOCKED_FILES[@]}"; do
    STATUS=$(git diff --cached -- "$f")
    # Allow deletion (removing from tracking is OK)
    if echo "$STATUS" | grep -q "^deleted"; then
        continue
    fi
    if echo "$STAGED" | grep -q "$f"; then
        echo "❌ BLOCKED: '$f' contains real personal data. Remove with:"
        echo "   git rm --cached $f"
        echo "   echo '$f' >> .gitignore"
        exit 1
    fi
done

# Check for real phone patterns (Canadian numbers) in staged files
if echo "$STAGED" | grep -v "^OUTPUT/" | grep -v "\.gitignore" | grep -v "LOCAL_GENERATOR.py" | xargs -I{} sh -c '
    git diff --cached "{}" 2>/dev/null | grep -E "\+1[[:space:]]*[0-9]{3}[[:space:]]*[0-9]{3}[[:space:]]*[0-9]{4}"
' | grep -q .; then
    echo "❌ BLOCKED: Real phone number detected in staged files."
    echo "   Use [PHONE] placeholder instead."
    exit 1
fi

# Check for real email patterns in staged files
if echo "$STAGED" | grep -v "^OUTPUT/" | xargs -I{} sh -c '
    git diff --cached "{}" 2>/dev/null | grep -E "@gmail\.com|@hotmail\.com|@outlook\.com|@yahoo\.com"
' | grep -q .; then
    echo "❌ BLOCKED: Real email detected in staged files."
    echo "   Use [EMAIL] placeholder instead."
    exit 1
fi

exit 0
