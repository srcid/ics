from dataclasses import dataclass, field, fields

from ics import __maintainer__, __project_name__, __version__

from .event import Event
from .todo import Todo


@dataclass
class Cal:
  prodid: str = f'-//{__maintainer__}//{__project_name__} {__version__}//EN'
  version: str = '2.0'
  calscale: str = 'GREGORIAN'

  method: str | None = None
  name: str | None = None
  description: str | None = None

  events: list[Event] = field(default_factory=list)
  todos: list[Todo] = field(default_factory=list)

  @classmethod
  def from_dict(cls, data: dict):
    defaults = {
      'prodid': '-//Python//iCalendar//EN',
      'version': '2.0',
      'calscale': 'GREGORIAN',
      'events': [],
      'todos': [],
    }

    values = defaults | data.copy()

    valid_fields = {f.name for f in fields(cls)}
    unknown = values.keys() - valid_fields

    if unknown:
      raise TypeError(f'Unexpected fields: {", ".join(unknown)}')

    values['events'] = [
      Event.from_dict(item) if isinstance(item, dict) else item
      for item in values['events']
    ]

    values['todos'] = [
      Todo.from_dict(item) if isinstance(item, dict) else item
      for item in values['todos']
    ]

    if not all(isinstance(item, Event) for item in values['events']):
      raise TypeError('events must contain Event instances')

    if not all(isinstance(item, Todo) for item in values['todos']):
      raise TypeError('todos must contain Todo instances')

    return cls(**values)

  def __str__(self):
    properties = [
      ('VERSION', self.version),
      ('PRODID', self.prodid),
      ('CALSCALE', self.calscale),
      ('METHOD', self.method),
      ('NAME', self.name),
      ('DESCRIPTION', self.description),
    ]

    lines = ['BEGIN:VCALENDAR']

    for name, value in properties:
      if value is not None:
        lines.append(f'{name}:{value}')

    for event in self.events:
      lines.extend(str(event).splitlines())

    for todo in self.todos:
      lines.extend(str(todo).splitlines())

    lines.append('END:VCALENDAR')

    return '\r\n'.join(lines) + '\r\n'
