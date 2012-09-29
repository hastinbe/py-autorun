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

class Autorun:

  def __init__ (self, apps, icalendar):
    """
    Create a new Autorun instance.

    @param apps      (dict) Applications to autorun.
    @param icalendar (str)  Path to an iCalendar file.
    """

    self.apps = apps
    self.icalendar = icalendar

  # ------------------------------------------------------------------------------------------------

  def start (self):
    """
    Executes autostart applications in the background.
    """

    for app, params in self.apps.iteritems():
      if 'skip_if_running' in params['conditions']:
        if params['conditions']['skip_if_running']:
          if self.is_running(app):
            continue

      if 'skip_if_holiday' in params['conditions']:
        if params['conditions']['skip_if_holiday']:
          if self.is_holiday():
            continue;

      if 'skip_if_weekend' in params['conditions']:
        if params['conditions']['skip_if_weekend']:
          if self.is_weekend():
            continue

      args = [params['path']]
      if not params['args'] is None:
        args.append(params['args'])

      params['pid'] = subprocess.Popen(args).pid

  # ------------------------------------------------------------------------------------------------

  def is_running (self, app_name):
    """
    Check if an application is running.

    @param app_name (str) The name of the application.

    @return (bool) True, if application is running, otherwise False.
    """

    for proc in psutil.get_process_list():
      if proc.name == app_name:
        return True
    return False

  # ------------------------------------------------------------------------------------------------

  def is_holiday (self, date=None):
    """
    Check if date is a US holiday.

    @param date (str) A date in YYYYMMDD format.

    @return (bool) True, if date is a holiday, otherwise False.
    """

    if date is None:
      date = datetime.date.today().strftime('%Y%m%d')

    calendar = Calendar.from_ical(open(self.icalendar, 'rb').read())
    holidays = [i['dtstart'] for i in calendar.walk('VEVENT')]

    for holiday in holidays:
      if holiday.to_ical() == date:
        return True
    return False

  # ------------------------------------------------------------------------------------------------

  def is_weekend (self, date=None):
    """
    Check if date is a weekend

    @param date (datetime.date) The date.

    @return (bool) True, if date falls on a weekend, otherwise False.
    """

    if date is None:
      date = datetime.date.today()

    return date.isoweekday() > 5

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
  autorun = Autorun(settings.apps, settings.icalendar)
  autorun.start()