import numpy as np
import os 
import sys
import massfunc as mf
import astropy.units as u
from scipy.interpolate import interp1d
from scipy.integrate import quad,quad_vec
from scipy.optimize import fsolve,root_scalar
from scipy.optimize import brentq
from . import PowerSpectrum as ps


cosmo = mf.SFRD()
m_H = (cosmo.mHu.to(u.M_sun)).value #M_sun
omega_b = cosmo.omegab
omega_m = cosmo.omegam
rhom = cosmo.rhom
nH = cosmo.nH  #cm^-3

class Barrier:

    def __init__(self,fesc=0.2, qion=10000.0,z_v=8.0,A2byA1=0.1,kMpc_trans=600,alpha=2.0,beta=0.0):
        self.A2byA1,self.kMpc_trans,self.alpha,self.beta = A2byA1,kMpc_trans,alpha,beta
        self.fesc = fesc
        self.qion = qion
        self.z = z_v
        self.M_min = cosmo.M_vir(0.61,1e4,self.z)  # Minimum halo mass for ionization
        self.powspec = ps.MassFunctions(A2byA1=A2byA1,kMpc_trans=kMpc_trans,alpha=alpha,beta=beta)
        self.deltaR_interp = np.concatenate((np.linspace(-0.999,2,1000), np.linspace(2.001,25,1000)))
        self.Nion_normal_ratio = self.Nion_ST()*self.fesc*self.qion
        self.M_J = self.powspec.M_Jeans(self.z)
        self.delta_R = np.linspace(-0.95,2,100)
        # self.Nxi_normal_ratio = self.Nxi_ST()

    def Nion_Pure(self,Mv,deltaR):
        def Nion_Pure_diff(m,Mv,deltaR):
            fstar = cosmo.fstar(m)
            return fstar*m*self.dndmeps(m,Mv,deltaR,self.z)/ m_H * omega_b / omega_m
        mslice = np.logspace(np.log10(self.M_min), np.log10(Mv), 12)
        ans = np.zeros_like(deltaR)
        for i in range(len(mslice)-1):
            ans += quad_vec(Nion_Pure_diff, mslice[i], mslice[i+1],args=(Mv,deltaR), epsrel=1e-6)[0]
        return ans
    
    def Nxi_Pure(self,Mv,deltaR):
        def Nxi_Pure_diff(m,Mv,deltaR):
            return self.Xim(m,self.z)*m*self.dndmeps(m,Mv,deltaR,self.z)/ m_H * omega_b / omega_m
        mslice = np.logspace(np.log10(self.M_J), np.log10(self.M_min), 12)
        ans = np.zeros_like(deltaR)
        for i in range(len(mslice)-1):
            ans += quad_vec(Nxi_Pure_diff, mslice[i], mslice[i+1],args=(Mv,deltaR), epsrel=1e-6)[0]
        return ans
    
    def Xim(self,m,z):
        A,B,C,D,E,F,G = 4.4 , 0.334, 0.023, 0.199, -0.042, 0,1
        M7 = m/1e7
        F0 = 1.0
        return 1+A*M7**(B+C*np.log10(M7))*(F+G*(1+z)/10)* F0**(D+E*np.log10(F0))
    
    # Interpolation for Nion
    def Nion_interp(self, Mv,deltaR):
        try:
            Nion_arr = np.load(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs(f'.Nion_Interp_init/NionAtz{self.z:.2f}', exist_ok=True)
            nion_pure = self.Nion_Pure(Mv, self.deltaR_interp)
            np.save(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nion_pure)
            Nion_arr = np.load(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        Nion_interp_Mv = interp1d(self.deltaR_interp, Nion_arr, kind='cubic')
        return Nion_interp_Mv(deltaR) * self.fesc * self.qion 

    # Interpolation for N_xi
    def N_xi_interp(self, Mv, deltaR):
        try:
            Nxi_arr = np.load(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}', exist_ok=True)
            nxi_pure = self.Nxi_Pure(Mv, self.deltaR_interp)
            np.save(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nxi_pure)
            Nxi_arr = np.load(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        Nxi_interp_Mv = interp1d(self.deltaR_interp, Nxi_arr, kind='cubic')
        return Nxi_interp_Mv(deltaR) 

    def Nxi_normalized(self,Mv:float,deltaR:np.ndarray) -> np.ndarray:
        nxi = self.N_xi_interp(Mv, deltaR)
        nxi_mean = np.mean(nxi) 
        nxi_normal = self.Nxi_ST()
        ratio = nxi_normal / nxi_mean
        return ratio * nxi

    def Nion_normalized(self,Mv:float,deltaR:np.ndarray) -> np.ndarray:
        nion = self.Nion_interp(Mv, deltaR)
        nion_mean = np.mean(nion) 
        ratio = self.Nion_normal_ratio / nion_mean
        return ratio * nion

    def Nion_ST(self):
        def Nion_ST_diff(m):
            fstar = cosmo.fstar(m)
            return (1 / m_H * fstar * omega_b / omega_m * m * self.powspec.dndmst(m, self.z))
        mslice = np.logspace(np.log10(self.M_min), np.log10(cosmo.M_vir(0.61,1e10,self.z)), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nion_ST_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans

    def Nxi_ST(self):
        def Nxi_ST_diff(m):
            return (self.Xim(m,self.z)*1 / m_H * omega_b / omega_m * m * self.powspec.dndmst(m, self.z))
        mslice = np.logspace(np.log10(self.M_J), np.log10(self.M_min), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nxi_ST_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans
    
    def N_H(self,deltaR):
        return 1/m_H * omega_b/omega_m * rhom *(1+deltaR)

    def delta_L(self, deltar):
        return ( 1.68647 - 1.35/(1+deltar)**(2/3) - 1.12431/(1+deltar) ** (1/2) + 0.78785/(1+deltar)**(0.58661) ) / cosmo.Dz(self.z)
    
    def dndmeps(self,M,Mr,deltar,z):
        deltaL = self.delta_L(deltar)
        sig1 = self.powspec.sigma2_interp(M) - self.powspec.sigma2_interp(Mr)
        del1 = cosmo.deltac(z) - deltaL
        return cosmo.rhom * (1 + deltar) / M / np.sqrt(2 * np.pi) * abs(self.powspec.dsigma2_dm_interp(M)) * del1 / (sig1**(3 / 2)) * np.exp(-del1 ** 2 / (2 * sig1))

    
    def dEPS_dz(self,M,Mv,deltar,z):
        return (self.dndmeps(M,Mv,deltar,z+0.001*z) - self.dndmeps(M,Mv,deltar,z-0.001*z)) / (0.002*z)

    def dNxi_dz(self,m,deltaR,Mv,z):
        return self.Xim(m,z)*m*self.dEPS_dz(m,Mv,deltaR,z)/ m_H * omega_b / omega_m

    def Nxi_dz(self,deltaR,Mv,z):
        Mj = cosmo.M_J(z)
        Mmax = cosmo.M_vir(0.61,1e4,z)
        if self.dEPS_dz(Mj,Mv,deltaR,z)>0 and self.dEPS_dz(Mmax,Mv,deltaR,z)>0:
            return 0
        elif self.dEPS_dz(Mj,Mv,deltaR,z)<0 and self.dEPS_dz(Mmax,Mv,deltaR,z)<0:
            M = np.logspace(np.log10(Mj),np.log10(Mmax),12)
            ans = 0 
            for i in range(len(M)-1):
                ans += quad_vec(self.dNxi_dz,M[i],M[i+1],args=(deltaR,Mv,z))[0]
            return ans
        elif self.dEPS_dz(Mj,Mv,deltaR,z)>0 and self.dEPS_dz(Mmax,Mv,deltaR,z)<0:
            Log_Mmin = brentq(lambda logM:self.dEPS_dz(10**logM,Mv,deltaR,z), np.log10(Mj), np.log10(Mmax),xtol=0.05)
            M = np.logspace(Log_Mmin,np.log10(Mmax),12)
            ans = 0
            for i in range(len(M)-1):
                ans += quad_vec(self.dNxi_dz,M[i],M[i+1],args=(deltaR,Mv,z))[0]
            return ans
        else:
            return 0
    def Nxi_dz_interp(self, deltaR, Mv, z):
        try:
            Nxi_arr = np.load(f'.Nxi_dz_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs(f'.Nxi_dz_Interp_init/NxiAtz{self.z:.2f}', exist_ok=True)
            delta_R = np.linspace(-0.95,2,100)
            nxi_pure = np.array([self.Nxi_dz(dr,Mv,z) for dr in delta_R])
            np.save(f'.Nxi_dz_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nxi_pure)
            Nxi_arr = np.load(f'.Nxi_dz_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        Nxi_interp_Mv = interp1d(self.delta_R, Nxi_arr, kind='cubic')
        return Nxi_interp_Mv(deltaR)

    def dST_dz(self,m,z):
        return (self.powspec.dndmst(m,z+0.001*z) - self.powspec.dndmst(m,z-0.001*z)) / (0.002*z)

    def dNxi_dz_ST(self,m,z):
        return self.Xim(m,z)*m*self.dST_dz(m,z)/ m_H * omega_b / omega_m

    def Nxi_dz_ST(self,z):
        Mj = cosmo.M_J(z)
        Mmax = cosmo.M_vir(0.61,1e4,z)
        if self.dST_dz(Mj,z)>0 and self.dST_dz(Mmax,z)>0:
            return 0
        if self.dST_dz(Mj,z)<0 and self.dST_dz(Mmax,z)<0:
            M = np.logspace(np.log10(Mj),np.log10(Mmax),12)
            ans = 0
            for i in range(len(M)-1):
                ans += quad_vec(self.dNxi_dz_ST,M[i],M[i+1],args=(z))[0]
            return ans
        if self.dST_dz(Mj,z)>0 and self.dST_dz(Mmax,z)<0:
            Mmin = brentq(self.dST_dz, Mj, Mmax, args=(z))
            M = np.logspace(np.log10(Mmin),np.log10(Mmax),12)
            ans = 0
            for i in range(len(M)-1):
                ans += quad_vec(self.dNxi_dz_ST,M[i],M[i+1],args=(z))[0]
            return ans

    # def Nxi_Add_Pure(self,Mv,deltaR):
    #     def Nxi_Pure_diff(m,Mv,deltaR):
    #         return self.Xim(m,self.z)*m*self.dEPS_dz(m,Mv,deltaR,self.z)/ m_H * omega_b / omega_m
    #     mslice = np.logspace(np.log10(self.M_Jz), np.log10(self.M_min), 12)
    #     ans = np.zeros_like(deltaR)
    #     for i in range(len(mslice)-1):
    #         ans += quad_vec(Nxi_Pure_diff, mslice[i], mslice[i+1],args=(Mv,deltaR), epsrel=1e-6)[0]
    #     if ans > 0:
    #         return 0
    #     else:
    #         return -ans

    # def dNxi_Add_Interp(self, Mv, deltaR):
    #     try:
    #         Nxi_arr = np.load(f'.Nxi_Add_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
    #     except FileNotFoundError:
    #         os.makedirs(f'.Nxi_Add_Interp_init/NxiAtz{self.z:.2f}', exist_ok=True)
    #         nxi_pure = self.Nxi_Add_Pure(Mv, self.deltaR_interp)
    #         np.save(f'.Nxi_Add_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nxi_pure)
    #         Nxi_arr = np.load(f'.Nxi_Add_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
    #     Nxi_interp_Mv = interp1d(self.deltaR_interp, Nxi_arr, kind='cubic')
    #     return Nxi_interp_Mv(deltaR)

    def CHII(self,z):
        return 2.9*((1+z)/6)**-1.1

    def dtdz(self,z):
        H = cosmo.H0u
        return ((-1/(H*cosmo.Ez(z)*(1+z))).to(u.s)).value

    def dnrec_dz_path(self,z,deltar,xHII_Field:np.ndarray)->np.ndarray:
        x_HE = 1.08
        CIGM = self.CHII(z)
        nh = nH*(1+deltar)
        Q_HII = xHII_Field
        alpha_A = 4.2e-13 #cm**3/s
        differential_trans = self.dtdz(z)
        return -CIGM*x_HE*alpha_A*nh*Q_HII*(1+z)**3 * differential_trans
    

def load_binary_data(filename, dtype=np.float32) -> np.ndarray:
        f = open(filename, "rb")
        data = f.read()
        f.close()
        _data = np.frombuffer(data, dtype)
        if sys.byteorder == 'big':
            _data = _data.byteswap()
        return _data
