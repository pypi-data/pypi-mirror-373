// MIT License

// Copyright (c) 2024 dechin

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#include <stdio.h>
#include <cuda_runtime.h>

struct CRD{
    double x, y, z;
};

struct PATH{
    CRD crds;
};

extern "C" int GetWeight(int CV_LENGTH, double* bias, double shift, double* weight);
extern "C" int GetDist(int CV_LENGTH, CRD* crd, PATH* cv, double* dis);
extern "C" int GaussGetDist(int CV_LENGTH, CRD* crd, PATH* cv, double* dis);
extern "C" int GaussGetDistHeight(int CV_LENGTH, CRD* crd, PATH* cv, double* dis, double* height);
extern "C" PATH* StickCv(int CV_LENGTH, PATH* cv, int device_id);
extern "C" int ReleaseCv(PATH* cv_device, int device_id);
extern "C" int GaussGetDistHeightDevice(int CV_LENGTH, CRD* crd, PATH* cv_device, double* dis, double* height);
extern "C" int GaussGetDistHeightStream(int CV_LENGTH, CRD* crd, PATH* cv_device, double* dis, double* height, cudaStream_t Stream);
extern "C" int GaussHeightDevice(int CV_LENGTH, CRD* crd, PATH* cv_device, double* dis, double* height, int device_id, cudaStream_t Stream);
