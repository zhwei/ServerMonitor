__author__ = 'zhwei'


def human_read(num, unit=['KB','MB','GB','TB']):
    """
    convert num to human read format
    From:
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for x in unit:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')
