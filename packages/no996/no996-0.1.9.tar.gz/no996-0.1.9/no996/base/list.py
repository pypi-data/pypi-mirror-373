class ListNode:
    @staticmethod
    def split_list_n_list(origin_list, n):
        """
        均分列表
        :param origin_list: 原始列表
        :param n: 份数
        :return: 列表生成器
        """
        if len(origin_list) % n == 0:
            cnt = len(origin_list) // n
        else:
            cnt = len(origin_list) // n + 1

        for i in range(0, n):
            yield origin_list[i * cnt : (i + 1) * cnt]
