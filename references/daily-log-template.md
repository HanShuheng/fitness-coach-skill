# 每日记录模板

真实记录默认保存为 `$COW_WORKSPACE/fitness_coach/data/daily/YYYY-MM-DD.md`。本文件只是模板。

## Frontmatter

```yaml
---
schema_version: 1
initialized: true
created_at: "ISO-8601"
updated_at: "ISO-8601"
record_id: "daily-YYYY-MM-DD"
source: "fitness-coach-skill"
---
```

## 结构化数据

```json payload
{
  "body": {
    "weight_kg": null,
    "waist_cm": null,
    "body_fat_percent": null
  },
  "nutrition": {
    "summary": "",
    "meals": [],
    "calories": null,
    "protein_g": null,
    "carbs_g": null,
    "fat_g": null,
    "water_l": null
  },
  "training": {
    "status": "",
    "session": "",
    "exercises": [],
    "steps": null,
    "cardio": ""
  },
  "recovery": {
    "sleep_hours": null,
    "mood": "",
    "energy": "",
    "stress": "",
    "hunger": "",
    "pain": ""
  },
  "coach_notes": "",
  "custom": {}
}
```

默认每日必填：体重、饮食概要或餐食记录、训练状态、睡眠小时数、心情或精力。
