import numpy as np

#max weight assignment
class KMmatcher:
    # weights : nxm weight matrix (numpy , float), n <= m
    def __init__(self, weights):
        weights = np.array(weights).astype(float)
        self.weights = weights
        self.n, self.m = weights.shape
        assert self.n <= self.m
        # init label
        self.label_x = np.max(weights, axis=1)
        self.label_y = np.zeros((self.m, ), dtype=float)

        self.max_match = 0
        self.xy = -np.ones((self.n,), dtype=int)
        self.yx = -np.ones((self.m,), dtype=int)

    def do_augment(self, x, y):
        self.max_match += 1
        while x != -2:
            self.yx[y] = x
            ty = self.xy[x]
            self.xy[x] = y
            x, y = self.prev[x], ty

    def find_augment_path(self):
        self.S = np.zeros((self.n,), bool)
        self.T = np.zeros((self.m,), bool)

        self.slack = np.zeros((self.m,), dtype=float)
        self.slackyx = -np.ones((self.m,), dtype=int)  # l[slackyx[y]] + l[y] - w[slackx[y], y] == slack[y]

        self.prev = -np.ones((self.n,), int)

        queue, st = [], 0
        root = -1

        for x in range(self.n):
            if self.xy[x] == -1:
                queue.append(x)
                root = x
                self.prev[x] = -2
                self.S[x] = True
                break

        self.slack = self.label_y + self.label_x[root] - self.weights[root]
        self.slackyx[:] = root

        while True:
            while st < len(queue):
                x = queue[st]; st+= 1

                is_in_graph = np.isclose(self.weights[x], self.label_x[x] + self.label_y)
                nonzero_inds = np.nonzero(np.logical_and(is_in_graph, np.logical_not(self.T)))[0]

                for y in nonzero_inds:
                    if self.yx[y] == -1:
                        return x, y
                    
                    self.T[y] = True
                    queue.append(self.yx[y])
                    self.add_to_tree(self.yx[y], x)

            self.update_labels()
            queue, st = [], 0
            is_in_graph = np.isclose(self.slack, 0)
            nonzero_inds = np.nonzero(np.logical_and(is_in_graph, np.logical_not(self.T)))[0]

            for y in nonzero_inds:
                x = self.slackyx[y]
                if self.yx[y] == -1:
                    return x, y
                
                self.T[y] = True
                if not self.S[self.yx[y]]:
                    queue.append(x)
                    self.add_to_tree(self.yx[y], x)

    def solve(self, verbose = False):
        while self.max_match < self.n:
            x, y = self.find_augment_path()
            self.do_augment(x, y)

        sum = 0.
        for x in range(self.n):
            if verbose:
                print('match {} to {}, weight {:.4f}'.format(x, self.xy[x], self.weights[x, self.xy[x]]))
            sum += self.weights[x, self.xy[x]]
        self.best = sum
        if verbose:
            print('ans: {:.4f}'.format(sum))

        return sum


    def add_to_tree(self, x, prevx):
        self.S[x] = True
        self.prev[x] = prevx

        better_slack_idx = self.label_x[x] + self.label_y - self.weights[x] < self.slack
        self.slack[better_slack_idx] = self.label_x[x] + self.label_y[better_slack_idx] - self.weights[x, better_slack_idx]
        self.slackyx[better_slack_idx] = x

    def update_labels(self):
        delta = self.slack[np.logical_not(self.T)].min()
        self.label_x[self.S] -= delta
        self.label_y[self.T] += delta
        self.slack[np.logical_not(self.T)] -= delta

def solve_km_assignment(cost_matrix, cost_threshold=0.5):
    """
    使用KM-Matcher進行匹配
    Args:
        cost_matrix: 2D numpy array, 成本矩陣，形狀為 (n, m)，其中 n 是追蹤對象數量，m 是dets數量
        cost_threshold: float, 成本閾值，匹配成本小於等於此值的對象將被視為匹配成功
    Returns:
        match: 1D numpy array, 每個追蹤對象對應的檢測對象索引，-1表示未匹配 (size = len(n))
    """
    if cost_matrix.shape[0] <= cost_matrix.shape[1]:
        matcher = KMmatcher(cost_matrix)
        matcher.solve()
        match = matcher.xy
    else:
        matcher = KMmatcher(cost_matrix.T)
        matcher.solve()
        match = matcher.yx
    
    # 把match結果對應原本cost_matrix當中 數值<=0 的位置設置為-1
    for trk_id, match_det_idx in enumerate(match):
        if cost_matrix[trk_id, match_det_idx] <= cost_threshold:
            match[trk_id] = -1
            
    return match
