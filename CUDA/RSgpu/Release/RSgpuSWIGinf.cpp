
#include "RSgpuSWIGinf.h"


void TestKern(int blocks, int threads)
{
	
	CudaTestInf(blocks, threads);
	return;
}

void RSgpuCalcField(
	double kr,
	gpureal * pre, int nx1, int ny1, int nz1,
	gpureal * pim, int nx2, int ny2, int nz2,
	gpureal * xp, int Nx,
	gpureal * yp, int Ny,
	gpureal * zp, int Nz,
	gpureal * u_real, int Nu1,
	gpureal * u_imag, int Nu2,
	gpureal * coeffs, int Nc,
	gpureal * ux, int Nux,
	gpureal * uy, int Nuy,
	gpureal * uz, int Nuz,
	gpureal * uvx, int Nuvx,
	gpureal * uvy, int Nuvy,
	gpureal * uvz, int Nuvz
	)
{
	
	RSgpu_CalcPressureField(
		pre, pim, kr,
		xp, Nx, yp, Ny, zp, Nz,
		u_real, u_imag, coeffs,
		ux, uy, uz,
		uvx, uvy, uvz,
		Nu1);

	return;
}