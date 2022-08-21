# UML Class Diagram
### for models:

```mermaid
classDiagram
    class Report{
      package_number: int
      date_code: int
      cycle: int
      created_at: DateTime
    }
    class Category{
      name: str
    }
    class Visit{
      visit_id: str
      pcs_mode: str
      visit_type: str
      scheduled_start_time: DateTime
      duration: DateTime
      science_instrument_and_mode: str
      target_name: str
      keywords: str
    }
    Report "1" *-- "*" Visit
    Category "0..1" o-- "*" Visit
```
