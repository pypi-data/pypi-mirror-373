# MIT License

# Copyright (c) 2024 dechin

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Example
$ python3 -m cyfes -i /home/Data/xyz_bias.txt -o ./z.cub
$ python3 -m cyfes -i /home/Data/xyz_bias.txt -e 5.0 -g 20,20,20 -o ./z.cub
"""
import os
import warnings
warnings.filterwarnings('ignore')


if __name__ == '__main__':
    import argparse
    import logging
    import numpy as np
    from pathlib import Path
    from cyfes import read_out, save_cube, save_dat
    from cyfes.utils import cube2xyz, save2dat
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", help="Set the input record file path.")
    parser.add_argument("-ic", help="Set the cv index of input record file. Default: 0,1,2", default='0,1,2')
    parser.add_argument("-ib", help="Set the bias index of input record file. Default: 3", default='3')
    parser.add_argument("-s", help="CV length. Default: None", default=None)
    parser.add_argument("-e", help="Edge length. Default: 0.0", default='0.0')
    parser.add_argument("-g", help="Grid numbers. Default: 10,10,10", default='10,10,10')
    parser.add_argument("-o", help="Set the output FES file path.")
    parser.add_argument("-odat", help="Set the dat output file path.", default=None)
    parser.add_argument("-no_bias", help="Do not use the bias from input file. Default: false", default='false')
    parser.add_argument("-f32", help="Use float32. Default: false", default='false')
    parser.add_argument("-sigma", help="Sigma value when calculating FES. Default: 0.3", default='0.3')
    parser.add_argument("-device", help="Set the device ids separated with commas. Default: 0", default='0')
    parser.add_argument("-a", help="Multiplier of FES grid values.", default='1')
    parser.add_argument("-b", help="Shift of FES grid values.", default='0')
    parser.add_argument("-cmin", help="The minimum value of cv. Example: 0,0,0", default=None)
    parser.add_argument("-cmax", help="The maximum value of cv. Example: 100,100,100", default=None)
    parser.add_argument("-intg", help="Set the edge of minimum and maximum cv to interger. Default: false", default='false')
    # parser.add_argument("-Ang", help="Use the length unit of angstrom. Default: 0", default='0')

    args = parser.parse_args()

    a_factor = float(args.a)
    b_factor = float(args.b)
    # use_angstrom = bool(args.Ang)

    logging.info("[CyFES] Start to initialize parameters")
    input_name = args.i
    if input_name is None:
        raise ValueError("The input file path can not be blank!")
    postfix = input_name.split('.')[-1]

    output_name = args.o
    if output_name is None:
        output_name = input_name.replace('.{}'.format(postfix), 
                                         '_fes.cub')
    if not os.path.exists(str(Path(output_name).parent)):
        raise ValueError("The file path {} does not exist.".format(output_name))
    
    dat_name = args.odat
    if dat_name is None:
        pass
    else:
        if not os.path.exists(str(Path(output_name).parent)):
            raise ValueError("The file path {} does not exist.".format(output_name))

    if args.f32.lower() == 'false':
        from cyfes import FastPathFES as PathFES
        DTYPE = np.float64
    else:
        from cyfes import FastPathFES_f32 as PathFES
        DTYPE = np.float32

    cv_index = [int(x) for x in args.ic.split(',')]
    bias_index = int(args.ib)
    sigma = float(args.sigma)
    device_ids = np.array([int(idx) for idx in args.device.split(',')], np.int32)
    use_intg = args.intg.lower() == 'true'
    
    cv_size = None
    if args.s is not None:
        cv_size = int(args.s)

    bw = np.ones((3, ), dtype=DTYPE) * sigma

    if postfix == 'txt':
        cv = read_out(input_name, idx=cv_index, hat_lines=0, max_size=cv_size)
        if args.no_bias.lower() == 'true':
            bias = np.zeros((cv.shape[-2], ), dtype=DTYPE)
        else:
            bias = read_out(input_name, idx=bias_index, hat_lines=0, max_size=cv_size)
    elif postfix == 'csv':
        cv = read_out(input_name, idx=cv_index, hat_lines=0, max_size=cv_size, dlm=',')
        if args.no_bias.lower() == 'true':
            bias = np.zeros((cv.shape[-2], ), dtype=DTYPE)
        else:
            bias = read_out(input_name, idx=bias_index, hat_lines=0, max_size=cv_size, dlm=',')
    elif postfix == 'xyz':
        cv = read_out(input_name, idx=cv_index, hat_lines=0, max_size=cv_size)
        if args.no_bias.lower() == 'true':
            bias = np.zeros((cv.shape[-2], ), dtype=DTYPE)
        else:
            bias = read_out(input_name, idx=bias_index, hat_lines=0, max_size=cv_size)
    else:
        raise ValueError("File format {} is not supported for now!".format(postfix))
    
    cv = cv.astype(DTYPE)
    logging.info("[CyFES] CV {}".format(cv.shape))
    bias = bias.astype(DTYPE)
    logging.info("[CyFES] Bias {}".format(bias.shape))
    edge = float(args.e)
    grid_num = [int(g)+1 for g in args.g.split(',')]
    if args.cmin is None:
        cv_min = cv.min(axis=-2) - edge
    else:
        cv_min = np.array([float(v) for v in args.cmin.split(',')], dtype=np.float32) - edge
    if args.cmax is None:
        cv_max = cv.max(axis=-2) + edge
    else:
        cv_max = np.array([float(v) for v in args.cmax.split(',')], dtype=np.float32) + edge
    if use_intg:
        cv_min = np.floor(cv_min)
        cv_max = np.ceil(cv_max)
    logging.info("[CyFES] Cube origin crd {}".format(cv_min))
    logging.info("[CyFES] Cube final crd {}".format(cv_max))
    x_grids = np.linspace(cv_min[0], cv_max[0], grid_num[0])
    y_grids = np.linspace(cv_min[1], cv_max[1], grid_num[1])
    z_grids = np.linspace(cv_min[2], cv_max[2], grid_num[2])
    xx, yy, zz = np.meshgrid(x_grids, y_grids, z_grids)

    path = np.hstack((xx.reshape((-1, 1)), yy.reshape((-1, 1)), zz.reshape((-1, 1)))).astype(DTYPE)
    logging.info("[CyFES] Grids {}".format(path.shape))
    logging.info("[CyFES] BandWidth {}".format(bw))

    logging.info("[CyFES] Start to calculate FES")
    cv /= bw
    rpath = path / bw
    Z = np.asarray(PathFES(rpath, cv, bw, bias)).reshape((grid_num[0], grid_num[1], grid_num[2])).swapaxes(0,1).flatten()
    logging.info("[CyFES] Writting FES into file {}".format(os.path.abspath(output_name)))

    Z_clip = a_factor * Z + b_factor
    Z_clip = np.clip(Z_clip, -450, 450)
    save_cube(output_name,
              cv_min,
              grid_num[0], x_grids[1] - x_grids[0],
              grid_num[1], y_grids[1] - y_grids[0],
              grid_num[2], z_grids[1] - z_grids[0],
              Z_clip,
              use_bohr=True)

    if dat_name is not None:
        logging.info("[CyFES] Writting FES into file {}".format(os.path.abspath(dat_name)))
        origin, values, spacing_vec = cube2xyz(output_name)
        success = save2dat(dat_name, spacing_vec, origin, values)

    logging.info("[CyFES] Task complete :)")
