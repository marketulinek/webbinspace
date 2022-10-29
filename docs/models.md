# UML Class Diagram
### for models:

```mermaid
classDiagram
    class Report{
      package_number: str
      date_code: int
      cycle: int
      created_at: DateTime
      __str__()
      get_absolute_url()
      get_path_to_file()
      file_name()
    }
    class Category{
      name: str
      __str__()
      get_absolute_url()
    }
    class Visit{
      visit_id: str
      pcs_mode: str
      visit_type: str
      scheduled_start_time: DateTime
      duration: Duration
      science_instrument_and_mode: str
      instrument: tuple
      target_name: str
      keywords: str
      valid: bool
      __str__()
    }
    Report "1" *-- "*" Visit
    Category "0..1" o-- "*" Visit
```
