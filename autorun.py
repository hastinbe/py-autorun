#!/usr/bin/env python
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
APP_GIT     = "http://github.com/hastinbe/py-autorun.git"
APP_NAME    = "Autorun"
APP_VERSION = "0.1.0-alpha"

# Standard Python imports.
import contextlib
import datetime
import subprocess
import time
import urllib2
import logging

# Log a message each time this module gets loaded.
logging.info('Loading %s, app version = %s', __name__, APP_VERSION)

# Application imports.
import settings

# 3rd party imports.
import psutil
from icalendar import Calendar

# --------------------------------------------------------------------------------------------------

class Autorun(object):
  """
  Provides an interface for executing applications under specified conditions.
  
  Public methods:
    start

  Protected methods:
    _has_internet
    _is_running
    _is_holiday
    _is_weekend

  Attributes:
    apps (dict) Applications to autorun.
    ical (str)  Path to an iCalendar file.
  """

  # Cached result of has_internet()
  _has_internet_result = False

  # Time in seconds the cached result expires
  _has_internet_expires = 60

  # Time in seconds since epoch that has_internet() was last called
  _has_internet_timeout = None

  def __init__ (self, apps, ical):
    """
    Create a new `Autorun` instance.

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
        if self._is_running(app):
          continue

      if params['conditions'].get('skip_if_holiday'):
        if self._is_holiday():
          continue

      if params['conditions'].get('skip_if_weekend'):
        if self._is_weekend():
          continue

      if params['conditions'].get('require_internet'):
        if not self._has_internet(settings.urls, settings.url_timeout):
          continue

      args = [params['path']]
      if not params['args'] is None:
        args.append(params['args'])

      subprocess.Popen(args)

  # ------------------------------------------------------------------------------------------------

  def _has_internet (self, urls, timeout=30):
    """
    Determine if there is an internet connection.
    
    The result is cached to prevent checking each URL for each application
    that has the require_internet condition set to `True`.

    Args:
      urls    (list) A list of URLs used to determine internet connectivity.
      timeout (int)  Optional time in seconds to block during the connection attempt. (default 30)

    Returns:
      (bool) `True`, if an internet connection is available, otherwise `False`.
    """

    if self._has_internet_timeout is None:
      self._has_internet_timeout = time.time()

    t = time.time()
    if t - self._has_internet_timeout > self._has_internet_expires:
      return self._has_internet_result

    try:
      for url in urls:
        with contextlib.closing(urllib2.urlopen(url, timeout=timeout)):
          self._has_internet_result = True
          self._has_internet_timeout = t
          return True
    except urllib2.URLError:
      pass

    self._has_internet_result = False
    self._has_internet_timeout = None
    return False

  # ------------------------------------------------------------------------------------------------

  def _is_running (self, app_name):
    """
    Check if `app_name` is running.

    Args:
      app_name (str) The name of the application.

    Returns:
      (bool) `True`, if application is running, otherwise `False`.
    """

    try:
      for proc in psutil.get_process_list():
        if proc.name == app_name:
          return True
    except:
      pass
    return False

  # ------------------------------------------------------------------------------------------------

  def _is_holiday (self, date=None):
    """
    Check if `date` is a US holiday.

    Args:
      date (datetime.date) Optional date. (default today's date)

    Returns:
      (bool) `True`, if date is a holiday, otherwise `False`.
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

  def _is_weekend (self, date=None):
    """
    Check if `date` is a weekend

    Args:
      date (datetime.date) Optional date. (default today's date)

    Returns:
      (bool) `True`, if date falls on a weekend, otherwise `False`.
    """

    if date is None:
      date = datetime.date.today()

    return date.isoweekday() > 5

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
  autorun = Autorun(settings.apps, settings.icalendar)
  autorun.start()