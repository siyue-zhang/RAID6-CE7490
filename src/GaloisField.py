import numpy as np 

class GaloisField(object):
    def __init__(self, num_data_disk, num_check_disk):
        self.num_data_disk = num_data_disk
        self.num_check_disk = num_check_disk
        self.prime = 0b100011101 # modulo
        self.gf_exp = [0] * 512 
        self.gf_log = [0] * 256
        self.vander = np.zeros((self.num_check_disk, self.num_data_disk), dtype=int)
        self.init_tables()
        self.init_vander()

    def init_tables(self):
        '''
        Set up the look up logarithm table
        '''
        b = 1
        for log in range(255):
            self.gf_log[b] = log
            self.gf_exp[log] = b
            b <<= 1
            if b & 0x100:
                b ^= self.prime    
        for i in range(255, 512):
            self.gf_exp[i] = self.gf_exp[i - 255]
    def init_vander(self):
        '''
        Set up the Vandermond matrix
        '''
        for i in range(self.num_check_disk):
            for j in range(self.num_data_disk):
                self.vander[i][j] = self.gf_power(j+1, i)
    
    def add(self, a, b):
        '''
        Sum in Galosis Field
        '''
        sum = a ^ b
        return sum

    def sub(self, a, b):
        '''
        Subtraction in Galosis Field
        '''
        return self.add(a, b)
    
    def gf_mul(self, a, b):
        '''
        Multiplication in Galosis Field
        Args:
            a: multiplicand
            b: multiplier
        '''
        if a == 0 or b == 0:
            return 0         
        return self.gf_exp[self.gf_log[a] + self.gf_log[b]]
    
    def gf_div(self, a, b):
        '''
        Division in Galosis Field
        Args:
            a: dividend
            b: divisor
        '''
        if a == 0:
            return 0
        if b == 0:
           raise ZeroDivisionError()
        return self.gf_exp[(self.gf_log[a] + 255 - self.gf_log[b]) % 255]

    
    def gf_power(self, a, n):
        '''
        Exponentiation in Galosis Field
        Args:
            a: base
            n: exponent
        '''
        return self.gf_exp[(self.gf_log[a] * n) % 255]
  
    def dot(self, a, b):
        '''
        Inner product of vector
        Return: c
        '''
        res = 0
        for i in range(len(a)):
            res = self.add(res, self.gf_mul(a[i], b[i]))
        return res  

    def matmul(self, a, b):
        '''
        Matrix multiplication
        Return: mat res
        '''
        res = np.zeros([a.shape[0], b.shape[1]], dtype=int)
        for i in range(res.shape[0]):
            for j in range(res.shape[1]):
                res[i][j] = self.dot(a[i, :], b[:, j])
        return res

    def gf_poly_add(self,p,q):
        r = [0] * max(len(p),len(q))
        for i in range(0,len(p)):
            r[i+len(r)-len(p)] = p[i]
        for i in range(0,len(q)):
            r[i+len(r)-len(q)] ^= q[i]
        return r

    def gf_poly_mul(self,p,q):
        r = [0] * (len(p)+len(q)-1)
        for j in range(0, len(q)):
            for i in range(0, len(p)):
                r[i+j] ^= self.gf_mul(p[i], q[j])
        return r

    def gf_poly_scale(self,p,x):
        return  [self.gf_mul(i, x) for i in p] 

    def gf_inverse(self, A):
        """
        cal the left inverse matrix of A
        Args:
            A: matrix
        Return: 
            A^-1
        """
        if A.shape[0] != A.shape[1]:
            A_T = np.transpose(A)
            A_ = self.matmul(A_T, A)
        else:
            A_ = A
        A_ = np.concatenate((A_, np.eye(A_.shape[0], dtype=int)), axis=1)
        dim = A_.shape[0]
        for i in range(dim):
            if not A_[i, i]:
                for k in range(i + 1, dim):
                    if A_[k, i]:
                        break
                A_[i, :] = list(map(self.add, A_[i, :], A_[k, :]))
            A_[i, :] = list(map(self.gf_div, A_[i, :], [A_[i, i]] * len(A_[i, :])))
            for j in range(i+1, dim):
                A_[j, :] = self.add(A_[j,:], list(map(self.gf_mul, A_[i, :], [self.gf_div(A_[j, i], A_[i, i])] * len(A_[i, :]))))
        for i in reversed(range(dim)):
            for j in range(i):
                A_[j, :] = self.add(A_[j, :], list(map(self.gf_mul, A_[i, :], [A_[j,i]] * len(A_[i,:]))))
        A_inverse = A_[:,dim:2*dim]
        if A.shape[0] != A.shape[1]:
            A_inverse = self.matmul(A_inverse, A_T)

        return A_inverse
    
    def gf_poly_eval(self,p,x):
        y = p[0]
        for i in range(1, len(p)):
            y = self.gf_mul(y,x) ^ p[i]
        return y