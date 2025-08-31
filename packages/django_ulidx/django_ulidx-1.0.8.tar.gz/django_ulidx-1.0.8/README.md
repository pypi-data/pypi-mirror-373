# Django ULIDX

Django IDX is a Django extension which allows developers to use alternative sequential IDs like ULID as ID.

## Usage

```python
from django.db import models
from django_ulidx.models import ULIDField


class MyModel(models.Model):
	id = ULIDField(primary_key=True)
```
