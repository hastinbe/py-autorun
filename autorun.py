#! /usr/bin/env python
#
#  Autorun
#
#  Autorun is a script designed to run programs based on conditions that you might not found
#  in many task schedulers.
#
#  Why? I wanted to autorun my work applications on system startup, but couldn't configure
#  any software to skip holidays and weekends, or days where people usually don't have work.
#
#  Copyright (c) 2012 Beau Hastings. All rights reserved.
#  License: GNU GPL version 2, see LICENSE for more details.
#
#  Author: Beau Hastings <beausy@gmail.com>

APP_AUTHOR  = "Beau Hastings"
APP_EMAIL   = "beausy@gmail.com"
APP_GIT     = "http://github.com/hastinbe/autorun.git"
APP_NAME    = "Autorun"
APP_VERSION = "0.1.0-alpha"

import datetime
import subprocess

import settings

import psutil
from icalendar import Calendar

# --------------------------------------------------------------------------------------------------

class Autorun(object):
  """
  Provides an interface for executing applications under specified conditions.

  Attributes:
    apps (dict) Applications to autorun.
    ical (str)  Path to an iCalendar file.
  """

  def __init__ (self, apps, ical):
    """
    Create a new Autorun instance.

    Args:
      apps (dict) Applications to autorun.
      ical (str)  Path to an iCalendar file.
    """

    self.apps = apps
    self.ical = ical

  # ------------------------------------------------------------------------------------------------

  def start (self):
    """
    Executes autostart applications in the background.
    """

    for app, params in self.apps.iteritems():
      if params['conditions'].get('skip_if_running'):
        if self.is_running(app):
          continue

      if params['conditions'].get('skip_if_holiday'):
        if self.is_holiday():
          continue

      if params['conditions'].get('skip_if_weekend'):
        if self.is_weekend():
          continue

      args = [params['path']]
      if not params['args'] is None:
        args.append(params['args'])

      subprocess.Popen(args)

  # ------------------------------------------------------------------------------------------------

  def is_running (self, app_name):
    """
    Check if an application is running.

    Args:
      app_name (str) The name of the application.

    Returns:
      (bool) True, if application is running, otherwise False.
    """

    try:
      for proc in psutil.get_process_list():
        if proc.name == app_name:
          return True
    except:
      pass
    return False

  # ------------------------------------------------------------------------------------------------

  def is_holiday (self, date=None):
    """
    Check if date is a US holiday.

    Args:
      date (datetime.date) The date

    Returns:
      (bool) True, if date is a holiday, otherwise False.
    """

    if date is None:
      date = datetime.date.today()

    calendar = Calendar.from_ical(open(self.ical, 'rb').read())
    holidays = [e['dtstart'] for e in calendar.walk('VEVENT')]
    date_str = date.strftime('%Y%m%d')

    for holiday in holidays:
      if holiday.to_ical() == date_str:
        return True
    return False

  # ------------------------------------------------------------------------------------------------

  def is_weekend (self, date=None):
    """
    Check if date is a weekend

    Args:
      date (datetime.date) The date.

    Returns:
      (bool) True, if date falls on a weekend, otherwise False.
    """

    if date is None:
      date = datetime.date.today()

    return date.isoweekday() > 5

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
  autorun = Autorun(settings.apps, settings.icalendar)
  autorun.start()