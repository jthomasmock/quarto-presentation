import pop.hub


def start():
    hub = pop.hub.Hub()
    hub.pop.sub.add(dyne_name="rend")
    hub.rend.init.standalone()
