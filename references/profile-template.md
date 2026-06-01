# 用户基础信息档案模板

真实档案保存为 `~/cow/fitness_coach/profile.md`。本文件只是模板，不保存用户真实数据。

## Frontmatter

```yaml
---
schema_version: 1
initialized: false
created_at: "ISO-8601"
updated_at: "ISO-8601"
record_id: "profile"
source: "fitness-coach-skill"
---
```

## 结构化数据

```json payload
{
  "identity": {
    "nickname": "unknown",
    "age_or_birth_year": "unknown",
    "sex": "unknown"
  },
  "body": {
    "height_cm": "unknown",
    "current_weight_kg": "unknown",
    "start_weight_kg": "unknown",
    "target_weight_kg": "unknown"
  },
  "goals": {
    "primary": "unknown",
    "deadline": "unknown",
    "priority": "unknown",
    "acceptable_rate": "unknown"
  },
  "training": {
    "experience": "unknown",
    "level": "unknown",
    "available_days_per_week": "unknown",
    "session_minutes": "unknown",
    "equipment": "unknown",
    "current_program": "unknown",
    "preferences": "unknown"
  },
  "nutrition": {
    "goal": "unknown",
    "allergies": "unknown",
    "restrictions": "unknown",
    "dislikes": "unknown",
    "favorite_foods": "unknown",
    "cooking_skill": "unknown",
    "budget": "unknown",
    "eating_out_frequency": "unknown"
  },
  "lifestyle": {
    "sleep": "unknown",
    "activity": "unknown",
    "stress": "unknown",
    "high_risk_periods": "unknown"
  },
  "health": {
    "conditions": "unknown",
    "medications": "unknown",
    "injuries_or_limitations": "unknown",
    "medical_constraints": "unknown"
  },
  "coach_notes": [],
  "custom": {}
}
```

核心字段齐全后才可把 `initialized` 设为 `true`：主要目标、性别或年龄、身高体重、训练经验、每周训练时间、饮食过敏/限制、伤病或医疗限制。
