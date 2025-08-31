class Node:
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return str(self.val)

class ListNode(Node):
    def __init__(self,val,nxt=None):
        super().__init__(val)
        self.nxt = nxt

class TreeNode(Node):
    def __init__(self,val,left=None,right=None):
        super().__init__(val)
        self.left = left
        self.right = right

