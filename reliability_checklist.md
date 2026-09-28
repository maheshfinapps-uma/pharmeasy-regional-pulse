# Reliability Checklist

## 1. Safety

Do not turn an operational movement flag into a causal claim. Treat the 8% threshold as an alerting rule, not a statistical significance test. [HIGH]

## 2. Validation

Validate schema, missing values, duplicate handling, region normalization, SQL joins, distinct order counts, and monthly sales before interpretation. [HIGH]

## 3. Critique and Refine

Challenge the headline movement, distinguish verified facts from unverified causes, and use order/category detail to test alternative explanations. [MEDIUM]

## 4. Human Sign-off

Only an approved report may proceed to downstream or external use; review decisions are recorded in `audit_log.jsonl`. [HIGH]
