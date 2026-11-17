from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class TodoStatus(str, Enum):
  NEEDS_ACTION = 'NEEDS-ACTION'
  IN_PROCESS = 'IN-PROCESS'
  COMPLETED = 'COMPLETED'
  CANCELLED = 'CANCELLED'


class TodoClassification(str, Enum):
  PUBLIC = 'PUBLIC'
  PRIVATE = 'PRIVATE'
  CONFIDENTIAL = 'CONFIDENTIAL'


@dataclass
class Todo:
  uid: str = field(default_factory=lambda: str(uuid4()))
  dtstamp: str = field(
    default_factory=lambda: datetime.now(timezone.utc).strftime(
      '%Y%m%dT%H%M%SZ'
    )
  )

  dtstart: str | None = None
  due: str | None = None
  duration: str | None = None
  completed: str | None = None

  summary: str | None = None
  description: str | None = None
  location: str | None = None
  url: str | None = None

  status: TodoStatus = TodoStatus.NEEDS_ACTION
  classification: TodoClassification = TodoClassification.PUBLIC

  percent_complete: int | None = None
  priority: int | None = None

  categories: list[str] = field(default_factory=list)
  geo: str | None = None

  organizer: str | None = None
  attendees: list[str] = field(default_factory=list)

  rrule: str | None = None
  rdate: list[str] = field(default_factory=list)
  exdate: list[str] = field(default_factory=list)

  related_to: list[str] = field(default_factory=list)

  @classmethod
  def from_dict(cls, data: dict):
    defaults = {
      'uid': str(uuid4()),
      'dtstamp': datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
      'status': TodoStatus.NEEDS_ACTION,
      'classification': TodoClassification.PUBLIC,
      'categories': [],
      'attendees': [],
      'rdate': [],
      'exdate': [],
      'related_to': [],
    }

    values = defaults | data.copy()

    if 'class' in values:
      values['classification'] = values.pop('class')

    enum_fields = {
      'status': TodoStatus,
      'classification': TodoClassification,
    }

    for name, enum_type in enum_fields.items():
      if name in values:
        values[name] = enum_type(values[name])

    valid_fields = {f.name for f in fields(cls)}
    unknown = values.keys() - valid_fields

    if unknown:
      raise TypeError(f'Unexpected fields: {", ".join(unknown)}')

    return cls(**values)

  def __str__(self):
    properties = [
      ('UID', self.uid),
      ('DTSTAMP', self.dtstamp),
      ('DTSTART', self.dtstart),
      ('DUE', self.due),
      ('DURATION', self.duration),
      ('COMPLETED', self.completed),
      ('SUMMARY', self.summary),
      ('DESCRIPTION', self.description),
      ('LOCATION', self.location),
      ('URL', self.url),
      ('STATUS', self.status.value),
      ('CLASS', self.classification.value),
      ('PERCENT-COMPLETE', self.percent_complete),
      ('PRIORITY', self.priority),
      ('CATEGORIES', ','.join(self.categories)),
      ('GEO', self.geo),
      ('ORGANIZER', self.organizer),
      *[('ATTENDEE', value) for value in self.attendees],
      ('RRULE', self.rrule),
      *[('RDATE', value) for value in self.rdate],
      *[('EXDATE', value) for value in self.exdate],
      *[('RELATED-TO', value) for value in self.related_to],
    ]

    lines = ['BEGIN:VTODO']

    for name, value in properties:
      if value is not None:
        lines.append(f'{name}:{value}')

    lines.append('END:VTODO')

    return '\r\n'.join(lines)
