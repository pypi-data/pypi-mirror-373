import numpy as np
import camb
import os
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import quad,quad_vec
from astropy.constants import G
import massfunc as mf
from filelock import FileLock
from joblib import Parallel,delayed


h=0.674
rhoc=2.7752e11*h**2
Omegam=0.315
rhom=rhoc*Omegam
OmegaLambda=1-Omegam
omegab = .0224*h**-2

class SteepPowerCalculator:

    #here As, ns are from Planck constraints, you should not change them much
    #alpha, beta, A2byA1, kMpc_trans are model parameters; alpha in [-2, 2], beta in [-pi, pi], A2byA1 in (0, 1), kMpc_trans is where you want the boost of power to start.
    # To get the standard case without power boost, you can set A2byA1 = 1 or kMpc_trans = + infinity.
    def __init__(self, As=2.1e-9, ns = 0.965, A2byA1 = 0.1, kMpc_trans = 1200, alpha=2.0, beta=0.0):
        self.alpha = alpha
        self.beta = beta
        self.c_alpha = np.cosh(alpha)
        self.s_alpha = np.sinh(alpha)
        self.c_beta = np.cos(beta)
        self.s_beta = np.sin(beta)
        self.As = As
        self.ns = ns
        self.A2byA1 = A2byA1
        self.kMpc_trans = kMpc_trans
        self.kMpc_pivot = 0.05 ##where As is defined
        eps = (1.-ns)/6.  #\epsilon        
        self.boost = (self.c_alpha-self.c_beta*self.s_alpha)**2 + (self.s_beta*self.s_alpha)**2

        self.HbyMp = np.pi*np.sqrt(As*eps*8./self.boost)  #H/M_p

        self.A1byMp3 = np.sqrt(eps*18.)*self.HbyMp**2
        self.A2byMp3 = self.A1byMp3*A2byA1

        self.norm = (3.*self.HbyMp**3/(2.*np.pi*self.A2byMp3))**2
        self.coef  = 3.*(1. - self.A2byA1)
        self.c1 = (self.c_alpha-self.c_beta*self.s_alpha)
        self.c2 = self.s_beta*self.s_alpha
        self.c3 = (self.c_alpha+self.c_beta*self.s_alpha)
        self.mp_prepared = False
                


    def PrimordialPower(self, kMpc:list):
        k = kMpc/self.kMpc_trans
        ksq = k**2
        if(k < 0.03): 
            kjy = -1./3.+ ksq*( (2./35.)*ksq -2./15. )
            kjj = k*ksq/9.*(1.-ksq/5.)
        else:
            kjy = ((k**2-1.)*np.sin(2*k)+2*k*np.cos(2*k))/(2.*k**3)
            kjj = (k*np.cos(k)-np.sin(k))**2/k**3
        return self.norm*(kMpc/self.kMpc_pivot)**(self.ns-1.)*((self.c1*(1.+self.coef*kjy) + self.c2*self.coef*kjj)**2 + (self.c2*(1.+self.coef*kjy) + self.c3*self.coef*kjj)**2)

   # Transfer function from BBKS to primordial power
    def BBKS_trans(self, x:float):
        return  np.log(1.+0.171*x)**2 *x**(self.ns-2.) / np.sqrt( 1.+ x*(0.284+x*(1.3924+x*(0.0635212+x*0.057648))))

    def Prepare_MatterPower(self, H0 = 67.5, ombh2 = 0.022, omch2 = 0.12, kMpc_max=10., zmax = 100.):
        nz = 100 #number of steps to use for the radial/redshift integration
        kmax=min(kMpc_max, 30.)  #kmax to use
        pars = camb.CAMBparams()
        pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2)
        pars.InitPower.set_params(As = self.As, ns=self.ns)
        results= camb.get_background(pars)
        self.mpi =  camb.get_matter_power_interpolator(pars, nonlinear=False, hubble_units=False, k_hunit=False, kmax=kmax, zmax=zmax)
        self.k_eq = 0.073*(omch2+ombh2)
        self.kmax = kmax
        self.norm_edge = self.BBKS_trans(self.kmax/self.k_eq)
        self.mp_prepared = True



    def MatterPower(self, kMpc:list, z): #kMpc can be an ordered array; z is the redshift
        if(not self.mp_prepared):
            self.Prepare_MatterPower()
        if(isinstance(kMpc, float)):
            if(kMpc <= self.kmax):
                pkraw = self.mpi.P(z, kMpc)
            else:
                pkraw = self.BBKS_trans(kMpc/self.k_eq)/self.norm_edge * self.mpi.P(z, self.kmax)
            return pkraw * (self.PrimordialPower(kMpc)/(self.As*(kMpc/self.kMpc_pivot)**(self.ns-1.)))
        else:
            nk = len(kMpc)
            Pk = np.empty(nk)
            for i in range(nk):
                if(kMpc[i] <= self.kmax):
                    pkraw = self.mpi.P(z, kMpc[i])
                else:
                    pkraw = self.BBKS_trans(kMpc[i]/self.k_eq)/self.norm_edge*self.mpi.P(z, self.kmax)
                Pk[i] = pkraw * (self.PrimordialPower(kMpc[i])/(self.As*(kMpc[i]/self.kMpc_pivot)**(self.ns-1.)))
            return Pk

class MassFunctions:
    def __init__(self, A2byA1=0.1, kMpc_trans=2e2, alpha=2.0, beta=0.0):
        self.spc = SteepPowerCalculator(As = 2.1e-9, ns = 0.965, A2byA1 = A2byA1, kMpc_trans = kMpc_trans, alpha = alpha, beta = beta) 
        self.A2byA1 = A2byA1
        self.kMpc_trans = kMpc_trans
        self.alpha = alpha
        self.beta = beta
        self.dsigma2_dm_interpolation_completed = False
        self.pk_interpolation_completed = False
        self.sigma2_interpolation_completed = False
        self.m_interp_range = np.logspace(0.0,18.0,1000)
        self.ps_interp_range = np.logspace(-4.0,8.0,50000)
        self.cosmo = mf.SFRD()


    def PowerSpectrum_Interp_Set(self):
        filename = f'.ps_init_out/Pk_interp_A{self.A2byA1}_K{self.kMpc_trans}_Alpha{self.alpha}_Beta{self.beta}.npy'
        lockfile = filename + '.lock'
        try:
            Pk_arr = np.load(filename)
        except FileNotFoundError:
            os.makedirs('.ps_init_out', exist_ok=True)
            with FileLock(lockfile):
                if not os.path.exists(filename):
                    self.spc.Prepare_MatterPower(H0=67.4, ombh2=0.022, omch2=0.12, kMpc_max=self.ps_interp_range[-1])
                    Pk = self.spc.MatterPower(self.ps_interp_range, z=0.0)
                    np.save(filename, Pk)
                Pk_arr = np.load(filename)
        self.pk0_interpolation = interp1d(np.log10(self.ps_interp_range), np.log10(Pk_arr), kind='cubic')
        self.pk_interpolation_completed = True

    def Sigma2_Interp_Set(self):
        filename = f'.ps_init_out/Sigma2_interp_A{self.A2byA1}_K{self.kMpc_trans}_Alpha{self.alpha}_Beta{self.beta}.npy'
        lockfile = filename + '.lock'
        try:
            sig_arr = np.load(filename)
        except FileNotFoundError:
            os.makedirs('.ps_init_out', exist_ok=True)
            with FileLock(lockfile):
                if not os.path.exists(filename):
                    sig = self.sigma2(self.m_interp_range)
                    np.save(filename, sig)
                sig_arr = np.load(filename)
        self.sigma2m_interpolation = interp1d(np.log10(self.m_interp_range), np.log10(sig_arr), kind='cubic')
        self.sigma2_interpolation_completed = True

    def Dsigma2dm_Interp_Set(self):
        filename = f'.ps_init_out/Dsigma2_dm_interp_A{self.A2byA1}_K{self.kMpc_trans}_Alpha{self.alpha}_Beta{self.beta}.npy'
        lockfile = filename + '.lock'
        try:
            dsig2dm_arr = np.load(filename)
        except FileNotFoundError:
            os.makedirs('.ps_init_out', exist_ok=True)
            with FileLock(lockfile):
                if not os.path.exists(filename):
                    dsig2dm = np.log10(-self.dsigma2_dm(self.m_interp_range))
                    np.save(filename, dsig2dm)
                dsig2dm_arr = np.load(filename)
        self.dsigma2_dm_interpolation = interp1d(np.log10(self.m_interp_range), dsig2dm_arr, kind='cubic')
        self.dsigma2_dm_interpolation_completed = True

    def ps_interp(self, kMpc):
        if not self.pk_interpolation_completed:
            self.PowerSpectrum_Interp_Set()
        # if kMpc < self.ps_interp_range[0] or kMpc > self.ps_interp_range[-1]:
        #     return self.spc.MatterPower(kMpc, z = self.z)
        return 10**self.pk0_interpolation(np.log10(kMpc))

    def sigma2_interp(self,M):
        if not self.sigma2_interpolation_completed:
            self.Sigma2_Interp_Set()
        # if M < self.m_interp_range[0] or M > self.m_interp_range[-1]:
        #     return self.sigma2(M)
        return 10**self.sigma2m_interpolation(np.log10(M))
    
    def dsigma2_dm_interp(self,M):
        if not self.dsigma2_dm_interpolation_completed:
            self.Dsigma2dm_Interp_Set()
        # if M < self.m_interp_range[0] or M > self.m_interp_range[-1]:
        #     return self.dsigma2_dm(M)
        return -10 ** self.dsigma2_dm_interpolation(np.log10(M))

    def dsigma2_dk(self,M,k):
        r=(3.0*M/(4.0*np.pi*rhom))**(1./3.) 
        x=r*k
        w=3.0*(np.sin(x)-x*np.cos(x))/x**3.0
        return 4.0*np.pi*k**2.0/(2.0*np.pi)**3.0 * self.ps_interp(k) * w*w

    def dsigma2_dlnk(self,lnk,M):
        k=np.exp(lnk)
        return k*self.dsigma2_dk(M,k)
    
    def sigma2(self,M):
        precision = 1e-6
        k_grid_1 = np.logspace(-4,0.9,20)
        k_grid_2 = np.logspace(1,5.3,200)
        k_grid = np.concatenate([k_grid_1, k_grid_2])
        int_ans = np.zeros_like(M)
        for i in range(len(k_grid)-1):
            int_ans += quad_vec(self.dsigma2_dlnk,np.log(k_grid[i]),np.log(k_grid[i+1]), args=(M,),epsrel=precision,limit=200)[0]
        return int_ans

    def dsigma2_dlnk_dm(self,lnk,M):
        k=np.exp(lnk)
        r=(3.0*M/(4.0*np.pi*rhom))**(1./3.)
        x=r*k
        w=3.0*(np.sin(x)-x*np.cos(x))/(x)**3.0
        dw_dx=(9.0*x*np.cos(x)+np.sin(x)*(3.0*x**2.0-9.0))/(x)**4.0
        dw_dm=dw_dx*k/(4.0*np.pi*r**2.0*rhom)
        return 4.0*np.pi*k**3.0/(2.0*np.pi)**3.0*self.ps_interp(k)*2.0*w*dw_dm

    def dsigma2_dm(self,M):
        precision = 1e-6
        k_grid_1 = np.logspace(-4,0.9,20)
        k_grid_2 = np.logspace(1,5.3,200)
        k_grid = np.concatenate([k_grid_1, k_grid_2])
        int_ans = np.zeros_like(M)
        for i in range(len(k_grid)-1):
            int_ans += quad_vec(self.dsigma2_dlnk_dm,np.log(k_grid[i]),np.log(k_grid[i+1]), args=(M,),epsrel=precision,limit=200)[0]
        return int_ans
    
    def dndmps(self, m, z):
        sigm = np.sqrt(self.sigma2_interp(m))
        dsig_dm = abs(self.dsigma2_dm_interp(m)) / (2.0 * sigm)
        return np.sqrt(2.0 / np.pi) * self.cosmo.rhom / m * self.cosmo.deltac(z) / sigm * dsig_dm * np.exp(-self.cosmo.deltac(z) ** 2 / (2 * sigm ** 2))

    def dndmst(self,M,z):
        Ast=0.353
        ast2=0.73
        Pst=0.175
    #   ST parameters from Jenkins et al. 2001,0005260
        sigma = np.sqrt(self.sigma2_interp(M))
        nu=self.cosmo.deltac(z)/sigma
        nup=np.sqrt(ast2)*nu
        dsigmadm=self.dsigma2_dm_interp(M)/(2*sigma)
        return -rhom/M*(dsigmadm/sigma)*(2*Ast)*(1+1.0/(nup)**(2*Pst))*(nup**2/(2*np.pi))**(1./2.)*np.exp(-nup**2/2)

    def delta_L(self, deltar,z):
        return (1.68647 - 1.35 / (1 + deltar) ** (2 / 3) - 1.12431 / (1 + deltar) ** (1 / 2) + 0.78785 / (1 + deltar) ** (0.58661)) / self.cosmo.Dz(z)

    def dndmeps(self, M, Mr, deltar, z):
        delta_L = self.delta_L(deltar,z)
        sig1 = self.sigma2_interp(M) - self.sigma2_interp(Mr)
        del1 = self.cosmo.deltac(z) - delta_L
        return rhom * (1 + deltar) / M / np.sqrt(2 * np.pi) * abs(self.dsigma2_dm_interp(M)) * del1 / sig1 ** (3 / 2) * np.exp(-del1 ** 2 / (2 * sig1))
    
    def M_Jeans(self, z):
        return 5.73e3*(Omegam*h**2/0.15)**(-1/2) * (omegab*h**2/0.0224)**(-3/5) * ((1+z)/10)**(3/2)



    # def func_fcoll(self,lnM,z):
    #     M=np.exp(lnM)
        #     return M*self.dndmst(M,z)*M

        # def fcoll(self,Mmin,Mmax,z):
        #     ss = 0
        #     mslice = np.linspace(Mmin,Mmax,50)
        #     for i in range(len(mslice)-1):
        #         ss += quad(self.func_fcoll,np.log(mslice[i]),np.log(mslice[i+1]), args=(z),epsrel=1e-6)[0]
        #     return ss/rhom

        # def dfcolldz(self,minmass,maxmass,z):
        #     zs = z - z*.01
        #     zl = z + z*.01
        #     diffz = (  self.fcoll(minmass,maxmass,zl) - self.fcoll(minmass,maxmass,zs)  ) / (zl - zs)
        #     return diffz

    def Delta_cc(self,z):
        d=self.cosmo.omegam_z(z)-1.0
        return 18*np.pi**2+82.0*d-39.0*d**2

    def M_vir(self,mu,Tvir,z):
        a1=(self.cosmo.omegam_z(z)*self.Delta_cc(z)/(18*np.pi**2))**(-1.0/3.0)
        a2=a1*(mu/0.6)**(-1.0)*((1.0+z)/10)**(-1.0)/1.98e4*Tvir
        return a2**(3.0/2.0)*1e8/h

    # @staticmethod
    # def M_Jeans(mu,T,z):
    #     return 3.96e4*(T/mu)**(3./2.)*(Omegam*h**2)**(-1./2.)*(1+z)**(-3./2.)

    def fstar(self,M):
        f0 = .14
        ylo = .46
        yhi = .82
        Mp = 10**12.3#M_sun solmass
        fup = 2 * f0
        fdown = ( (M/Mp)**-ylo + (M/Mp)**yhi )
        return fup/fdown

    def fduty(slef,M):
        al = 1.5
        Mc = 6e7
        return (1 +(2.**(al/3.)-1)*(M/Mc)**-al)**(-3./al)

    def dMdt(self,M,z):
        return 24.1 * (M/(1e12))**1.094 * (1+1.75*z) * np.sqrt(  Omegam*(1+z)**3 + OmegaLambda  )  #solmass/yr

    def rhosfrdiff(self,lnM,z):
        M = np.exp(lnM)
        diff = self.fstar(M) * omegab/Omegam * self.dMdt(M,z) * self.dndmst(M,z) * self.fduty(M)
        return M * diff

    def rhosfr(self,T1,T2):
        Mmin =  self.M_vir(Tvir=T1,mu=0.61)
        Mmax =  self.M_vir(Tvir=T2,mu=0.61)
        mslice = np.linspace(Mmin,Mmax,50)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(self.rhosfrdiff,np.log(mslice[i]),np.log(mslice[i+1]), epsrel=1e-6)[0]
        return ans
    

if __name__ == '__main__':
    mf1 = MassFunctions(A2byA1=0.1, kMpc_trans=2e2, alpha=2.0, beta=0.0)
    mf2 = MassFunctions(A2byA1=1.0, kMpc_trans=1e6, alpha=0.0, beta=0.0)
    cosmo = mf.SFRD()

    k_space = np.logspace(-4, 8, 1000)  # k in Mpc^-1
    pk1 = mf1.ps_interp(k_space)
    pk2 = mf2.ps_interp(k_space)
    pks = cosmo.Pk(k_space, z=0.0)
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(k_space, pk1, label='A2byA1=0.1')
    plt.plot(k_space, pk2, label='A2byA1=1.0')
    plt.plot(k_space, pks, label='Standard', color='crimson', linewidth=3, linestyle='--')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim([1e-4,1e4])
    plt.ylim([1e-7,1e6])
    plt.xlabel('k (Mpc$^{-1}$)')
    plt.ylabel('P(k) (Mpc$^3$ h$^{-3}$)')
    plt.legend()
    plt.title('Matter Power Spectrum Comparison')
    plt.savefig('standard_out/matter_power_spectrum_comparison.png')

    # 测试sigma2
    m_test = np.logspace(1, 15, 1000)  #
    sigma2_1 = mf1.sigma2_interp(m_test)
    sigma2_2 = mf2.sigma2_interp(m_test)
    sigma2_s = cosmo.sigma2_interpolation(m_test)
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(m_test, sigma2_1, label='A2byA1=0.1')
    plt.plot(m_test, sigma2_2, label='A2byA1=1.0')
    plt.plot(m_test, sigma2_s, label='Standard',color='crimson',linewidth=3,linestyle='--')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim([1e1, 1e15])
    plt.xlabel('Mass (M_sun)')
    plt.ylabel('σ² (Mpc$^3$ h$^{-3}$)')
    plt.legend()
    plt.title('Variance σ² Comparison')
    plt.savefig('standard_out/NS_variance_comparison.png')

    # 测试dsigma2_dm
    plt.figure(figsize=(10, 6), dpi=300)
    dsig_ori_1 = mf1.dsigma2_dm(m_test)
    dsig_ori_2 = mf2.dsigma2_dm(m_test)
    plt.plot(m_test, -dsig_ori_1, label='A2byA1=0.1')
    plt.plot(m_test, -dsig_ori_2, label='A2byA1=1.0')

    dsigmadm_s = cosmo.dsig2dm_interpolation(m_test)
    plt.plot(m_test, -dsigmadm_s, label='Standard',color='crimson',linewidth=3,linestyle='--')

    dsigma2_dm_1 = mf1.dsigma2_dm_interp(m_test)
    dsigma2_dm_2 = mf2.dsigma2_dm_interp(m_test)

    plt.plot(m_test, -dsigma2_dm_1, label='A2byA1=0.1')
    plt.plot(m_test, -dsigma2_dm_2, label='A2byA1=1.0')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim([1e1, 1e15])
    plt.xlabel('Mass (M_sun)')
    plt.ylabel('dσ²/dM (Mpc$^3$ h$^{-3}$)')
    plt.legend()
    plt.title('Derivative of Variance dσ²/dM Comparison')
    plt.savefig('standard_out/NS_derivative_variance_comparison_log.png')

    mh = np.logspace(1, 15, 1000)
    hmf1 = mf1.dndmst(mh,10.0)
    hmf2 = mf2.dndmst(mh,10.0)
    hmf_s = cosmo.dndmst(mh,10.0)
    plt.figure(figsize=(10, 6),dpi=300)
    plt.plot(mh, mh*hmf1, label='A2byA1=0.1')
    plt.plot(mh, mh*hmf2, label='A2byA1=1.0')
    plt.plot(mh, mh*hmf_s, label='Standard', color='crimson', linewidth=3, linestyle='--')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim([1e1,1e15])
    plt.ylim([1e-7,1e6])
    plt.xlabel('Mass (M_sun)')
    plt.ylabel('dN/dM (Mpc^{-3} h^3)')
    plt.legend()
    plt.title('Halo Mass Function Comparison')
    plt.savefig('standard_out/NS_halo_mass_function_comparison_10.png')
# if __name__ == '__main__':
#     # 对比两种情况
#     mf1 = MassFunctions(A2byA1=0.1, kMpc_trans=2e2, alpha=2.0, beta=0.0, z=10.0)
#     mf2 = MassFunctions(A2byA1=1.0, kMpc_trans=1e6, alpha=0.0, beta=0.0, z=10.0)
    
#     # 测试几个质量点
#     test_masses = np.logspace(6, 16, 20)
    
#     print("Testing A2byA1=0.1:")
#     for m in test_masses[:5]:  # 只测试前5个
#         try:
#             sigma2 = mf1.sigma2_interp(m)
#             dsigma2dm = mf1.dsigma2_dm_interp(m)
#             hmf = mf1.dndmst(m, z=10.0)
#             print(f"M={m:.2e}: σ²={sigma2:.2e}, dσ²/dM={dsigma2dm:.2e}, hmf={hmf:.2e}")
#         except Exception as e:
#             print(f"M={m:.2e}: Error - {e}")
    
#     print("\nTesting A2byA1=1.0:")
#     for m in test_masses[:5]:
#         try:
#             sigma2 = mf2.sigma2_interp(m)
#             dsigma2dm = mf2.dsigma2_dm_interp(m)
#             hmf = mf2.dndmst(m, z=10.0)
#             print(f"M={m:.2e}: σ²={sigma2:.2e}, dσ²/dM={dsigma2dm:.2e}, hmf={hmf:.2e}")
#         except Exception as e:
#             print(f"M={m:.2e}: Error - {e}")
