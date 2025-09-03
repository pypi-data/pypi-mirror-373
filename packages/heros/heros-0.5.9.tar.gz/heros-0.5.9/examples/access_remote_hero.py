from heros import RemoteHERO

if __name__ == "__main__":
    obj = RemoteHERO("foobar1")

    # call remote functions
    print(obj.read_temp(0, 10))
    print(obj.hello())

    # set remote attribute
    obj.foovar = ["hallo", 2, []]

    # read remote attributes
    print(obj.foovar)
    print(obj.testme)

    # react on remote event
    def printer(payload):
        print(payload)

    obj.new_data.connect(printer)
