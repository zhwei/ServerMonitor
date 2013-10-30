mongodb 文档结构
=======================


    temperature = {
        "name": "server or location",
        "description": "",
        "temp": "Temperature",
        "datetime": datetime.datetime.now()
    }

    Server = {
        "name": _name,
        "ip": _ip,
        "description": _description,
        "date": _date,
        # ---auto---------
        "system": get_system(),
        "host": get_node(),
        "cpu_info": cpu_info(),
        "location_ID":location,
        "uname": get_uname(),
    }