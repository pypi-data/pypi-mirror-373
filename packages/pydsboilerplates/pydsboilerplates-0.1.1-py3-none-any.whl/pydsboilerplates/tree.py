from utils import TreeNode as Node


class Tree:
    def __init__(self,nums=None,root=None):
        self.root = root if root else self.add_nodes(nums)

    def add_nodes(self,nodes):
        nodes = list(map(lambda x: Node(x) if x else x, nodes))
        for i, nd in enumerate(nodes):
            if nd:
                nd.left = nodes[2 * i + 1] if (2 * i + 1) < len(nodes) else None
                nd.right = nodes[2 * i + 2] if (2 * i + 2) < len(nodes) else None

        return nodes[0]

    def dfs(self):
        stck = [self.root]
        op = []
        while stck:
            tmp = stck.pop()
            op.append(tmp.val)
            if tmp.right:
                stck.append(tmp.right)
            if tmp.left:
                stck.append(tmp.left)
        return op

    def bfs(self):
        que = [self.root]
        op = []
        while que:
            tmp = que[0]
            op.append(tmp.val)
            que = que[1:]
            if tmp.left:
                que.append(tmp.left)
            if tmp.right:
                que.append(tmp.right)

        return op
