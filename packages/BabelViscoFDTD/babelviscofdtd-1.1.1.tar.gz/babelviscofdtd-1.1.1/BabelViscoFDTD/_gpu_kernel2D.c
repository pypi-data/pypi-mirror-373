#ifdef METAL
#ifndef METALCOMPUTE
#define N1 p_CONSTANT_BUFFER_UINT[CInd_N1]
#define N2 p_CONSTANT_BUFFER_UINT[CInd_N2]
#define Limit_I_low_PML p_CONSTANT_BUFFER_UINT[CInd_Limit_I_low_PML]
#define Limit_J_low_PML p_CONSTANT_BUFFER_UINT[CInd_Limit_J_low_PML]
#define Limit_I_up_PML p_CONSTANT_BUFFER_UINT[CInd_Limit_I_up_PML]
#define Limit_J_up_PML p_CONSTANT_BUFFER_UINT[CInd_Limit_J_up_PML]
#define SizeCorrI p_CONSTANT_BUFFER_UINT[CInd_SizeCorrI]
#define SizeCorrJ p_CONSTANT_BUFFER_UINT[CInd_SizeCorrJ]
#define PML_Thickness p_CONSTANT_BUFFER_UINT[CInd_PML_Thickness]
#define NumberSources p_CONSTANT_BUFFER_UINT[CInd_NumberSources]
#define LengthSource p_CONSTANT_BUFFER_UINT[CInd_LengthSource]
#define NumberSensors p_CONSTANT_BUFFER_UINT[CInd_NumberSensors]
#define TimeSteps p_CONSTANT_BUFFER_UINT[CInd_TimeSteps]

#define SizePML p_CONSTANT_BUFFER_UINT[CInd_SizePML]
#define SizePMLxp1 p_CONSTANT_BUFFER_UINT[CInd_SizePMLxp1]
#define SizePMLyp1 p_CONSTANT_BUFFER_UINT[CInd_SizePMLyp1]
#define SizePMLxp1yp1 p_CONSTANT_BUFFER_UINT[CInd_SizePMLxp1yp1]
#define ZoneCount p_CONSTANT_BUFFER_UINT[CInd_ZoneCount]

#define SelRMSorPeak p_CONSTANT_BUFFER_UINT[CInd_SelRMSorPeak]
#define SelMapsRMSPeak p_CONSTANT_BUFFER_UINT[CInd_SelMapsRMSPeak]
#define IndexRMSPeak_Vx p_CONSTANT_BUFFER_UINT[CInd_IndexRMSPeak_Vx]
#define IndexRMSPeak_Vy p_CONSTANT_BUFFER_UINT[CInd_IndexRMSPeak_Vy]
#define IndexRMSPeak_Sigmaxx p_CONSTANT_BUFFER_UINT[CInd_IndexRMSPeak_Sigmaxx]
#define IndexRMSPeak_Sigmayy p_CONSTANT_BUFFER_UINT[CInd_IndexRMSPeak_Sigmayy]
#define IndexRMSPeak_Sigmaxy p_CONSTANT_BUFFER_UINT[CInd_IndexRMSPeak_Sigmaxy]
#define IndexRMSPeak_Pressure p_CONSTANT_BUFFER_UINT[CInd_IndexRMSPeak_Pressure]
#define NumberSelRMSPeakMaps p_CONSTANT_BUFFER_UINT[CInd_NumberSelRMSPeakMaps]

#define SelMapsSensors p_CONSTANT_BUFFER_UINT[CInd_SelMapsSensors]
#define IndexSensor_Vx p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Vx]
#define IndexSensor_Vy p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Vy]
#define IndexSensor_Sigmaxx p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Sigmaxx]
#define IndexSensor_Sigmayy p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Sigmayy]
#define IndexSensor_Sigmaxy p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Sigmaxy]
#define IndexSensor_Pressure p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Pressure]
#define IndexSensor_Pressure_gx p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Pressure_gx]
#define IndexSensor_Pressure_gy p_CONSTANT_BUFFER_UINT[CInd_IndexSensor_Pressure_gy]
#define NumberSelSensorMaps p_CONSTANT_BUFFER_UINT[CInd_NumberSelSensorMaps]
#define SensorSubSampling p_CONSTANT_BUFFER_UINT[CInd_SensorSubSampling]
#define SensorStart p_CONSTANT_BUFFER_UINT[CInd_SensorStart]
#define nStep p_CONSTANT_BUFFER_UINT[CInd_nStep]
#define CurrSnap p_CONSTANT_BUFFER_UINT[CInd_CurrSnap]
#define TypeSource p_CONSTANT_BUFFER_UINT[CInd_TypeSource]

#define DT p_CONSTANT_BUFFER_MEX[CInd_DT]
#define InvDXDTplus_pr (p_CONSTANT_BUFFER_MEX + CInd_InvDXDTplus)
#define DXDTminus_pr (p_CONSTANT_BUFFER_MEX + CInd_DXDTminus)
#define InvDXDTplushp_pr (p_CONSTANT_BUFFER_MEX + CInd_InvDXDTplushp)
#define DXDTminushp_pr (p_CONSTANT_BUFFER_MEX + CInd_DXDTminushp)
#else
#define nStep p_CONSTANT_BUFFER_UINT[CInd_nStep]
#define TypeSource p_CONSTANT_BUFFER_UINT[CInd_TypeSource]
#endif

#define __def_MEX_VAR_0(__NameVar)  (&p_MEX_BUFFER_0[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_1(__NameVar)  (&p_MEX_BUFFER_1[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_2(__NameVar)  (&p_MEX_BUFFER_2[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_3(__NameVar)  (&p_MEX_BUFFER_3[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_4(__NameVar)  (&p_MEX_BUFFER_4[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_5(__NameVar)  (&p_MEX_BUFFER_5[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_6(__NameVar)  (&p_MEX_BUFFER_6[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_7(__NameVar)  (&p_MEX_BUFFER_7[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_8(__NameVar)  (&p_MEX_BUFFER_8[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_9(__NameVar)  (&p_MEX_BUFFER_9[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_10(__NameVar)  (&p_MEX_BUFFER_10[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 
#define __def_MEX_VAR_11(__NameVar)  (&p_MEX_BUFFER_11[ ((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar *2])) | (((unsigned long) (p_INDEX_MEX[CInd_ ##__NameVar*2+1]))<<32) ]) 

#define __def_UINT_VAR(__NameVar)  (&p_UINT_BUFFER[ ((unsigned long) (p_INDEX_UINT[CInd_ ##__NameVar*2])) | (((unsigned long) (p_INDEX_UINT[CInd_ ##__NameVar*2+1]))<<32) ])

// #define __def_MEX_VAR(__NameVar)  (&p_MEX_BUFFER[ p_INDEX_MEX[CInd_ ##__NameVar ]]) 
// #define __def_UINT_VAR(__NameVar)  (&p_UINT_BUFFER[ p_INDEX_UINT[CInd_ ##__NameVar]])


#define k_V_x_x_pr  __def_MEX_VAR_0(V_x_x)
#define k_V_y_x_pr  __def_MEX_VAR_0(V_y_x)
#define k_V_x_y_pr  __def_MEX_VAR_0(V_x_y)
#define k_V_y_y_pr  __def_MEX_VAR_0(V_y_y)

#define k_Vx_pr  __def_MEX_VAR_1(Vx)
#define k_Vy_pr  __def_MEX_VAR_1(Vy)

#define k_Rxx_pr  __def_MEX_VAR_2(Rxx)
#define k_Ryy_pr  __def_MEX_VAR_2(Ryy)

#define k_Rxy_pr  __def_MEX_VAR_3(Rxy)

#define k_Sigma_x_xx_pr  __def_MEX_VAR_4(Sigma_x_xx)
#define k_Sigma_y_xx_pr  __def_MEX_VAR_4(Sigma_y_xx)
#define k_Sigma_x_yy_pr  __def_MEX_VAR_4(Sigma_x_yy)
#define k_Sigma_y_yy_pr  __def_MEX_VAR_4(Sigma_y_yy)

#define k_Sigma_x_xy_pr  __def_MEX_VAR_5(Sigma_x_xy)
#define k_Sigma_y_xy_pr  __def_MEX_VAR_5(Sigma_y_xy)

#define k_Sigma_xy_pr  __def_MEX_VAR_6(Sigma_xy)
#define k_Sigma_xx_pr  __def_MEX_VAR_6(Sigma_xx)

#define k_Sigma_yy_pr  __def_MEX_VAR_7(Sigma_yy)
#define k_Pressure_pr  __def_MEX_VAR_7(Pressure)

#define k_SourceFunctions_pr __def_MEX_VAR_8(SourceFunctions)

#define k_LambdaMiuMatOverH_pr  __def_MEX_VAR_9(LambdaMiuMatOverH)
#define k_LambdaMatOverH_pr     __def_MEX_VAR_9(LambdaMatOverH)
#define k_MiuMatOverH_pr        __def_MEX_VAR_9(MiuMatOverH)
#define k_TauLong_pr            __def_MEX_VAR_9(TauLong)
#define k_OneOverTauSigma_pr    __def_MEX_VAR_9(OneOverTauSigma)
#define k_TauShear_pr           __def_MEX_VAR_9(TauShear)
#define k_InvRhoMatH_pr         __def_MEX_VAR_9(InvRhoMatH)
#define k_Ox_pr  __def_MEX_VAR_9(Ox)
#define k_Oy_pr  __def_MEX_VAR_9(Oy)


#define k_SqrAcc_pr  __def_MEX_VAR_10(SqrAcc)

#define k_SensorOutput_pr  __def_MEX_VAR_11(SensorOutput)

#define k_IndexSensorMap_pr  __def_UINT_VAR(IndexSensorMap)
#define k_SourceMap_pr		 __def_UINT_VAR(SourceMap)
#define k_MaterialMap_pr	 __def_UINT_VAR(MaterialMap)

#ifdef METALCOMPUTE
#define CGID uint
#else
#define CGID uint3
#endif
#ifndef METALCOMPUTE
#define METAL_PARAMS\
	const device unsigned int *p_CONSTANT_BUFFER_UINT [[ buffer(0) ]],\
	const device mexType * p_CONSTANT_BUFFER_MEX [[ buffer(1) ]],\
	const device unsigned int *p_INDEX_MEX [[ buffer(2) ]],\
	const device unsigned int *p_INDEX_UINT [[ buffer(3) ]],\
	const device unsigned int *p_UINT_BUFFER [[ buffer(4) ]],\
	device mexType * p_MEX_BUFFER_0 [[ buffer(5) ]],\
	device mexType * p_MEX_BUFFER_1 [[ buffer(6) ]],\
	device mexType * p_MEX_BUFFER_2 [[ buffer(7) ]],\
	device mexType * p_MEX_BUFFER_3 [[ buffer(8) ]],\
	device mexType * p_MEX_BUFFER_4 [[ buffer(9) ]],\
	device mexType * p_MEX_BUFFER_5 [[ buffer(10) ]],\
	device mexType * p_MEX_BUFFER_6 [[ buffer(11) ]],\
	device mexType * p_MEX_BUFFER_7 [[ buffer(12) ]],\
	device mexType * p_MEX_BUFFER_8 [[ buffer(13) ]],\
	device mexType * p_MEX_BUFFER_9 [[ buffer(14) ]],\
	device mexType * p_MEX_BUFFER_10 [[ buffer(15) ]],\
	device mexType * p_MEX_BUFFER_11 [[ buffer(16) ]],\
	CGID gid[[thread_position_in_grid]])\
{
#else
#define METAL_PARAMS\
	const device unsigned int *p_CONSTANT_BUFFER_UINT [[ buffer(0) ]],\
	const device unsigned int *p_INDEX_MEX [[ buffer(1) ]],\
	const device unsigned int *p_INDEX_UINT [[ buffer(2) ]],\
	const device unsigned int *p_UINT_BUFFER [[ buffer(3) ]],\
	device mexType * p_MEX_BUFFER_0 [[ buffer(4) ]],\
	device mexType * p_MEX_BUFFER_1 [[ buffer(5) ]],\
	device mexType * p_MEX_BUFFER_2 [[ buffer(6) ]],\
	device mexType * p_MEX_BUFFER_3 [[ buffer(7) ]],\
	device mexType * p_MEX_BUFFER_4 [[ buffer(8) ]],\
	device mexType * p_MEX_BUFFER_5 [[ buffer(9) ]],\
	device mexType * p_MEX_BUFFER_6 [[ buffer(10) ]],\
	device mexType * p_MEX_BUFFER_7 [[ buffer(11) ]],\
	device mexType * p_MEX_BUFFER_8 [[ buffer(12) ]],\
	device mexType * p_MEX_BUFFER_9 [[ buffer(13) ]],\
	device mexType * p_MEX_BUFFER_10 [[ buffer(14) ]],\
	device mexType * p_MEX_BUFFER_11 [[ buffer(15) ]],\
	CGID gid[[thread_position_in_grid]])\
{
#endif
#endif
/// PMLS


#ifdef CUDA
extern "C" __global__ void MAIN_1_StressKernel(
#ifdef CUDA
#define __predecorator 
#else
#define __predecorator __global
#endif
__predecorator mexType *V_x_x_pr,
__predecorator mexType *V_y_x_pr,
__predecorator mexType *V_x_y_pr,
__predecorator mexType *V_y_y_pr,
__predecorator mexType *Vx_pr,
__predecorator mexType *Vy_pr,
__predecorator mexType *Rxx_pr,
__predecorator mexType *Ryy_pr,
__predecorator mexType *Rxy_pr,
__predecorator mexType *Sigma_x_xx_pr,
__predecorator mexType *Sigma_y_xx_pr,
__predecorator mexType *Sigma_x_yy_pr,
__predecorator mexType *Sigma_y_yy_pr,
__predecorator mexType *Sigma_x_xy_pr,
__predecorator mexType *Sigma_y_xy_pr,
__predecorator mexType *Sigma_xy_pr,
__predecorator mexType *Sigma_xx_pr,
__predecorator mexType *Sigma_yy_pr,
__predecorator mexType *SourceFunctions_pr,
__predecorator mexType * LambdaMiuMatOverH_pr,
__predecorator mexType * LambdaMatOverH_pr,
__predecorator mexType * MiuMatOverH_pr,
__predecorator mexType * TauLong_pr,
__predecorator mexType * OneOverTauSigma_pr,
__predecorator mexType * TauShear_pr,
__predecorator mexType * InvRhoMatH_pr,
__predecorator mexType * SqrAcc_pr,
__predecorator unsigned int * MaterialMap_pr,
__predecorator unsigned int * SourceMap_pr,
__predecorator mexType * Ox_pr,
__predecorator mexType * Oy_pr,
__predecorator mexType * Pressure_pr
	,unsigned int nStep, unsigned int TypeSource)
{
	_PT i = (_PT) (blockIdx.x * blockDim.x + threadIdx.x);
    _PT j = (_PT) (blockIdx.y * blockDim.y + threadIdx.y);
#endif
#ifdef OPENCL
__kernel void MAIN_1_StressKernel(
#ifdef CUDA
#define __predecorator 
#else
#define __predecorator __global
#endif
__predecorator mexType *V_x_x_pr,
__predecorator mexType *V_y_x_pr,
__predecorator mexType *V_x_y_pr,
__predecorator mexType *V_y_y_pr,
__predecorator mexType *Vx_pr,
__predecorator mexType *Vy_pr,
__predecorator mexType *Rxx_pr,
__predecorator mexType *Ryy_pr,
__predecorator mexType *Rxy_pr,
__predecorator mexType *Sigma_x_xx_pr,
__predecorator mexType *Sigma_y_xx_pr,
__predecorator mexType *Sigma_x_yy_pr,
__predecorator mexType *Sigma_y_yy_pr,
__predecorator mexType *Sigma_x_xy_pr,
__predecorator mexType *Sigma_y_xy_pr,
__predecorator mexType *Sigma_xy_pr,
__predecorator mexType *Sigma_xx_pr,
__predecorator mexType *Sigma_yy_pr,
__predecorator mexType *SourceFunctions_pr,
__predecorator mexType * LambdaMiuMatOverH_pr,
__predecorator mexType * LambdaMatOverH_pr,
__predecorator mexType * MiuMatOverH_pr,
__predecorator mexType * TauLong_pr,
__predecorator mexType * OneOverTauSigma_pr,
__predecorator mexType * TauShear_pr,
__predecorator mexType * InvRhoMatH_pr,
__predecorator mexType * SqrAcc_pr,
__predecorator unsigned int * MaterialMap_pr,
__predecorator unsigned int * SourceMap_pr,
__predecorator mexType * Ox_pr,
__predecorator mexType * Oy_pr,
__predecorator mexType * Pressure_pr
	, unsigned int nStep, unsigned int TypeSource)
{
  _PT i = (_PT) get_global_id(0);
  _PT j = (_PT) get_global_id(1);
#endif
#ifdef METAL
kernel void MAIN_1_StressKernel(
	METAL_PARAMS
	#ifndef METALCOMPUTE
  	_PT i = (_PT) gid.x;
  	_PT j = (_PT) gid.y;
	#else	
	_PT j = (_PT) ((gid )/N1);
  	_PT i = (_PT) (gid -j*N1);
	#endif
#endif

#if defined(OPENCL) || defined(METAL) || defined(CUDA)
if (i>=N1 || j >=N2  )
	return;
#endif
	
	mexType Diff;
	mexType Diff2;
	mexType Dx;
	mexType Dy;
	mexType value;
	mexType m1;
	mexType m2;
	mexType m3;
	mexType m4;
	mexType RigidityXY=0.0;
	mexType TauShearXY=0.0;
	mexType LambdaMiu;
	mexType LambdaMiuComp;
	mexType dFirstPart;
	mexType dFirstPartForR;
	mexType accum_xx=0.0;
	mexType accum_yy=0.0;
	mexType accum_p=0.0;
	_PT source;
	_PT bAttenuating=1;
	mexType Miu;
	mexType MiuComp;
	mexType OneOverTauSigma;
	mexType NextR;

	mexType accum_xy=0.0;



#ifdef USE_2ND_ORDER_EDGES
    interface_t interfaceZ=inside, interfaceY=inside, interfaceX=inside;
#endif
_PT index2;
_PT index;
_PT  MaterialID;
_PT CurZone;

for ( CurZone=0;CurZone<ZoneCount;CurZone++)
  {
	index=Ind_MaterialMap(i,j);
	MaterialID=ELD(MaterialMap,index);
	m1=ELD(MiuMatOverH,MaterialID);
	if (i<N1-1)
		m2=ELD(MiuMatOverH,EL(MaterialMap,i+1,j));
	else
		m2=m1;
	if (j<N2-1)
		m3=ELD(MiuMatOverH,EL(MaterialMap,i,j+1));
	else
		m3=m1;
	if (i<N1-1 && j<N2-1 )
		m4=ELD(MiuMatOverH,EL(MaterialMap,i+1,j+1));
	else
		m4 = m1;
	value=m1*m2*m3*m4;
	RigidityXY =value !=0.0 ? 4.0/(1.0/m1+1.0/m2+1.0/m3+1.0/m4):0.0;
	if (value ==0.0)
		TauShearXY = ELD(TauShear,MaterialID);
	else
	{
		m1 = ELD(TauShear,MaterialID);
		if (i<N1-1)
			m2=ELD(TauShear,EL(MaterialMap,i+1,j));
		else
			m2=m1;
		if (j<N2-1)
			m3=ELD(TauShear,EL(MaterialMap,i,j+1));
		else
			m3=m1;
		if (i<N1-1 && j<N2-1 )
			m4=ELD(TauShear,EL(MaterialMap,i+1,j+1));
		else
			m4=m1;

		TauShearXY=0.25*(m1+m2+m3+m4);
		
	}	   
  	
  	if (IsOnPML_I(i)==1 || IsOnPML_J(j)==1 )//We are in the PML borders
  	 {

  		if (i<N1-1 && j <N2-1 )
  		{

  			Diff= i>1 && i <N1-1 ? CA*(EL(Vx,i,j)-EL(Vx,i-1,j)) -
  			                       CB*(EL(Vx,i+1,j)-EL(Vx,i-2,j))
  			      : i>0 && i <N1 ? (EL(Vx,i,j)-EL(Vx,i-1,j))  :0;

			Diff2= j>1 && j < N2-1 ? CA*(EL(Vy,i,j)-EL(Vy,i,j-1))-
  									CB*(EL(Vy,i,j+1)-EL(Vy,i,j-2))
  			        : j>0 && j < N2 ? EL(Vy,i,j)-EL(Vy,i,j-1):0;

  			index2=Ind_Sigma_x_xx(i,j);
  			ELD(Sigma_x_xx,index2) =InvDXDT_I*(
  											ELD(Sigma_x_xx,index2)*DXDT_I+
  											ELD(LambdaMiuMatOverH,MaterialID)*
  											Diff);
			index2=Ind_Sigma_y_xx(i,j);
  			ELD(Sigma_y_xx,index2) =InvDXDT_J*(
  											ELD(Sigma_y_xx,index2)*DXDT_J+
  											ELD(LambdaMatOverH,MaterialID)*
  											Diff2);

			index=Ind_Sigma_xx(i,j);
  			index2=Ind_Sigma_x_xx(i,j);
  			ELD(Sigma_xx,index)= ELD(Sigma_x_xx,index2) + ELD(Sigma_y_xx,index2);
		
			index2=Ind_Sigma_x_yy(i,j);
  			ELD(Sigma_x_yy,index2) =InvDXDT_I*(
  											ELD(Sigma_x_yy,index2)*DXDT_I+
  											ELD(LambdaMatOverH,MaterialID)*
  											Diff);

			index2=Ind_Sigma_y_yy(i,j);
  			ELD(Sigma_y_yy,index2) =InvDXDT_J*(
  											ELD(Sigma_y_yy,index2)*DXDT_J+
  											ELD(LambdaMiuMatOverH,MaterialID)*
  											Diff2);


			index=Ind_Sigma_xx(i,j);
  			index2=Ind_Sigma_x_xx(i,j);
  			ELD(Sigma_yy,index)= ELD(Sigma_x_yy,index2) + ELD(Sigma_y_yy,index2);


  			index2=Ind_Sigma_x_xy(i,j);

  			Diff= i >0 && i<N1-2 ? CA*(EL(Vy,i+1,j)-EL(Vy,i,j)) -
  			                   CB*(EL(Vy,i+2,j)-EL(Vy,i-1,j))
  			                    :i<N1-1 ? EL(Vy,i+1,j)-EL(Vy,i,j):0;

  			ELD(Sigma_x_xy,index2) =InvDXDThp_I*(
  											ELD(Sigma_x_xy,index2)*DXDThp_I+
  											RigidityXY*
  											Diff);
			index2=Ind_Sigma_y_xy(i,j);

  			Diff=j > 0 && j<N2-2 ? CA*(EL(Vx,i,j+1)-EL(Vx,i,j) )-
  			                       CB*(EL(Vx,i,j+2)-EL(Vx,i,j-1) )
  			                       :j<N2-1 ? EL(Vx,i,j+1)-EL(Vx,i,j) :0;

  			ELD(Sigma_y_xy,index2) =InvDXDThp_J*(
  											ELD(Sigma_y_xy,index2)*DXDThp_J+
  											RigidityXY*
  											Diff);
			index=Ind_Sigma_xy(i,j);

			ELD(Sigma_xy,index)= ELD(Sigma_x_xy,Ind_Sigma_x_xy(i,j)) + ELD(Sigma_y_xy,index2);


		  }	   
	}
  	else
  	{
  		//We are in the center, no need to check any limits, the use of the PML simplify this
  		index=Ind_Sigma_xx(i,j);

		if (REQUIRES_2ND_ORDER_M(X))
			Dx=EL(Vx,i,j)-EL(Vx,i-1,j);
		else
			Dx=CA*(EL(Vx,i,j)-EL(Vx,i-1,j))-
				CB*(EL(Vx,i+1,j)-EL(Vx,i-2,j));

		if REQUIRES_2ND_ORDER_M(Y)
			Dy=EL(Vy,i,j)-EL(Vy,i,j-1);
		else
			Dy=CA*(EL(Vy,i,j)-EL(Vy,i,j-1))-
				CB*(EL(Vy,i,j+1)-EL(Vy,i,j-2));

		//We will use the particle displacement to estimate the acoustic pressure, and using the conservation of mass formula
		//We can use the stress kernel as V matrices are not being modified in this kernel,
		// and the spatial derivatives are the same ones required for pressure calculation
        // partial(p)/partial(t) = \rho c^2 div(V)
        //it is important to mention that the Python function will need still to multiply the result for the maps of (speed of sound)^2 and density, 
		// and divide by the spatial step.
		EL(Pressure,i,j)+=DT*(Dx+Dy);
        accum_p+=EL(Pressure,i,j);


  		LambdaMiu=ELD(LambdaMiuMatOverH,MaterialID)*(1.0+ELD(TauLong,MaterialID));
  		Miu=2.0*ELD(MiuMatOverH,MaterialID)*(1.0+ELD(TauShear,MaterialID));
  		OneOverTauSigma=ELD(OneOverTauSigma,MaterialID);
		dFirstPart=LambdaMiu*(Dx+Dy);
		
		if (ELD(TauLong,MaterialID)!=0.0 || ELD(TauShear,MaterialID)!=0.0) // We avoid unnecessary calculations if there is no attenuation
		{
			
			LambdaMiuComp=DT*ELD(LambdaMiuMatOverH,MaterialID)*(ELD(TauLong,MaterialID)*OneOverTauSigma);
			dFirstPartForR=LambdaMiuComp*(Dx+Dy);
			MiuComp=DT*2.0*ELD(MiuMatOverH,MaterialID)*(ELD(TauShear,MaterialID)*OneOverTauSigma);
			NextR=( (1-DT*0.5*OneOverTauSigma)*ELD(Rxx,index) - dFirstPartForR + MiuComp*(Dy))
  		    	  /(1+DT*0.5*OneOverTauSigma);

			ELD(Sigma_xx,index)+=	DT*(dFirstPart - Miu*(Dy) + 0.5*(ELD(Rxx,index) + NextR));
			ELD(Rxx,index)=NextR;
		}
		else
		{
			bAttenuating=0;
			ELD(Sigma_xx,index)+=	DT*(dFirstPart - Miu*(Dy));
		}
  		
	    accum_xx+=ELD(Sigma_xx,index);

		if (bAttenuating==1)
		{
  			NextR=( (1-DT*0.5*OneOverTauSigma)*ELD(Ryy,index) - dFirstPartForR + MiuComp*(Dx))
  		    	  /(1+DT*0.5*OneOverTauSigma);
				
  			ELD(Sigma_yy,index)+=	DT*(dFirstPart - Miu*(Dx) + 0.5*(ELD(Ryy,index) + NextR));
			ELD(Ryy,index)=NextR;
		}
		else
			ELD(Sigma_yy,index)+=	DT*(dFirstPart - Miu*(Dx));
      	
		accum_yy+=ELD(Sigma_yy,index);

  		index=Ind_Sigma_xy(i,j);
		if (RigidityXY!=0.0)
  		{
			  OneOverTauSigma=ELD(OneOverTauSigma,MaterialID);
              if (REQUIRES_2ND_ORDER_P(X))
                  Dx=EL(Vy,i+1,j)-EL(Vy,i,j);
              else
                  Dx=CA*(EL(Vy,i+1,j)-EL(Vy,i,j))-
                     CB*(EL(Vy,i+2,j)-EL(Vy,i-1,j));


              if (REQUIRES_2ND_ORDER_P(Y))
                  Dx+=EL(Vx,i,j+1)-EL(Vx,i,j);
              else
                  Dx+=CA*(EL(Vx,i,j+1)-EL(Vx,i,j))-
                      CB*(EL(Vx,i,j+2)-EL(Vx,i,j-1));

  			Miu=RigidityXY*(1.0+TauShearXY);

			if (TauShearXY!=0.0)
			{
				MiuComp=RigidityXY*(TauShearXY*OneOverTauSigma);
				NextR=( (1-DT*0.5*OneOverTauSigma)*ELD(Rxy,index) - DT*MiuComp*Dx)
  		          /(1+DT*0.5*OneOverTauSigma);
				ELD(Sigma_xy,index)+= DT*(Miu*Dx + 0.5*(ELD(Rxy,index) +NextR));
				ELD(Rxy,index)=NextR;
			}
			else
				ELD(Sigma_xy,index)+= DT*(Miu*Dx );
        	
			accum_xy+=ELD(Sigma_xy,index);

  		}
        // else
        //     ELD(Rxy,index)=0.0;

		if ((nStep < LengthSource) && TypeSource>=2) //Source is stress
  		{
  			index=IndN1N2(i,j,0);
  			source=ELD(SourceMap,index);
  			if (source>0)
  			{
  			  source--; //need to use C index
  			  value=ELD(SourceFunctions,nStep*NumberSources+source); 
				index=Ind_Sigma_xx(i,j);
                if ((TypeSource-2)==0)
                {
                    ELD(Sigma_xx,index)+=value*ELD(Ox,index);
                    ELD(Sigma_yy,index)+=value*ELD(Oy,index);
                }
                else
                {
                   ELD(Sigma_xx,index)=value*ELD(Ox,index);
                   ELD(Sigma_yy,index)=value*ELD(Oy,index);
                }

  			}
  		}
	
  	}
  }
  if (IsOnPML_I(i)==0 && IsOnPML_J(j)==0  && nStep>=SensorStart*SensorSubSampling)
  {
    accum_xx/=ZoneCount;
    accum_yy/=ZoneCount;
    accum_xy/=ZoneCount;


    CurZone=0;
    index=IndN1N2(i,j,0);
    index2=N1*N2;


    if ((SelRMSorPeak & SEL_RMS) ) //RMS was selected, and it is always at the location 0 of dim 5
    {
        if (IS_Sigmaxx_SELECTED(SelMapsRMSPeak))
            ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxx)+=accum_xx*accum_xx;
        if (IS_Sigmayy_SELECTED(SelMapsRMSPeak))
            ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmayy)+=accum_yy*accum_yy;
    
		if (IS_Pressure_SELECTED(SelMapsRMSPeak))
			ELD(SqrAcc,index+index2*IndexRMSPeak_Pressure)+=accum_p*accum_p;
        if (IS_Sigmaxy_SELECTED(SelMapsRMSPeak))
            ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxy)+=accum_xy*accum_xy;

		
    }
    if ((SelRMSorPeak & SEL_RMS) && (SelRMSorPeak & SEL_PEAK) ) //If both PEAK and RMS were selected we save in the far part of the array
        index+=index2*NumberSelRMSPeakMaps;
    if (SelRMSorPeak & SEL_PEAK)
    {
        if (IS_Sigmaxx_SELECTED(SelMapsRMSPeak))
            ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxx)=accum_xx>ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxx) ? accum_xx: ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxx);
        if (IS_Sigmayy_SELECTED(SelMapsRMSPeak))
            ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmayy)=accum_yy>ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmayy) ? accum_yy: ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmayy);
        if (IS_Pressure_SELECTED(SelMapsRMSPeak))
			ELD(SqrAcc,index+index2*IndexRMSPeak_Pressure)=accum_p > ELD(SqrAcc,index+index2*IndexRMSPeak_Pressure) ? accum_p :ELD(SqrAcc,index+index2*IndexRMSPeak_Pressure);
		if (IS_Sigmaxy_SELECTED(SelMapsRMSPeak))
            ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxy)=accum_xy>ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxy) ? accum_xy: ELD(SqrAcc,index+index2*IndexRMSPeak_Sigmaxy);
    }

  }
}

#if defined(CUDA)
extern "C" __global__ void MAIN_1_ParticleKernel(
#ifdef CUDA
#define __predecorator 
#else
#define __predecorator __global
#endif
__predecorator mexType *V_x_x_pr,
__predecorator mexType *V_y_x_pr,
__predecorator mexType *V_x_y_pr,
__predecorator mexType *V_y_y_pr,
__predecorator mexType *Vx_pr,
__predecorator mexType *Vy_pr,
__predecorator mexType *Rxx_pr,
__predecorator mexType *Ryy_pr,
__predecorator mexType *Rxy_pr,
__predecorator mexType *Sigma_x_xx_pr,
__predecorator mexType *Sigma_y_xx_pr,
__predecorator mexType *Sigma_x_yy_pr,
__predecorator mexType *Sigma_y_yy_pr,
__predecorator mexType *Sigma_x_xy_pr,
__predecorator mexType *Sigma_y_xy_pr,
__predecorator mexType *Sigma_xy_pr,
__predecorator mexType *Sigma_xx_pr,
__predecorator mexType *Sigma_yy_pr,
__predecorator mexType *SourceFunctions_pr,
__predecorator mexType * LambdaMiuMatOverH_pr,
__predecorator mexType * LambdaMatOverH_pr,
__predecorator mexType * MiuMatOverH_pr,
__predecorator mexType * TauLong_pr,
__predecorator mexType * OneOverTauSigma_pr,
__predecorator mexType * TauShear_pr,
__predecorator mexType * InvRhoMatH_pr,
__predecorator mexType * SqrAcc_pr,
__predecorator unsigned int * MaterialMap_pr,
__predecorator unsigned int * SourceMap_pr,
__predecorator mexType * Ox_pr,
__predecorator mexType * Oy_pr,
__predecorator mexType * Pressure_pr
			,unsigned int nStep,unsigned int TypeSource)
{
	_PT i = (_PT) (blockIdx.x * blockDim.x + threadIdx.x);
    _PT j = (_PT) (blockIdx.y * blockDim.y + threadIdx.y);

#endif
#ifdef OPENCL
__kernel void MAIN_1_ParticleKernel(
#ifdef CUDA
#define __predecorator 
#else
#define __predecorator __global
#endif
__predecorator mexType *V_x_x_pr,
__predecorator mexType *V_y_x_pr,
__predecorator mexType *V_x_y_pr,
__predecorator mexType *V_y_y_pr,
__predecorator mexType *Vx_pr,
__predecorator mexType *Vy_pr,
__predecorator mexType *Rxx_pr,
__predecorator mexType *Ryy_pr,
__predecorator mexType *Rxy_pr,
__predecorator mexType *Sigma_x_xx_pr,
__predecorator mexType *Sigma_y_xx_pr,
__predecorator mexType *Sigma_x_yy_pr,
__predecorator mexType *Sigma_y_yy_pr,
__predecorator mexType *Sigma_x_xy_pr,
__predecorator mexType *Sigma_y_xy_pr,
__predecorator mexType *Sigma_xy_pr,
__predecorator mexType *Sigma_xx_pr,
__predecorator mexType *Sigma_yy_pr,
__predecorator mexType *SourceFunctions_pr,
__predecorator mexType * LambdaMiuMatOverH_pr,
__predecorator mexType * LambdaMatOverH_pr,
__predecorator mexType * MiuMatOverH_pr,
__predecorator mexType * TauLong_pr,
__predecorator mexType * OneOverTauSigma_pr,
__predecorator mexType * TauShear_pr,
__predecorator mexType * InvRhoMatH_pr,
__predecorator mexType * SqrAcc_pr,
__predecorator unsigned int * MaterialMap_pr,
__predecorator unsigned int * SourceMap_pr,
__predecorator mexType * Ox_pr,
__predecorator mexType * Oy_pr,
__predecorator mexType * Pressure_pr
	, unsigned int nStep,
	unsigned int TypeSource)
{
	_PT i = (_PT) get_global_id(0);
	_PT j = (_PT) get_global_id(1);
	
#endif
#ifdef METAL
kernel void MAIN_1_ParticleKernel(
	METAL_PARAMS
	#ifndef METALCOMPUTE
  	_PT i = (_PT) gid.x;
  	_PT j = (_PT) gid.y;
	#else
  	_PT j = (_PT) ((gid )/N1);
  	_PT i = (_PT) (gid -j*N1);
	#endif
#endif

#if defined(OPENCL) || defined(METAL) || defined(CUDA)
if (i>=N1 || j >=N2  )
	return;
#endif
	_PT source;
	mexType value;
	mexType AvgInvRhoI;
	mexType Diff;
	mexType accum_x=0.0;
	mexType Dx;
	mexType accum_y=0.0;
	mexType AvgInvRhoJ;
	mexType Dy;

_PT index;
_PT index2;
_PT  CurZone;
	for (   CurZone=0;CurZone<ZoneCount;CurZone++)
		{
		  if (IsOnPML_I(i)==1 || IsOnPML_J(j)==1 )
			{
				index=Ind_MaterialMap(i,j);
				AvgInvRhoI=ELD(InvRhoMatH,ELD(MaterialMap,index));
				//In the PML
				// For coeffs. for V_x
				if (i<N1-1 && j <N2-1 )
				{
    				index=Ind_V_x_x(i,j);


		            Diff= i>0 && i<N1-2 ? CA*(EL(Sigma_xx,i+1,j)-EL(Sigma_xx,i,j))-
		                                  CB*(EL(Sigma_xx,i+2,j)-EL(Sigma_xx,i-1,j))
					                      :i<N1-1 ? EL(Sigma_xx,i+1,j)-EL(Sigma_xx,i,j):0;

					ELD(V_x_x,index) =InvDXDThp_I*(ELD(V_x_x,index)*DXDThp_I+
													AvgInvRhoI*
													Diff);

					index=Ind_V_y_x(i,j);
					Diff= j>1 && j<N2-1 ? CA*(EL(Sigma_xy,i,j)-EL(Sigma_xy,i,j-1))-
					                      CB*(EL(Sigma_xy,i,j+1)-EL(Sigma_xy,i,j-2))
					                      :j>0 && j<N2 ? EL(Sigma_xy,i,j)-EL(Sigma_xy,i,j-1):0;

					ELD(V_y_x,index) =InvDXDT_J*(
													ELD(V_y_x,index)*DXDT_J+
													AvgInvRhoI*
													Diff);

					
					index=Ind_V_x(i,j);
					index2=Ind_V_x_x(i,j);
					ELD(Vx,index)=ELD(V_x_x,index2)+ELD(V_y_x,index2);
		

				// For coeffs. for V_y

					index=Ind_V_x_y(i,j);

					Diff= i>1 && i<N1-1 ? CA *(EL(Sigma_xy,i,j)-EL(Sigma_xy,i-1,j)) -
					                      CB *(EL(Sigma_xy,i+1,j)-EL(Sigma_xy,i-2,j))
					                      :i>0 && i<N1 ? EL(Sigma_xy,i,j)-EL(Sigma_xy,i-1,j):0;

					ELD(V_x_y,index) =InvDXDT_I*(
													ELD(V_x_y,index)*DXDT_I+
													AvgInvRhoI*
													Diff);
					index=Ind_V_y_y(i,j);
					Diff= j>0 && j < N2-2 ? CA*( EL(Sigma_yy,i,j+1)-EL(Sigma_yy,i,j)) -
					                        CB*( EL(Sigma_yy,i,j+2)-EL(Sigma_yy,i,j-1))
					                        :j < N2-1 ? EL(Sigma_yy,i,j+1)-EL(Sigma_yy,i,j):0;

					ELD(V_y_y,index) =InvDXDThp_J*(
												ELD(V_y_y,index)*DXDThp_J+
												AvgInvRhoI*
												Diff);

					index=Ind_V_y(i,j);
					index2=Ind_V_y_y(i,j);
					ELD(Vy,index)=ELD(V_x_y,index2)+ELD(V_y_y,index2);


		
				 }

			}
			else
			{
				index=Ind_MaterialMap(i,j);
				AvgInvRhoI=0.5*(ELD(InvRhoMatH,EL(MaterialMap,i+1,j))+ELD(InvRhoMatH,ELD(MaterialMap,index)));
				
				Dx=CA*(EL(Sigma_xx,i+1,j)-EL(Sigma_xx,i,j))-
						CB*(EL(Sigma_xx,i+2,j)-EL(Sigma_xx,i-1,j));

				Dx+=CA*(EL(Sigma_xy,i,j)-EL(Sigma_xy,i,j-1))-
						CB*(EL(Sigma_xy,i,j+1)-EL(Sigma_xy,i,j-2));

				EL(Vx,i,j)+=DT*AvgInvRhoI*Dx;
				accum_x+=EL(Vx,i,j);
				//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
				AvgInvRhoJ=0.5*(ELD(InvRhoMatH,EL(MaterialMap,i,j+1))+ELD(InvRhoMatH,ELD(MaterialMap,index)));
				
				Dy=CA*(EL(Sigma_yy,i,j+1)-EL(Sigma_yy,i,j) )-
						CB*(EL(Sigma_yy,i,j+2)-EL(Sigma_yy,i,j-1));

				Dy+=CA*(EL(Sigma_xy,i,j)-EL(Sigma_xy,i-1,j))-
						CB*(EL(Sigma_xy,i+1,j)-EL(Sigma_xy,i-2,j));
				
				EL(Vy,i,j)+=DT*AvgInvRhoJ*Dy;
				accum_y+=EL(Vy,i,j);
				//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		}
  		if ((nStep < LengthSource) && TypeSource<2) //Source is particle displacement
  		{
			index=IndN1N2(i,j,0);
  			source=ELD(SourceMap,index);
  			if (source>0)
  			{
				source--; //need to use C index
  			  	value=ELD(SourceFunctions,nStep*NumberSources+source);
				if (TypeSource==0)
				{
					EL(Vx,i,j)+=value*ELD(Ox,index);
					EL(Vy,i,j)+=value*ELD(Oy,index);
				
				}
				else
				{
					EL(Vx,i,j)=value*ELD(Ox,index);
					EL(Vy,i,j)=value*ELD(Oy,index);
				}

  			}
  		}
		}
		if (IsOnPML_I(i)==0 && IsOnPML_J(j)==0  && nStep>=SensorStart*SensorSubSampling)
	    {
			if (ZoneCount>1)
			{
				accum_x/=ZoneCount;
				accum_y/=ZoneCount;
			}
			CurZone=0;
			index=IndN1N2(i,j,0);
			index2=N1*N2;
			if ((SelRMSorPeak & SEL_RMS) ) //RMS was selected, and it is always at the location 0 of dim 5
			{
				if (IS_Vx_SELECTED(SelMapsRMSPeak))
					ELD(SqrAcc,index+index2*IndexRMSPeak_Vx)+=accum_x*accum_x;
				if (IS_Vy_SELECTED(SelMapsRMSPeak))
					ELD(SqrAcc,index+index2*IndexRMSPeak_Vy)+=accum_y*accum_y;
			}
			if ((SelRMSorPeak & SEL_RMS) && (SelRMSorPeak & SEL_PEAK) ) //If both PEAK and RMS were selected we save in the far part of the array
					index+=index2*NumberSelRMSPeakMaps;
			if (SelRMSorPeak & SEL_PEAK)
			{
				if (IS_Vx_SELECTED(SelMapsRMSPeak))
						ELD(SqrAcc,index+index2*IndexRMSPeak_Vx)=accum_x > ELD(SqrAcc,index+index2*IndexRMSPeak_Vx) ? accum_x : ELD(SqrAcc,index+index2*IndexRMSPeak_Vx);
				if (IS_Vy_SELECTED(SelMapsRMSPeak))
						ELD(SqrAcc,index+index2*IndexRMSPeak_Vy)=accum_y > ELD(SqrAcc,index+index2*IndexRMSPeak_Vy) ? accum_y : ELD(SqrAcc,index+index2*IndexRMSPeak_Vy);
				
			}


		}
		
		
}

#if defined(CUDA)
extern "C" __global__ void SnapShot(unsigned int SelK,mexType * Snapshots_pr,mexType * Sigma_xx_pr,mexType * Sigma_yy_pr,unsigned int CurrSnap)
{
	_PT i = (_PT) (blockIdx.x * blockDim.x + threadIdx.x);
  _PT j = (_PT) (blockIdx.y * blockDim.y + threadIdx.y);
#endif
#ifdef OPENCL
__kernel void SnapShot(unsigned int SelK,__global mexType * Snapshots_pr,__global mexType * Sigma_xx_pr,__global mexType * Sigma_yy_pr,unsigned int CurrSnap)
{
  _PT i = (_PT) get_global_id(0);
  _PT j = (_PT) get_global_id(1);
#endif
#ifdef METAL
#define Sigma_xx_pr k_Sigma_xx_pr
#define Sigma_yy_pr k_Sigma_yy_pr

kernel void SnapShot(
	const device unsigned int *p_CONSTANT_BUFFER_UINT [[ buffer(0) ]],
	const device mexType * p_CONSTANT_BUFFER_MEX [[ buffer(1) ]],
	const device unsigned int *p_INDEX_MEX [[ buffer(2) ]],
	const device unsigned int *p_INDEX_UINT [[ buffer(3) ]],
	const device unsigned int *p_UINT_BUFFER [[ buffer(4) ]],
	device mexType * p_MEX_BUFFER_0 [[ buffer(5) ]],
	device mexType * p_MEX_BUFFER_1 [[ buffer(6) ]],
	device mexType * p_MEX_BUFFER_2 [[ buffer(7) ]],
	device mexType * p_MEX_BUFFER_3 [[ buffer(8) ]],
	device mexType * p_MEX_BUFFER_4 [[ buffer(9) ]],
	device mexType * p_MEX_BUFFER_5 [[ buffer(10) ]],
	device mexType * p_MEX_BUFFER_6 [[ buffer(11) ]],
	device mexType * p_MEX_BUFFER_7 [[ buffer(12) ]],
	device mexType * p_MEX_BUFFER_8 [[ buffer(13) ]],
	device mexType * p_MEX_BUFFER_9 [[ buffer(14) ]],
	device mexType * p_MEX_BUFFER_10 [[ buffer(15) ]],
	device mexType * p_MEX_BUFFER_11 [[ buffer(16) ]],
	device mexType * Snapshots_pr [[ buffer(17) ]],
	uint2 gid[[thread_position_in_grid]])

	{
	_PT i = (_PT) gid.x;
	_PT j = (_PT) gid.y;
#endif

    if (i>=N1 || j >=N2)
		return;
	// mexType accum=0.0;
	// for (unsigned int CurZone=0;CurZone<ZoneCount;CurZone++)
	// 	{
	// 		_PT index=Ind_Sigma_xx(i,j,(_PT)SelK);
	// 		accum+=(Sigma_xx_pr[index]+Sigma_yy_pr[index]+Sigma_zz_pr[index])/3.0;

	// 	}

	// 	Snapshots_pr[IndN1N2Snap(i,j)+CurrSnap*N1*N2]=accum/ZoneCount;
}

#if defined(CUDA)
extern "C" __global__ void SensorsKernel(
#ifdef CUDA
#define __predecorator 
#else
#define __predecorator __global
#endif
__predecorator mexType *V_x_x_pr,
__predecorator mexType *V_y_x_pr,
__predecorator mexType *V_x_y_pr,
__predecorator mexType *V_y_y_pr,
__predecorator mexType *Vx_pr,
__predecorator mexType *Vy_pr,
__predecorator mexType *Rxx_pr,
__predecorator mexType *Ryy_pr,
__predecorator mexType *Rxy_pr,
__predecorator mexType *Sigma_x_xx_pr,
__predecorator mexType *Sigma_y_xx_pr,
__predecorator mexType *Sigma_x_yy_pr,
__predecorator mexType *Sigma_y_yy_pr,
__predecorator mexType *Sigma_x_xy_pr,
__predecorator mexType *Sigma_y_xy_pr,
__predecorator mexType *Sigma_xy_pr,
__predecorator mexType *Sigma_xx_pr,
__predecorator mexType *Sigma_yy_pr,
__predecorator mexType *SourceFunctions_pr,
__predecorator mexType * LambdaMiuMatOverH_pr,
__predecorator mexType * LambdaMatOverH_pr,
__predecorator mexType * MiuMatOverH_pr,
__predecorator mexType * TauLong_pr,
__predecorator mexType * OneOverTauSigma_pr,
__predecorator mexType * TauShear_pr,
__predecorator mexType * InvRhoMatH_pr,
__predecorator mexType * SqrAcc_pr,
__predecorator unsigned int * MaterialMap_pr,
__predecorator unsigned int * SourceMap_pr,
__predecorator mexType * Ox_pr,
__predecorator mexType * Oy_pr,
__predecorator mexType * Pressure_pr
	,mexType * SensorOutput_pr,
	unsigned int * IndexSensorMap_pr,
	unsigned int nStep)
{
	unsigned int sj =blockIdx.x * blockDim.x + threadIdx.x;
#endif
#ifdef OPENCL
__kernel void SensorsKernel(
#ifdef CUDA
#define __predecorator 
#else
#define __predecorator __global
#endif
__predecorator mexType *V_x_x_pr,
__predecorator mexType *V_y_x_pr,
__predecorator mexType *V_x_y_pr,
__predecorator mexType *V_y_y_pr,
__predecorator mexType *Vx_pr,
__predecorator mexType *Vy_pr,
__predecorator mexType *Rxx_pr,
__predecorator mexType *Ryy_pr,
__predecorator mexType *Rxy_pr,
__predecorator mexType *Sigma_x_xx_pr,
__predecorator mexType *Sigma_y_xx_pr,
__predecorator mexType *Sigma_x_yy_pr,
__predecorator mexType *Sigma_y_yy_pr,
__predecorator mexType *Sigma_x_xy_pr,
__predecorator mexType *Sigma_y_xy_pr,
__predecorator mexType *Sigma_xy_pr,
__predecorator mexType *Sigma_xx_pr,
__predecorator mexType *Sigma_yy_pr,
__predecorator mexType *SourceFunctions_pr,
__predecorator mexType * LambdaMiuMatOverH_pr,
__predecorator mexType * LambdaMatOverH_pr,
__predecorator mexType * MiuMatOverH_pr,
__predecorator mexType * TauLong_pr,
__predecorator mexType * OneOverTauSigma_pr,
__predecorator mexType * TauShear_pr,
__predecorator mexType * InvRhoMatH_pr,
__predecorator mexType * SqrAcc_pr,
__predecorator unsigned int * MaterialMap_pr,
__predecorator unsigned int * SourceMap_pr,
__predecorator mexType * Ox_pr,
__predecorator mexType * Oy_pr,
__predecorator mexType * Pressure_pr
		, __global mexType * SensorOutput_pr,
			__global unsigned int * IndexSensorMap_pr,
			unsigned int nStep)
{
	_PT sj =(_PT) get_global_id(0);
#endif
#ifdef METAL

#define IndexSensorMap_pr k_IndexSensorMap_pr

#ifndef METALCOMPUTE
kernel void SensorsKernel(
	const device unsigned int *p_CONSTANT_BUFFER_UINT [[ buffer(0) ]],
	const device mexType * p_CONSTANT_BUFFER_MEX [[ buffer(1) ]],
	const device unsigned int *p_INDEX_MEX [[ buffer(2) ]],
	const device unsigned int *p_INDEX_UINT [[ buffer(3) ]],
	const device unsigned int *p_UINT_BUFFER [[ buffer(4) ]],
	device mexType * p_MEX_BUFFER_0 [[ buffer(5) ]],
	device mexType * p_MEX_BUFFER_1 [[ buffer(6) ]],
	device mexType * p_MEX_BUFFER_2 [[ buffer(7) ]],
	device mexType * p_MEX_BUFFER_3 [[ buffer(8) ]],
	device mexType * p_MEX_BUFFER_4 [[ buffer(9) ]],
	device mexType * p_MEX_BUFFER_5 [[ buffer(10) ]],
	device mexType * p_MEX_BUFFER_6 [[ buffer(11) ]],
	device mexType * p_MEX_BUFFER_7 [[ buffer(12) ]],
	device mexType * p_MEX_BUFFER_8 [[ buffer(13) ]],
	device mexType * p_MEX_BUFFER_9 [[ buffer(14) ]],
	device mexType * p_MEX_BUFFER_10 [[ buffer(15) ]],
	device mexType * p_MEX_BUFFER_11 [[ buffer(16) ]],
	uint gid[[thread_position_in_grid]])
#else
kernel void SensorsKernel(
	const device unsigned int *p_CONSTANT_BUFFER_UINT [[ buffer(0) ]],
	const device unsigned int *p_INDEX_MEX [[ buffer(1) ]],
	const device unsigned int *p_INDEX_UINT [[ buffer(2) ]],
	const device unsigned int *p_UINT_BUFFER [[ buffer(3) ]],
	device mexType * p_MEX_BUFFER_0 [[ buffer(4) ]],
	device mexType * p_MEX_BUFFER_1 [[ buffer(5) ]],
	device mexType * p_MEX_BUFFER_2 [[ buffer(6) ]],
	device mexType * p_MEX_BUFFER_3 [[ buffer(7) ]],
	device mexType * p_MEX_BUFFER_4 [[ buffer(8) ]],
	device mexType * p_MEX_BUFFER_5 [[ buffer(9) ]],
	device mexType * p_MEX_BUFFER_6 [[ buffer(10) ]],
	device mexType * p_MEX_BUFFER_7 [[ buffer(11) ]],
	device mexType * p_MEX_BUFFER_8 [[ buffer(12) ]],
	device mexType * p_MEX_BUFFER_9 [[ buffer(13) ]],
	device mexType * p_MEX_BUFFER_10 [[ buffer(14) ]],
	device mexType * p_MEX_BUFFER_11 [[ buffer(15) ]],
	uint gid[[thread_position_in_grid]])
#endif
{
	_PT sj = (_PT) gid;
#endif

	if (sj>=(_PT) NumberSensors)
		return;
_PT index=(((_PT)nStep)/((_PT)SensorSubSampling)-((_PT)SensorStart))*((_PT)NumberSensors)+(_PT)sj;
_PT  i,j;
_PT index2,index3,
    subarrsize=(((_PT)NumberSensors)*(((_PT)TimeSteps)/((_PT)SensorSubSampling)+1-((_PT)SensorStart)));
index2=IndexSensorMap_pr[sj]-1;

mexType accumX=0.0,accumY=0.0,
        accumXX=0.0, accumYY=0.0, 
        accumXY=0.0, accum_p=0, accum_p_gx=0,accum_p_gy=0;
for (_PT CurZone=0;CurZone<ZoneCount;CurZone++)
  {
    i=index2%(N1);
    j=index2/N1;

    if ( IS_Vx_SELECTED(SelMapsSensors))
        accumX+=EL(Vx,i,j);
    if ( IS_Vy_SELECTED(SelMapsSensors))
        accumY+=EL(Vy,i,j);

    index3=Ind_Sigma_xx(i,j);
  #ifdef METAL
    //No idea why in this kernel the ELD(SigmaXX...) macros do not expand correctly
    //So we go a bit more manual
  if (IS_Sigmaxx_SELECTED(SelMapsSensors))
      accumXX+=k_Sigma_xx_pr[index3];
  if (IS_Sigmayy_SELECTED(SelMapsSensors))
      accumYY+=k_Sigma_yy_pr[index3];
  if (IS_Pressure_SELECTED(SelMapsSensors))
      accum_p+=k_Pressure_pr[index3];
  if (IS_Pressure_Gx_SELECTED(SelMapsSensors))
      accum_p_gx+=(k_Pressure_pr[Ind_Sigma_xx(i+1,j)]-k_Pressure_pr[Ind_Sigma_xx(i-1,j)])*0.5;
  if (IS_Pressure_Gy_SELECTED(SelMapsSensors))
      accum_p_gy+=(k_Pressure_pr[Ind_Sigma_xx(i,j+1)]-k_Pressure_pr[Ind_Sigma_xx(i,j-1)])*0.5;
  index3=Ind_Sigma_xy(i,j);
  if (IS_Sigmaxy_SELECTED(SelMapsSensors))
      accumXY+=k_Sigma_xy_pr[index3];
  
  #else
    if (IS_Sigmaxx_SELECTED(SelMapsSensors))
        accumXX+=ELD(Sigma_xx,index3);
    if (IS_Sigmayy_SELECTED(SelMapsSensors))
        accumYY+=ELD(Sigma_yy,index3);
    if (IS_Pressure_SELECTED(SelMapsSensors))
        accum_p+=ELD(Pressure,index3);
    if (IS_Pressure_Gx_SELECTED(SelMapsSensors))
      accum_p_gx+=(Pressure_pr[Ind_Sigma_xx(i+1,j)]-Pressure_pr[Ind_Sigma_xx(i-1,j)])*0.5;
    if (IS_Pressure_Gy_SELECTED(SelMapsSensors))
      accum_p_gy+=(Pressure_pr[Ind_Sigma_xx(i,j+1)]-Pressure_pr[Ind_Sigma_xx(i,j-1)])*0.5;
    index3=Ind_Sigma_xy(i,j);
    if (IS_Sigmaxy_SELECTED(SelMapsSensors))
        accumXY+=ELD(Sigma_xy,index3);
   #endif
  }
accumX/=ZoneCount;
accumY/=ZoneCount;
accumXX/=ZoneCount;
accumYY/=ZoneCount;
accumXY/=ZoneCount;
accum_p/=ZoneCount;
//ELD(SensorOutput,index)=accumX*accumX+accumY*accumY+accumZ*accumZ;
if (IS_Vx_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Vx)=accumX;
if (IS_Vy_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Vy)=accumY;
if (IS_Sigmaxx_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Sigmaxx)=accumXX;
if (IS_Sigmayy_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Sigmayy)=accumYY;
if (IS_Sigmaxy_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Sigmaxy)=accumXY;
if (IS_Pressure_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Pressure)=accum_p;
if (IS_Pressure_Gx_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Pressure_gx)=accum_p_gx;
if (IS_Pressure_Gy_SELECTED(SelMapsSensors))
    ELD(SensorOutput,index+subarrsize*IndexSensor_Pressure_gy)=accum_p_gy;


}