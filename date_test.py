import datetime

s = "Wed Oct 23 12:11:08"
t = "%a %b %d %H:%M:%S"

type(s)
# OUT: <type 'str'>
type(t)
# OUT: <type 'str'>
datetime.datetime.strptime(s, t)
# OUT: datetime.datetime(1900, 10, 23, 12, 11, 8)
s
# OUT: 'Wed Oct 23 12:11:08'
t
# OUT: '%a %b %d %H:%M:%S'

datetime.datetime.strptime(s, t)
# OUT: datetime.datetime(1900, 10, 23, 12, 11, 8)
datetime.datetime.strptime(s, t)
# OUT: datetime.datetime(1900, 10, 23, 12, 11, 8)
datetime.datetime.strptime(s, t)
# OUT: datetime.datetime(1900, 10, 23, 12, 11, 8)
