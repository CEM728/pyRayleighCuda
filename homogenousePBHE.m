function [ T, pixMultiplier, newDx, tdotsrc, newI ] = homogenousePBHE( T0, alpha, ktherm, rho, cp, c_sound, I, Nx, Ny, Nz, Dx, nnx, nny, nnz, Nt, tstep, downsample )
%homogenousePBHE Wrapper to call Penne's bioheat MEX function
%   [ T, pixMultiplier, newDx, tdotsrc, newI ] = homogenousePBHE( T0, alpha, ktherm, rho, cp, I, Nx, Ny, Nz, Dx, nnx, nny, nnz, Nt, tstep, downsample )
%   Inputs:
%   T0 - scalar or 3D map of initial temperature. Of size [Nx Ny Nz] if 3D.
%   alpha - thermo-acoustic absorption coefficient in 1/meters.  
%   ktherm - thermal conductivity in W/(m*C). Tissue and gel ~ 0.5 - 0.7.  
%   rho - density of the material in (kg/m^3)
%   cp - heat capacity of the material in J/(kg*C)
%   c_sound - sound speed in m/s
%   I - 3D acoustic intensity-magnitude field in (W/m^2). The 3-D temperature source is deterined from these parameters. 
%       The the temperature source is dT/dt = 2*alpha * I / (rho*Cp), so alpha=0 means
%       there is no heat source.  Only diffusion of the T0 occurs.
%   Nx,Ny,Nz -  Dimensions of I.  
%   nnx,nny,nnz - Upper limit of the resulting temperature map dimensions.
%       If downsample = 1, then the simulation grid will be downsampled from the input grid size (for faster results).
%       The size is the result of an integer number of pixels being averaged
%       together.
%   downsample - whether or not downsample I. 
%   


if downsample
    
    newI=I;
    pixMultiplier=1.0;
    newIdims = [Nx Ny Nz];
        
    [newI, pixMultiplier, newIdims] = reduceTruncate3D( I, Nx, Ny, Nz, nnx, nny, nnz );

    nnx = newIdims(1);
    nny = newIdims(2);
    nnz = newIdims(3);

else

    newI=I;
    pixMultiplier=1.0;
    newIdims = [Nx Ny Nz];
    
    nnx = newIdims(1);
    nny = newIdims(2);
    nnz = newIdims(3);

end

newDx = pixMultiplier.*Dx;

fdtdDX = [tstep newDx];

T=zeros(Nt,nnx,nny,nnz);
tdotsrc = newI* (2*alpha / (rho*c_sound));

rho_cp_3d = zeros(nnx,nny,nnz);
kt3d = zeros(nnx,nny,nnz);

T(1,:,:,:) = T0;

kt3d(:) = ktherm;
rho_cp_3d(:) = rho*cp;

PBHE_FDsolve_mex(T, tdotsrc, rho_cp_3d, kt3d, fdtdDX);
%PBHE_FreeOutflow_FDsolve_mex(T, tdotsrc, rho_cp_3d, kt3d, fdtdDX);

end

