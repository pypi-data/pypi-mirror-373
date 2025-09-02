from torch.utils.data import Dataset, DataLoader
import torch


def get_param_indexs(index=torch.arange(327, 331), param_nums=(6, 5, 4, 3, 2)):
    """

    :param index: [..., 1]
    :param param_nums:
    :return: [..., 5]
    """
    ans = index + 0
    rs = []
    for base in param_nums[::-1]:
        a1 = ans % base
        rs.append(a1)
        ans = ans // base
    return torch.cat(rs, dim=-1).flip(-1).long()


def get_sample_indexs(param_indexs, param_nums=(6, 5, 4, 3, 2)):
    """

    :param param_indexs: [..., 5]
    :param param_nums: [*5*]
    :return: [..., 1]
    """
    tmp = 1
    bases = [tmp]
    for b in param_nums[1:][::-1]:
        tmp = tmp * b
        bases.append(tmp)
    bases = torch.Tensor(bases).flip(0).unsqueeze(-1).long()

    flt_param_index = param_indexs.flatten(0, -2)
    flt_size = [*param_indexs.size()][:-1]

    flt_indexs = flt_param_index @ bases

    return flt_indexs.unflatten(0, flt_size)


def get_imgs(
        param_srcs=torch.randn(1, 5),
        fig_size=torch.Tensor([200, 200]).long()
):
    """

    :param param_srcs: [..., 5]:(a, b, pose, x, y)
    :param fig_size: (height, width)
    :return: Tensor[..., height, width]
    """
    freedom = param_srcs.size(-1)
    xs, ys = torch.meshgrid(torch.arange(0, fig_size[0]), torch.arange(0, fig_size[1]))
    xs = xs - fig_size[0] // 2
    ys = ys - fig_size[1] // 2
    index = [1 for i in range(len(param_srcs.size()) - 1)]
    sample_size = [*param_srcs.size()][:-1]

    xs = xs.view(*index, *fig_size).expand(*sample_size, *fig_size)
    ys = ys.view(*index, *fig_size).expand(*sample_size, *fig_size)

    pas = param_srcs[..., 0].unsqueeze(-1).unsqueeze(-1).expand(xs.size())
    pbs = param_srcs[..., 1].unsqueeze(-1).unsqueeze(-1).expand(xs.size())
    pose = param_srcs[..., 2].unsqueeze(-1).unsqueeze(-1).expand(xs.size())
    xb = param_srcs[..., 3].unsqueeze(-1).unsqueeze(-1).expand(xs.size())
    yb = param_srcs[..., 4].unsqueeze(-1).unsqueeze(-1).expand(xs.size())

    imgs = (pbs * (xs * torch.cos(pose) + ys * torch.sin(pose) - xb)) ** 2 + (
            pas * (ys * torch.cos(pose) - xs * torch.sin(pose) - yb)) ** 2 <= (pas * pbs) ** 2
    return imgs.float()

# from EasyModel import Model
# class MultiGaussianFig(Model):
#     def __init__(self, a, b, pose, x, y):
#         self.pas = torch.nn.Parameters(a)
#         self.pbs = torch.nn.Parameters(b)
#         self.prs = torch.nn.Parameters(pose)
#         self.pxs = torch.nn.Parameters(x)
#         self.pys = torch.nn.Parameters(y)

#     def forward(self):
#         return get_imgs()



class LinearCongruence:
    def __init__(self, seed=1.7, k=5.6, b=3.5, p=1):
        self.seed = seed
        self.k = k
        self.b = b
        self.p = p

    def random(self, item):
        seed = self.seed +0
        k = self.k + 0
        b = self.b + 0
        p = self.p + 0
        for i in range(item):
            seed = (seed * k + b) % p
        return seed


class SingleEpliDataset(Dataset):
    def __init__(self, srcs=None):
        """
        srcs
        """
        if srcs is None:
            srcs = torch.rand(5, 3)*28
            srcs[0] += 28

        self.srcs = srcs
        self.param_nums = []
        for src in srcs:
            self.param_nums.append(src.flatten().size(0))
        self.sample_num = 1
        for n in self.param_nums:
            self.sample_num *= n

        fig_size = torch.empty(2)
        size_a = srcs[0]
        locate_x = srcs[-2]
        locate_y = srcs[-1]
        fig_size[1] = 2 * ((size_a.abs().max() + locate_x.abs().max()).long() + 1)
        fig_size[0] = 2 * ((size_a.abs().max() + locate_y.abs().max()).long() + 1)
        self.fig_size = fig_size.long()

        self.random = LinearCongruence()

    #region  params
    @ property
    def param_a(self):
        return self.srcs[0]
    @ property
    def param_b(self):
        return self.srcs[1]
    @ property
    def param_pose(self):
        return self.srcs[2]
    @ property
    def param_x(self):
        return self.srcs[3]
    @ property
    def param_y(self):
        return self.srcs[4]
    
    #endregion


    #region  iterable
    def __getitem__(self, item):
        sep_mark = self.random.random(item)
        if isinstance(item, int):
            item = torch.tensor([item])
        param_indexs = get_param_indexs(torch.Tensor(item), self.param_nums)
        params = []
        for i, index in enumerate(param_indexs):
            params.append(self.srcs[i][index])
        params = torch.stack(params)
        img = get_imgs(params, self.fig_size)

        return item, sep_mark, img

    def __iter__(self):
        self.iter_count = -1
        return self

    def __next__(self):
        self.iter_count += 1
        if self.iter_count >= len(self):
            raise StopIteration
        return self.iter_count

    def __len__(self):
        return self.sample_num

    
    #endregion

    def loader(self, batch_size=1, shuffle=True):
        return DataLoader(self, batch_size=batch_size, shuffle=shuffle)



