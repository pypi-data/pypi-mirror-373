from utils import ListNode as Node

class LinkedList:
    def __init__(self,nodes):
        self.head = None
        self.curr = self.head
        self.add_nodes(nodes)

    def __repr__(self):
        tmp = self.head
        op = ""
        while tmp:
            op += str(tmp) + " => "
            tmp = tmp.nxt
        return op.rstrip(" => ")

    def __add_node(self, list_node):
        if self.head is None:
            self.head = Node(list_node)
            self.curr = self.head
        else:
            self.curr.nxt = Node(list_node)
            self.curr = self.curr.nxt

    def __add_arr_to_list(self,arr):
        list(map(self.__add_node,arr))

    def add_nodes(self,nodes):
        assert type(nodes) in (list,tuple,str,int)
        if isinstance(nodes,(list,tuple)):
            self.__add_arr_to_list(nodes)
        else:
            self.__add_node(nodes)
