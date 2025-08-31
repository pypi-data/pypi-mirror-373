#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Generate test file for Pygenda
#
# Copyright (C) 2022-2025 Matthew Lewis
#
# This file is part of Pygenda.
#
# Pygenda is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# Pygenda is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pygenda. If not, see <https://www.gnu.org/licenses/>.
#

from datetime import datetime,timedelta, date as dt_date
from argparse import ArgumentParser


YEAR = datetime.now().year
STAMPDATE = '{}0101T000000'.format(YEAR)
MAX_LINE_BYTES = 74
uid = 1234567
uid_gp = None


#
# Globals used to create events this year
#
Jan01 = dt_date(YEAR, 1, 1)
day_offset = Jan01.weekday() # 0=Mon, 1=Tue...
Mar01 = dt_date(YEAR, 3, 1)
day_offset2 = Mar01.weekday() # 0=Mon, 1=Tue...


def print_stamp_uid():
    global uid, uid_gp
    print('DTSTAMP;VALUE=DATE-TIME:{}Z'.format(STAMPDATE), end='\r\n')
    if uid_gp is None:
        print('UID:Pygenda-{:08d}'.format(uid), end='\r\n')
    else:
        print('UID:Pygenda-{:05d}-{:08d}'.format(uid_gp,uid), end='\r\n')
    uid += 1


def start_uid_group(gp:int):
    global uid, uid_gp
    uid = 1234567
    uid_gp = gp


def print_vevent(desc, date, time=None, endtime=None, daycount=None, repeat=None, interval=1, repeat_count=None, bymonthday=None, status=None, anniv=False):
    if isinstance(date, str):
        date = datetime.strptime(date,'%Y-%m-%d').date()
    print('BEGIN:VEVENT', end='\r\n')
    summary = 'SUMMARY:{:s}'.format(escape_str(desc))
    print(summary[:MAX_LINE_BYTES], end='\r\n')
    for i in range(MAX_LINE_BYTES,len(summary), MAX_LINE_BYTES-1):
        print(' ' + summary[i:i+MAX_LINE_BYTES-1], end='\r\n')
    if time is not None:
        if isinstance(time, str):
            time = datetime.strptime(time,'%H:%M').time()
        print('DTSTART;VALUE=DATE-TIME:{:04d}{:02d}{:02d}T{:02d}{:02d}{:02d}'.format(date.year, date.month, date.day, time.hour, time.minute, time.second), end='\r\n')
        if endtime is not None:
            if isinstance(endtime, str):
                endtime = datetime.strptime(endtime,'%H:%M').time()
            print('DTEND;VALUE=DATE-TIME:{:04d}{:02d}{:02d}T{:02d}{:02d}{:02d}'.format(date.year, date.month, date.day, endtime.hour, endtime.minute, endtime.second), end='\r\n')
    else:
        print('DTSTART;VALUE=DATE:{:04d}{:02d}{:02d}'.format(date.year, date.month, date.day), end='\r\n')
        if daycount is not None:
            enddate = date+timedelta(days=daycount)
            print('DTEND;VALUE=DATE:{:04d}{:02d}{:02d}'.format(enddate.year, enddate.month, enddate.day), end='\r\n')
    print_stamp_uid()
    if repeat=='YEARLY':
        print('RRULE:FREQ=YEARLY{:s}{:s}{:s}'.format(
            '' if interval==1 else ';INTERVAL={:d}'.format(interval),
            '' if bymonthday is None else ';BYMONTH={:d};BYDAY={:s}'.format(bymonthday[0],bymonthday[1]),
            '' if repeat_count is None else ';COUNT={:d}'.format(repeat_count)
            ), end='\r\n')
    elif repeat=='WEEKLY':
        print('RRULE:FREQ=WEEKLY{:s}{:s}'.format(
            '' if interval==1 else ';INTERVAL={:d}'.format(interval),
            '' if repeat_count is None else ';COUNT={:d}'.format(repeat_count)
            ), end='\r\n')
    elif repeat=='MONTHLY':
        print('RRULE:FREQ=MONTHLY{:s}{:s}{:s}'.format(
            '' if interval==1 else ';INTERVAL={:d}'.format(interval),
            '' if bymonthday is None else ';BYDAY={:s}'.format(bymonthday),
            '' if repeat_count is None else ';COUNT={:d}'.format(repeat_count)
            ), end='\r\n')
    if anniv:
        print('X-PYGENDA-ANNIVERSARY;VALUE=BOOLEAN:TRUE', end='\r\n')
        #print('X-EPOCAGENDAENTRYTYPE:ANNIVERSARY', end='\r\n')
        if isinstance(anniv, str):
            print('X-PYGENDA-ANNIVERSARY-SHOW:'+anniv, end='\r\n')
    if status is not None:
        print('STATUS:{:s}'.format(status.upper()), end='\r\n')
    print('END:VEVENT', end='\r\n')


def print_vtodo(desc, cat=None, priority=None, status=None, duedate=None):
    print('BEGIN:VTODO', end='\r\n')
    summary = 'SUMMARY:{:s}'.format(escape_str(desc))
    print(summary[:MAX_LINE_BYTES], end='\r\n')
    for i in range(MAX_LINE_BYTES,len(summary), MAX_LINE_BYTES-1):
        print(' ' + summary[i:i+MAX_LINE_BYTES-1], end='\r\n')
    if cat is not None:
        print('CATEGORIES:{:s}'.format(cat), end='\r\n')
    if priority is not None:
        print('PRIORITY:{:d}'.format(priority), end='\r\n')
    if status is not None:
        print('STATUS:{:s}'.format(status), end='\r\n')
    if duedate is not None:
        if isinstance(duedate, str):
            duedate = datetime.strptime(duedate,'%Y-%m-%d')
        print('DUE;VALUE=DATE:{:04d}{:02d}{:02d}'.format(duedate.year, duedate.month, duedate.day), end='\r\n')
    print_stamp_uid()
    print('END:VTODO', end='\r\n')


def escape_str(st):
    st = st.replace('\\', r'\\')
    st = st.replace(',', '\,')
    st = st.replace(';', '\;')
    return st


def print_daylight_saving_changes():
    start_uid_group(2388)
    print_vevent('Clocks go forward (Europe)', '2000-03-26', time='1:00', repeat='YEARLY', bymonthday=[3,'-1SU'])
    print_vevent('Clocks go back (Europe)', '2000-10-29', time='1:00', repeat='YEARLY', bymonthday=[10,'-1SU'])
    print_vevent('Clocks go forward (USA)', '2000-03-12', time='2:00', repeat='YEARLY', bymonthday=[3,'2SU'])
    print_vevent('Clocks go back (USA)', '2000-11-05', time='2:00', repeat='YEARLY', bymonthday=[11,'1SU'])


def print_holidays():
    # Anniversaries and various yearly events
    start_uid_group(12322)
    print_vevent('New Year', '0001-01-01', repeat='YEARLY', daycount=1)
    print_vevent('Christmas!', '0001-12-25', repeat='YEARLY', daycount=1)
    print_vevent('Christmas Eve', '0001-12-24', repeat='YEARLY', daycount=1)
    print_vevent('Boxing Day', '0001-12-26', repeat='YEARLY', daycount=1)
    print_vevent('Bonfire Night', '2000-11-05', repeat='YEARLY', daycount=1)
    print_vevent('Halloween', '2000-10-31', repeat='YEARLY', daycount=1)
    print_vevent('Valentine\'s Day', '2000-02-14', repeat='YEARLY', daycount=1)
    print_vevent('Armistice Day', '1918-11-11', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('VE Day', '1945-05-08', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('VJ Day', '1945-08-15', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('May Day', '2000-05-01', repeat='YEARLY', daycount=1)
    print_vevent('May Day bank holiday (UK)', '2000-05-01', repeat='YEARLY', bymonthday=[5,'1MO'], daycount=1)
    print_vevent('Spring bank holiday (UK)', '2000-05-29', repeat='YEARLY', bymonthday=[5,'-1MO'], daycount=1)
    print_vevent('Summer bank holiday (UK)', '2000-08-28', repeat='YEARLY', bymonthday=[8,'-1MO'], daycount=1)
    print_vevent('April Fools\' Day', '2000-04-01', repeat='YEARLY', daycount=1)
    print_vevent('Burns\' Night', '1759-01-25', repeat='YEARLY', daycount=1)
    print_vevent('St Patrick\'s Day', '2000-03-17', repeat='YEARLY', daycount=1)
    print_vevent('St George\'s Day', '0303-04-23', repeat='YEARLY', daycount=1, anniv='NONE')
    print_vevent('St Andrew\'s Day', '2000-11-30', repeat='YEARLY', daycount=1)
    print_vevent('St David\'s Day', '0589-03-01', repeat='YEARLY', daycount=1, anniv='NONE')
    print_vevent('Independence Day (USA)', '1776-07-04', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Thanksgiving (USA)', '1942-11-26', repeat='YEARLY', bymonthday=[11,'4TH'], daycount=1)
    print_vevent('Canada Day', '1867-07-01', repeat='YEARLY', daycount=1)
    print_vevent('Thanksgiving (Canada)', '1957-10-14', repeat='YEARLY', bymonthday=[10,'2MO'], daycount=1)
    print_vevent('Australia Day', '1994-01-26', repeat='YEARLY', daycount=1)
    print_vevent('Waitangi Day (NZ)', '1947-02-06', repeat='YEARLY', daycount=1)
    print_vevent('Fête nationale française (Bastille Day)', '1880-07-14', repeat='YEARLY', daycount=1)
    print_vevent('Mother\'s Day (USA)', '2000-05-14', repeat='YEARLY', bymonthday=[5,'2SU'], daycount=1)
    print_vevent('Father\'s Day', '2000-06-18', repeat='YEARLY', bymonthday=[6,'3SU'], daycount=1)
    print_vevent('Winter Solstice (northern hemisphere)', '0001-12-21', repeat='YEARLY', daycount=1)
    print_vevent('Summer Solstice (northern hemisphere)', '0001-06-21', repeat='YEARLY', daycount=1)
    print_vevent('New Year\'s Eve', '0001-12-31', repeat='YEARLY', daycount=1)

    # Easter & related dates
    EASTER_DATES = ('1990-04-15','1991-03-31','1992-04-19','1993-04-11','1994-04-03','1995-04-16','1996-04-07','1997-03-30','1998-04-12','1999-04-04','2000-04-23','2001-04-15','2002-03-31','2003-04-20','2004-04-11','2005-03-27','2006-04-16','2007-04-08','2008-03-23','2009-04-12','2010-04-04','2011-04-24','2012-04-08','2013-03-31','2014-04-20','2015-04-05','2016-03-27','2017-04-16','2018-04-01','2019-04-21','2020-04-12','2021-04-04','2022-04-17','2023-04-09','2024-03-31','2025-04-20','2026-04-05','2027-03-28','2028-04-16','2029-04-01','2030-04-21','2031-04-13','2032-03-28','2033-04-17','2034-04-09','2035-03-25','2036-04-13','2037-04-05','2038-04-25','2039-04-10','2040-04-01','2041-04-21','2042-04-06','2043-03-29','2044-04-17','2045-04-09','2046-03-25','2047-04-14','2048-04-05','2049-04-18','2050-04-10')
    for easter_date in EASTER_DATES:
        edt = datetime.strptime(easter_date,'%Y-%m-%d').date()
        print_vevent('Good Friday', edt-timedelta(days=2), daycount=1)
        print_vevent('Easter', edt, daycount=1)
        print_vevent('Easter Monday', edt+timedelta(days=1), daycount=1)
        print_vevent('Shrove Tuesday', edt-timedelta(days=47), daycount=1)
        print_vevent('Mothering Sunday (UK)', edt-timedelta(days=21), daycount=1)


def print_moon_phases():
    # Full moon (note dates given here are for UTC, so don't use outside of testing)
    FULLMOON_DATES =(
        '2020-01-10','2020-02-09','2020-03-09','2020-04-08','2020-05-07','2020-06-05','2020-07-05','2020-08-03','2020-09-02','2020-10-01','2020-10-31','2020-11-30','2020-12-30',
        '2021-01-28','2021-02-27','2021-03-28','2021-04-27','2021-05-26','2021-06-24','2021-07-24','2021-08-22','2021-09-20','2021-10-20','2021-11-19','2021-12-19',
        '2022-01-17','2022-02-16','2022-03-18','2022-04-16','2022-05-16','2022-06-14','2022-07-13','2022-08-12','2022-09-10','2022-10-09','2022-11-08','2022-12-08',
        '2023-01-06','2023-02-05','2023-03-07','2023-04-06','2023-05-05','2023-06-04','2023-07-03','2023-08-01','2023-08-31','2023-09-29','2023-10-28','2023-11-27','2023-12-27',
        '2024-01-25','2024-02-24','2024-03-25','2024-04-23','2024-05-23','2024-06-22','2024-07-21','2024-08-19','2024-09-18','2024-10-17','2024-11-15','2024-12-15',
        '2025-01-13','2025-02-12','2025-03-14','2025-04-13','2025-05-12','2025-06-11','2025-07-10','2025-08-09','2025-09-07','2025-10-07','2025-11-05','2025-12-04',
        '2026-01-03','2026-02-01','2026-03-03','2026-04-02','2026-05-01','2026-05-31','2026-06-29','2026-07-29','2026-08-28','2026-09-26','2026-10-26','2026-11-24','2026-12-24',
        '2027-01-22','2027-02-20','2027-03-22','2027-04-20','2027-05-20','2027-06-19','2027-07-18','2027-08-17','2027-09-15','2027-10-15','2027-11-14','2027-12-13',
    )
    # New moon (as above, dates given here are for UTC, so not accurate)
    NEWMOON_DATES = (
        '2020-01-24','2020-02-23','2020-03-24','2020-04-23','2020-05-22','2020-06-21','2020-07-20','2020-08-19','2020-09-17','2020-10-16','2020-11-15','2020-12-14',
        '2021-01-13','2021-02-11','2021-03-13','2021-04-12','2021-05-11','2021-06-10','2021-07-10','2021-08-08','2021-09-07','2021-10-06','2021-11-04','2021-12-04',
        '2022-01-02','2022-02-01','2022-03-02','2022-04-01','2022-04-30','2022-05-30','2022-06-29','2022-07-28','2022-08-27','2022-09-25','2022-10-25','2022-11-23','2022-12-23',
        '2023-01-21','2023-02-20','2023-03-21','2023-04-20','2023-05-19','2023-06-18','2023-07-17','2023-08-16','2023-09-15','2023-10-14','2023-11-13','2023-12-12',
        '2024-01-11','2024-02-09','2024-03-10','2024-04-08','2024-05-08','2024-06-06','2024-07-05','2024-08-04','2024-09-03','2024-10-02','2024-11-01','2024-12-01','2024-12-30',
        '2025-01-29','2025-02-28','2025-03-29','2025-04-27','2025-05-27','2025-06-25','2025-07-24','2025-08-23','2025-09-21','2025-10-21','2025-11-20','2025-12-20',
        '2026-01-18','2026-02-17','2026-03-19','2026-04-17','2026-05-16','2026-06-15','2026-07-14','2026-08-12','2026-09-11','2026-10-10','2026-11-09','2026-12-09',
        '2027-01-07','2027-02-06','2027-03-08','2027-04-06','2027-05-06','2027-06-04','2027-07-04','2027-08-02','2027-08-31','2027-09-30','2027-10-29','2027-11-28','2027-12-27',
    )

    start_uid_group(63652)
    for fm_date in FULLMOON_DATES:
        print_vevent('🌕 Full moon', fm_date)
    for nm_date in NEWMOON_DATES:
        print_vevent('🌑 New moon', nm_date)


def print_annual_days():
    # Annual days, not holidays
    start_uid_group(72662)
    print_vevent('Holocaust Memorial Day', '1945-01-27', repeat='YEARLY', daycount=1)
    print_vevent('International Women\'s Day', '1977-03-08', repeat='YEARLY', daycount=1)
    print_vevent('International Men\'s Day', '1999-11-19', repeat='YEARLY', daycount=1)
    print_vevent('International Trans Day of Visibility', '2009-03-31', repeat='YEARLY', daycount=1)
    print_vevent('Bisexual Pride Day', '1999-09-23', repeat='YEARLY', daycount=1)
    print_vevent('International Day Against Homophobia, Biphobia and Transphobia', '2005-05-17', repeat='YEARLY', daycount=1)
    print_vevent('Martin Luther King Jr. Day (USA)', '1986-01-20', repeat='YEARLY', bymonthday=[1,'3MO'], daycount=1)
    print_vevent('Juneteenth (USA), end of slavery in Texas', '1865-06-19', repeat='YEARLY', anniv='BOTH')
    print_vevent('Black History Month (USA & Canada)', '1970-02-01', repeat='YEARLY')
    print_vevent('Black History Month (UK & Ireland)', '1987-10-01', repeat='YEARLY')
    print_vevent('World AIDS day', '1988-12-01', repeat='YEARLY', daycount=1)
    print_vevent('International Talk Like a Pirate Day', '1995-09-19', repeat='YEARLY', daycount=1)
    print_vevent('World Introvert Day', '2012-01-02', repeat='YEARLY', daycount=1)
    print_vevent('Pi Day', '2000-03-14', repeat='YEARLY', daycount=1)
    print_vevent('Perseids meteor shower', '2000-08-12', repeat='YEARLY')
    print_vevent('Leonids meteor shower', '2000-11-17', repeat='YEARLY')


def print_historical_anniversaries():
    # Birthdays of historical figures, anniversaries of historical events
    start_uid_group(47157)
    print_vevent('Cervantes\' birthday (maybe)', '1547-09-29', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Shakespeare\'s birthday (maybe)', '1564-04-23', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Beethoven\'s birthday', '1770-12-16', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Jane Austen\'s birthday', '1775-12-16', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Charles Babbage\'s birthday', '1891-12-26', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Charles Darwin\'s birthday', '1809-02-12', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Ada Lovelace\'s birthday', '1815-12-10', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('13th Amendment of US Constitution ratified (abolished slavery)', '1865-12-06', repeat='YEARLY', anniv='BOTH')
    print_vevent('Marie Skłodowska-Curie\'s birthday', '1867-11-07', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Albert Einstein\'s birthday', '1879-03-14', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Alan Turing\'s birthday', '1912-06-23', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Nelson Mandela\'s birthday', '1918-07-18', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Nelson Mandela released from prison', '1990-02-11', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Representation of the People Act 1918 passed, allowing women to vote in the UK', '1918-02-06', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Sophie Scholl\'s birthday', '1921-05-09', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Anne Frank\'s birthday', '1929-06-12', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Yuri Gagarin becomes first man in space', '1961-04-12', repeat='YEARLY', anniv='BOTH')
    print_vevent('Valentina Tereshkova becomes first woman in space', '1963-06-16', repeat='YEARLY', anniv='BOTH')
    print_vevent('Neil Armstrong becomes first man to walk on the Moon', '1969-07-20', repeat='YEARLY', anniv='BOTH')
    print_vevent('Boston Tea Party', '1773-12-16', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('India & Pakistan gain independence from Britain', '1947-08-15', repeat='YEARLY', daycount=1, anniv='BOTH')
    print_vevent('Fall of the Berlin Wall', '1989-11-09', repeat='YEARLY', daycount=1, anniv='BOTH')


def print_work_events():
    # Work events
    start_uid_group(93425)
    day_back = 11-(day_offset+3)%7 # first Mon after 4th Jan
    print_vevent('Back to work', '{:04d}-01-{:02d}'.format(YEAR,day_back))
    print_vevent('Team meeting', '{:04d}-01-{:02d}'.format(YEAR,1+(7-day_offset)%7), time='10:30', repeat='MONTHLY', bymonthday='1MO')
    print_vevent('Farrier', '{:04d}-01-{:02d}'.format(YEAR,day_back+3), time='19:00')
    print_vevent('Presentation to Sophie & team', '{:04d}-02-{:02d}'.format(YEAR,day_back+7), time='14:00')
    print_vevent('Meeting with Steve (Marketing)', '{:04d}-02-{:02d}'.format(YEAR,1 if day_offset not in (2,3) else 5-day_offset), time='14:30')
    print_vevent('Funding deadline', '{:04d}-03-{:02d}'.format(YEAR, 2 if day_offset2 not in (2,3) else 9-day_offset2))
    print_vevent('Last day (half day)', '{:04d}-12-{:02}'.format(YEAR,23 if day_offset2 not in (2,3) else 24-day_offset2)) # last weekday before 24th
    print_vevent('Visit from Imran (Manufacturing)', '{:04d}-03-{:02d}'.format(YEAR,1 if day_offset not in (2,3) else 5-day_offset), time='10:00', status='cancelled')


def print_personal_anniversaries():
    # Birthdays (fictional!)
    start_uid_group(58781)
    print_vevent('Dad\'s birthday', '1953-04-02', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('Mum\'s birthday', '1955-07-12', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('Grandma\'s birthday', '1930-11-29', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('J\'s birthday', '1980-09-17', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('Mo\'s birthday', '1979-02-16', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('Matt P\'s birthday', '1980-03-22', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('Matt B\'s birthday', '1982-10-29', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('Nila\'s birthday', '1983-01-25', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('Antoine\'s birthday', '1983-05-04', repeat='YEARLY', daycount=1, anniv='COUNT')
    print_vevent('The twins\' birthday', '2012-06-01', repeat='YEARLY', daycount=1, anniv='COUNT')


def print_personal_events():
    # Social & personal events
    start_uid_group(46711)
    first_wed = 12-(day_offset+1)%7 # first Wed after 2nd Jan
    print_vevent('Guitar lesson', '{:04d}-01-{:02d}'.format(YEAR, first_wed), time='19:00', repeat='WEEKLY', interval=2)
    print_vevent('Dentist', '{:04d}-03-{:02d}'.format(YEAR, 1 if day_offset2<5 else 8-day_offset2), time='9:00')
    print_vevent('Merseyside Derby', '{:04d}-02-{:02d}'.format(YEAR, 7-day_offset2), time='14:00')
    print_vevent('Party at Mo+Soph\'s', '{:04d}-02-{:02d}'.format(YEAR, 20-day_offset2 if day_offset2<5 else 27-day_offset2), time='20:00')
    print_vevent('Mum+Dad visit', '{:04d}-{:02d}-{:02d}'.format(YEAR, 3 if day_offset2==6 else 2, 27-day_offset2 if day_offset2<5 else (28 if day_offset2==6 else 1)))
    print_vevent('Romeo & Juliet', '{:04d}-03-11'.format(YEAR), time='19:00')
    print_vevent('Take car for MOT', '{:04d}-03-17'.format(YEAR), time='10:00')
    print_vevent('New bed delivered', '{:04d}-02-01'.format(YEAR), time='9:00',endtime='12:00')
    print_vevent('Thai with Jay+Rich?', '{:04d}-{:02d}-{:02d}'.format(YEAR, 3, 14),status='tentative')

    # Some to-dos
    # config assumed:
    #list0_filter = UNCATEGORIZED
    #list1_title = Exercises
    #list1_filter = exercise
    #list2_title = Spanish vocab
    #list2_filter = spanish
    #list3_title = Holiday
    #list3_filter = holiday

    print_vtodo('Book flu vaccinations')
    print_vtodo('Renew domain names', duedate='{:04d}-09-19'.format(YEAR))
    print_vtodo('Phone bank')

    # Exercises
    print_vtodo('Bike - 5m warmup + 25min alternate 2m & 30s sprints', 'exercise')
    print_vtodo('Planks (side) planks - 1min, 3(2) reps', 'exercise')
    print_vtodo('Squats - 20, 3 reps', 'exercise')

    # Fictional holiday
    print_vevent('Fly to Barcelona', '{:04d}-07-{:02d}'.format(YEAR, 24-day_offset2))
    print_vevent('Off work', '{:04d}-07-{:02d}'.format(YEAR, 23-day_offset2), daycount=15)
    print_vevent('Back to UK', '{:04d}-{:02d}-{:02d}'.format(YEAR, 8 if day_offset2<5 else 7, (5 if day_offset2<5 else 36)-day_offset2))
    print_vevent('Spanish class', '{:04d}-05-{:02d}'.format(YEAR, 12-day_offset2), time='19:30', repeat='WEEKLY', repeat_count=11)
    print_vtodo('Take Luna (& food etc.) to Antoine & Nila\'s', cat='holiday')
    print_vtodo('Order Euros', cat='holiday', priority=1, status='NEEDS-ACTION')
    print_vtodo('Buy: suncream, mosquito repellant', cat='holiday')
    print_vtodo('Buy: hats & sunglasses for the kids', cat='holiday')
    print_vtodo('Find power adaptors', cat='holiday')

    # Spanish vocab
    print_vtodo('el museo - museum', cat='spanish')
    print_vtodo('el billete de ida y vuelta - return ticket', cat='spanish')
    print_vtodo('el horario - timetable', cat='spanish')
    print_vtodo('el mapa - map', cat='spanish')
    print_vtodo('la heladería - ice cream shop', cat='spanish')
    print_vtodo('la tumbona - sunbed', cat='spanish')
    print_vtodo('el secador de pelo - hair dryer', cat='spanish')


#
# Parse arguments
#
parser = ArgumentParser()
parser.add_argument('--public-holidays', action='store_true')
parser.add_argument('--celebration-days', action='store_true')
parser.add_argument('--historical-events', action='store_true')
parser.add_argument('--dst-changes', action='store_true')
parser.add_argument('--work', action='store_true')
parser.add_argument('--personal', action='store_true')
parser.add_argument('--personal-anniversaries', action='store_true')
parser.add_argument('--moon-phases', action='store_true')
args = parser.parse_args()

do_all =     not args.public_holidays \
         and not args.celebration_days \
         and not args.historical_events \
         and not args.dst_changes \
         and not args.work \
         and not args.personal \
         and not args.personal_anniversaries \
         and not args.moon_phases

#
# Output iCal file
#
print('BEGIN:VCALENDAR', end='\r\n')
print('VERSION:2.0', end='\r\n')
print('PRODID:-//Semiprime//PygendaTest//EN', end='\r\n')

if do_all or args.public_holidays:
    print_holidays()

if do_all or args.celebration_days:
    print_annual_days()

if do_all or args.historical_events:
    print_historical_anniversaries()

if do_all or args.dst_changes:
    print_daylight_saving_changes()

if do_all or args.work:
    print_work_events()

if do_all or args.personal_anniversaries:
    print_personal_anniversaries()

if do_all or args.moon_phases:
    print_moon_phases()

if do_all or args.personal:
    print_personal_events()

print('END:VCALENDAR', end='\r\n')
