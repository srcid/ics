import sys
from pathlib import Path

import click

from ics.cal import Cal
from ics.event import Event, EventStatus
from ics.todo import Todo, TodoStatus


@click.group(chain=True)
@click.option(
  '--output',
  '-o',
  type=click.Path(path_type=Path, writable=True),
  help='Output ICS file. Defaults to stdout.',
)
@click.pass_context
def cli(ctx, output):
  """Generate an iCalendar file from events and todos."""
  ctx.ensure_object(dict)
  ctx.obj['output'] = output


@cli.command()
@click.option('--title', '-t', required=True)
@click.option('--start', required=True)
@click.option('--end')
@click.option('--duration')
@click.option('--description', '-d')
@click.option('--location', '-l')
@click.option('--url')
@click.option(
  '--status',
  type=click.Choice([s.value for s in EventStatus]),
  default=EventStatus.CONFIRMED.value,
)
@click.option('--category', 'categories', multiple=True)
def event(
  title, start, end, duration, description, location, url, status, categories
):
  """Add an event."""

  return Event(
    summary=title,
    dtstart=start,
    dtend=end,
    duration=duration,
    description=description,
    location=location,
    url=url,
    status=EventStatus(status),
    categories=list(categories),
  )


@cli.command()
@click.option('--title', '-t', required=True)
@click.option('--start')
@click.option('--due')
@click.option('--description', '-d')
@click.option('--location', '-l')
@click.option('--url')
@click.option(
  '--status',
  type=click.Choice([s.value for s in TodoStatus]),
  default=TodoStatus.NEEDS_ACTION.value,
)
@click.option('--priority', type=click.IntRange(0, 9))
@click.option('--category', 'categories', multiple=True)
def todo(
  title, start, due, description, location, url, status, priority, categories
):
  """Add a todo."""

  return Todo(
    summary=title,
    dtstart=start,
    due=due,
    description=description,
    location=location,
    url=url,
    status=TodoStatus(status),
    priority=priority,
    categories=list(categories),
  )


@cli.result_callback()
@click.pass_context
def finish(ctx, results, **kwargs):
  """Generate and output the calendar."""

  cal = Cal(
    events=[item for item in results if isinstance(item, Event)],
    todos=[item for item in results if isinstance(item, Todo)],
  )

  content = str(cal)
  output = ctx.obj['output']

  if output:
    output.write_text(content, encoding='utf-8', newline='')
  else:
    sys.stdout.write(content)


if __name__ == '__main__':
  cli()
