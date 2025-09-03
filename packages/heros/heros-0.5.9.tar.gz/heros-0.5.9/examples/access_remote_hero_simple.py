from heros import RemoteHERO

with RemoteHERO("my_hero") as obj:
    # call remote functions
    print(obj.read_temp(0, 10))
    print(obj.hello())

    # access remote attribute
    obj.testme = 10
