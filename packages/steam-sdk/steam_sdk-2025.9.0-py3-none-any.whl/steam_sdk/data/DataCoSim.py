from dataclasses import dataclass

@dataclass
class NSTI:
    """
    N=Simulation number, S=Simulation set, T=Time window, I=Iteration
    """
    n: int
    s: int
    t: int
    i: int


    def update(self, n, s, t, i):
        self.n = n
        self.s = s
        self.t = t
        self.i = i


    @property
    def n_s_t_i(self):
        return f'{self.n}_{self.s}_{self.t}_{self.i}'