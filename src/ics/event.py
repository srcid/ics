from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class EventStatus(str, Enum):
  TENTATIVE = 'TENTATIVE'
  CONFIRMED = 'CONFIRMED'
  CANCELLED = 'CANCELLED'


class Transparency(str, Enum):
  OPAQUE = 'OPAQUE'
  TRANSPARENT = 'TRANSPARENT'


class Classification(str, Enum):
  PUBLIC = 'PUBLIC'
  PRIVATE = 'PRIVATE'
  CONFIDENTIAL = 'CONFIDENTIAL'


@dataclass
class Event:
  uid: str = field(default_factory=lambda: str(uuid4()))
  dtstamp: str = field(
    default_factory=lambda: datetime.now(timezone.utc).strftime(
      '%Y%m%dT%H%M%SZ'
    )
  )

  dtstart: str | None = None
  dtend: str | None = None
  duration: str | None = None

  summary: str | None = None
  description: str | None = None
  location: str | None = None
  url: str | None = None

  status: EventStatus = EventStatus.CONFIRMED
  transp: Transparency = Transparency.OPAQUE
  classification: Classification = Classification.PUBLIC

  categories: list[str] = field(default_factory=list)
  priority: int | None = None
  geo: str | None = None

  organizer: str | None = None
  attendees: list[str] = field(default_factory=list)

  rrule: str | None = None
  rdate: list[str] = field(default_factory=list)
  exdate: list[str] = field(default_factory=list)

  @classmethod
  def from_dict(cls, data: dict):
    defaults = {
      'uid': str(uuid4()),
      'dtstamp': datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
      'status': EventStatus.CONFIRMED,
      'transp': Transparency.OPAQUE,
      'classification': Classification.PUBLIC,
      'categories': [],
      'attendees': [],
      'rdate': [],
      'exdate': [],
    }

    values = defaults | data.copy()

    if 'class' in values:
      values['classification'] = values.pop('class')

    enum_fields = {
      'status': EventStatus,
      'transp': Transparency,
      'classification': Classification,
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
      ('DTEND', self.dtend),
      ('DURATION', self.duration),
      ('SUMMARY', self.summary),
      ('DESCRIPTION', self.description),
      ('LOCATION', self.location),
      ('URL', self.url),
      ('STATUS', self.status.value),
      ('TRANSP', self.transp.value),
      ('CLASS', self.classification.value),
      ('CATEGORIES', ','.join(self.categories)),
      ('PRIORITY', self.priority),
      ('GEO', self.geo),
      ('ORGANIZER', self.organizer),
      *[('ATTENDEE', value) for value in self.attendees],
      ('RRULE', self.rrule),
      *[('RDATE', value) for value in self.rdate],
      *[('EXDATE', value) for value in self.exdate],
    ]

    lines = ['BEGIN:VEVENT']

    for name, value in properties:
      if value is not None:
        lines.append(f'{name}:{value}')

    lines.append('END:VEVENT')

    return '\r\n'.join(lines)
