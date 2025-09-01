import re
import os
import numpy as np
from .masking import image_by_windows
import mcemtools
from lognflow import printprogress
import scipy
from itertools import product

def channel_to_image(image_by_ch, detector_response):
    n_ch, _, _ = detector_response.shape
    n_ch_ = len(image_by_ch)
    assert n_ch_ == n_ch, 'image_by_ch should have same number of channels as detector_response'
    img = (image_by_ch[:, None, None] * detector_response).sum(0)
    return img

def load_dm4(filename):
    from hyperspy.api import load as hyperspy_api_load
    return hyperspy_api_load(filename)

def open_muSTEM_binary(filename):
    '''opens binary with name filename outputted from the muSTEM software
        This peice of code is modified from muSTEM repo.
    '''
    filename = pathlib.Path(filename)
    assert filename.is_file(), f'{filename.absolute()} does not exist'
    m = re.search('([0-9]+)x([0-9]+)',filename)
    if m:
        y = int(m.group(2))
        x = int(m.group(1))
    #Get file size and intuit datatype
    size =  os.path.getsize(filename)
    if (size/(y*x) == 4):
        d_type = '>f4'
    elif(size/(y*x) == 8):
        d_type = '>f8'
    #Read data and reshape as required.
    return np.reshape(np.fromfile(filename, dtype = d_type),(y,x))

def load_raw(filename, scanSize: tuple[int, int], detSize: tuple[int, int]):
    dt = np.dtype([('data',  f'({detSize[0]},{detSize[1]})single'),
                   ('footer',f'{scanSize[0]}single')])
    data = np.fromfile(file=filename,dtype=dt)["data"].reshape(scanSize+detSize)
    return data

class mesh_maker_2D:
    def __init__(self, input_image, ground_truth = None):
        
        if ground_truth is None:
            ground_truth = input_image.copy()
        
        self.input_image_shape = input_image.shape
        self.n_pts = self.input_image_shape[0] * self.input_image_shape[1]
        xx, yy = np.meshgrid(np.arange(self.input_image_shape[1], dtype='int'),
                             np.arange(self.input_image_shape[0], dtype='int'))
        xx = xx.ravel()
        xx = xx - xx.mean()
        xx = xx / xx.std()
        yy = yy.ravel()
        yy = yy - yy.mean()
        yy = yy / yy.std()
        
        self.X_in = np.array([xx, yy]).T.astype('float32')
        
        self.Y_lable = input_image.copy().ravel().astype('float32')
        self.Y_lable_mean = self.Y_lable.mean()
        self.Y_lable -= self.Y_lable_mean
        self.Y_lable /= self.Y_lable.std()
        self.Y_lable = np.array([self.Y_lable]).swapaxes(0,1)
        
        self.GNDTruth = ground_truth.copy().ravel().astype('float32')
        self.GNDTruth_mean = self.GNDTruth.mean()
        self.GNDTruth -= self.GNDTruth_mean
            
    def dist2Truth(self, pred, ind):
        return np.fabs(pred - self.GNDTruth[ind])
    
    def dist2label(self, pred, ind):
        return np.fabs(pred - self.Y_lable[ind])
    
    def reconstruct(self, outimg_viewed):
        return outimg_viewed.reshape(*self.input_image_shape)

    def __call__(self, inds):
        try:
            _ = inds.shape[0]
        except:
            inds = np.array([inds])
        return(self.X_in[inds], self.Y_lable[inds])

def mask_random_pixels(inimg_set, mask_rate, random_function = np.zeros):
    """
    """
    inimg_set = inimg_set.copy()
    for imgcnt, inimg in enumerate(inimg_set):
        inimg = inimg.squeeze()
        nprange = np.arange(inimg.size).astype('int')
        np.random.shuffle(nprange)
        mask_vec = np.ones(nprange.shape)
        mask_vec[nprange[int(mask_rate*inimg.size):]] = 0
        mask = mask_vec.reshape(*inimg.shape)
        inimg[mask == 0] = random_function((mask == 0).sum())
        inimg_set[imgcnt] = inimg.copy()
    return inimg_set
    
class data_maker_2D:
    def __init__(self, inimg, groundtruth, win_shape,
                 skip = (1,1), mask_rate = 0.5):
        assert inimg.shape == groundtruth.shape
        
        self.inimg_mean = inimg.mean()
        
        self.mask_rate = mask_rate
        inimg = inimg.astype('float32')
        self.n_r, self.n_c = inimg.shape
        
        self.imbywin = image_by_windows(
            inimg.shape, win_shape, skip, method = 'fixed')
        self.Y_label = self.imbywin.image2views(inimg).copy()
        self.Y_label = np.array([self.Y_label]).swapaxes(0, 1)

        self.GNDTruth = self.imbywin.image2views(groundtruth).copy()
        self.GNDTruth = np.array([self.GNDTruth]).swapaxes(0, 1)
        
        self.n_pts = self.imbywin.n_pts

        self.randomize()

    def randomize(self):
        self.X_in = self.Y_label.copy()
        for cnt, y_lbl in enumerate(self.Y_label):
            self.X_in[cnt] = mask_random_pixels(y_lbl, self.mask_rate)

    def reconstruct(self, outimg_viewed):
        return self.imbywin.views2image(outimg_viewed)
            
    def dist2Truth(self, pred, ind):
        return np.linalg.norm(pred - self.GNDTruth[ind])
    
    def dist2label(self, pred, ind):
        return np.linalg.norm(pred - self.Y_label[ind])
    
    def __call__(self, inds):
        try:
            _ = inds.shape[0]
        except:
            inds = np.array([inds])
        return(self.X_in[inds], self.Y_label[inds])

def np_random_poisson_no_zeros(img):
    img_noisy = 0*img.copy()
    while img_noisy.sum() == 0:
        img_noisy = np.random.poisson(img).astype('float32')
    return img_noisy

class data_maker_4D:
    def __init__(self, inimg, groundtruth, len_side = 3,
                 trainable_area_I4D = None):
        
        assert len_side == (len_side//2)*2 + 1,\
            'data_maker_I4D:len_side should be odd'
        self.len_side = len_side
        self.edgew = len_side // 2
        self.inimg_shape = inimg.shape
        n_x, n_y, n_r, n_c = inimg.shape
        self.n_x, self.n_y, self.n_r, self.n_c = inimg.shape
        self.dtype = inimg.dtype

        self.imbywin = mcemtools.image_by_windows(
            (n_x, n_y), (len_side, len_side), method = 'fixed')
        
        self.mask_range = np.ones((len_side, len_side), dtype = 'int')
        self.mask_range[len_side //2, len_side // 2] = 0
        print('mask_range:'); print(self.mask_range)
        self.mask_range = self.mask_range.ravel()
        
        inimg_viewed = self.imbywin.image2views(groundtruth)
        inimg_viewed = inimg_viewed.reshape(
            inimg_viewed.shape[0], self.len_side**2, self.n_r, self.n_c)
        self.GNDTruth = inimg_viewed[:,  self.mask_range == 0].copy()
                
        self.update(inimg)

        self.groundtruth_mu = self.reconstruct2D(
            self.GNDTruth.sum((1, 2, 3)).squeeze())
        self.groundtruth_PACBED = self.GNDTruth.sum((0, 1)).squeeze()
        self.noisy_mu = self.reconstruct2D(
            self.Y_label.sum((1, 2, 3)).squeeze())
        self.noisy_PACBED = self.Y_label.sum((0, 1)).squeeze()
        self.cropped_shape = (n_x - len_side , n_y - len_side, n_r, n_c)
        self.xx = self.imbywin.grid_rows.ravel() + len_side // 2
        self.yy = self.imbywin.grid_clms.ravel() + len_side // 2
        self.n_pts = len(self.imbywin)
        
        if trainable_area_I4D is not None:
            trainable_area = np.arange(n_x* n_y).reshape(n_x, n_y)
            self.trainable_inds = trainable_area[trainable_area_I4D > 0]
    
    def update(self, inimg, update_label = True):
        inimg_viewed = self.imbywin.image2views(inimg)
        inimg_viewed = inimg_viewed.reshape(
            inimg_viewed.shape[0], self.len_side**2, self.n_r, self.n_c)
        
        self.X_in = inimg_viewed[:, self.mask_range == 1]
        if update_label:
            self.Y_label = inimg_viewed[:, self.mask_range == 0]
        
    def reconstruct2D(self, outimg_viewed, indices = None):
        # The input shape is grid.npts
        img = self.imbywin.views2image(
                outimg_viewed, include_inds = indices, method = 'fixed',
                win_shape = (1, 1))
        return img[self.edgew:-self.edgew, self.edgew:-self.edgew]
    
    def reconstruct4D(self, viewed4D, indices = None):
        # The input shape is grid.npts, 1, n_r, n_c
        assert viewed4D.shape[1] == 1
        viewed4D = np.expand_dims(viewed4D, 2)
        img4d = self.imbywin.views2image(viewed4D, indices, method = 'fixed',
                                         win_shape = (1, 1))
        return img4d
                
    def dist2Truth(self, pred, ind):
        return np.linalg.norm(pred - self.GNDTruth[ind])
    
    def dist2label(self, pred, ind):
        return np.linalg.norm(pred - self.Y_label[ind])    

    def __call__(self, inds):
        try:
            _ = inds.shape[0]
        except:
            inds = np.array([inds])
        return(self.X_in[inds], self.Y_label[inds])
    
class feature_maker_4D:
    def __init__(self, inimg, groundtruth, len_side = 3,
                 trainable_area_I4D = None):
        assert len_side == (len_side//2)*2 + 1,\
            'data_maker_I4D:len_side should be odd'
        self.len_side = len_side
        self.inimg_shape = inimg.shape
        n_x, n_y, n_r, n_c = inimg.shape
        self.n_r = n_r
        self.n_c = n_c
        self.n_x = n_x
        self.n_y = n_y
        grid_x = np.arange(len_side // 2, n_x - len_side // 2, 1, dtype='int')
        grid_y = np.arange(len_side // 2, n_y - len_side // 2, 1, dtype='int')
        yy, xx = np.meshgrid(grid_y, grid_x)
        xx = xx.ravel()
        yy = yy.ravel()
        n_pts = xx.shape[0]
        self.n_xx = grid_x.shape[0]
        self.n_yy = grid_y.shape[0]
        self.n_pts = n_pts
        self.X_in     = \
            np.zeros((n_pts, len_side*len_side - 1, n_r, n_c), dtype='float32')
        self.Y_label  = \
            np.zeros((n_pts,                 1, n_r, n_c), dtype='float32')
        self.GNDTruth = \
            np.zeros((n_pts,                 1, n_r, n_c), dtype='float32')
        self.xx = xx.copy()
        self.yy = yy.copy()
        mask_range = np.ones(len_side*len_side).astype('int')
        mask_range[(len_side * len_side) // 2] = 0        
        self.mask_range = mask_range.copy()
        print(f'mask_range:{mask_range}')
                
        for gpt_cnt in range(n_pts):     
            a_tile = groundtruth[
                xx[gpt_cnt] - len_side // 2 : 
                    xx[gpt_cnt] + len_side // 2 + 1,
                yy[gpt_cnt] - len_side // 2 : 
                    yy[gpt_cnt] + len_side // 2 + 1].copy()
            a_tile = a_tile.reshape(len_side*len_side, n_r, n_c)
            self.GNDTruth[gpt_cnt] = a_tile[mask_range == 0].copy()

        self.update(inimg)

        self.groundtruth_mu = self.reconstruct2D(
            self.GNDTruth.sum(3).sum(2).sum(1).squeeze())
        self.groundtruth_PACBED = self.GNDTruth.sum(1).sum(0).squeeze()
        self.noisy_mu = self.reconstruct2D(
            self.Y_label.sum(3).sum(2).sum(1).squeeze())
        self.noisy_PACBED = self.Y_label.sum(1).sum(0).squeeze()
        self.cropped_shape = (grid_x.shape[0], grid_y.shape[0], n_r, n_c)
        
        self.trainable_inds = np.arange(self.n_pts, dtype='int')
    
    def filter(self, mch_img):                                                   ############################
        for cnt, img in enumerate(mch_img):
            
            img = np_random_poisson_no_zeros(img)
            # thresh = np.percentile(img, (cnt + 1) * 7)
            # img[img<thresh] = 0
            # img[img>=thresh] = 1
            
            mch_img[cnt] = img.copy()
        return mch_img
    
    def update(self, inimg):
        for gpt_cnt in range(self.n_pts):
            a_tile = inimg[
                self.xx[gpt_cnt] - self.len_side // 2 : 
                    self.xx[gpt_cnt] + self.len_side // 2 + 1,
                self.yy[gpt_cnt] - self.len_side // 2 : 
                    self.yy[gpt_cnt] + self.len_side // 2 + 1].copy()
            a_tile = a_tile.reshape(
                self.len_side*self.len_side, self.n_r, self.n_c)
            self.X_in[gpt_cnt] = np.tile(a_tile[self.mask_range == 0].copy(), (1, 8, 1, 1)) ###########################
            self.X_in[gpt_cnt] = self.filter(self.X_in[gpt_cnt])                         #####################################
            self.Y_label[gpt_cnt] = a_tile[self.mask_range == 0].copy()
    
    def reconstruct1D(self, out1D_viewed):
        n_pts = self.xx.shape[0]
        out1D_viewed = out1D_viewed.squeeze()
        output = np.zeros((self.inimg_shape[0],
                           self.inimg_shape[1], 2), dtype='float32')
        for gpt_cnt in range(n_pts):
            output[self.xx[gpt_cnt], self.yy[gpt_cnt]] = \
                out1D_viewed[gpt_cnt].copy()
        output = output[self.len_side//2 : -(self.len_side//2),
                        self.len_side//2 : -(self.len_side//2)].copy()
        return output              
    
    def reconstruct2D(self, outimg_viewed, indices = None):
        _outimg_viewed = np.zeros((self.n_xx * self.n_yy), dtype='float32')
        if indices is None:
            _outimg_viewed = outimg_viewed.copy()
        else:
            _outimg_viewed[indices] = outimg_viewed.copy()
        return _outimg_viewed.reshape(self.n_xx, self.n_yy)
    
    def reconstruct4D(self, viewed4D, indices = None):
        if indices is None:
            indices = range(self.xx.shape[0])
        viewed4D = viewed4D.squeeze()
        output = np.zeros(self.inimg_shape, dtype='float32')
        for gpt_cnt, gpt_ind in enumerate(indices):
            output[self.xx[gpt_ind], self.yy[gpt_ind]] = \
                viewed4D[gpt_cnt].copy()
        output = output[self.len_side//2 : -(self.len_side//2),
                        self.len_side//2 : -(self.len_side//2)].copy()
        return output              
        
    def dist2Truth(self, pred, ind):
        return np.linalg.norm(pred - self.GNDTruth[ind])
    
    def dist2label(self, pred, ind):
        return np.linalg.norm(pred - self.Y_label[ind])    

    def __call__(self, inds):
        try:
            _ = inds.shape[0]
        except:
            inds = np.array([inds])
        return(self.X_in[inds], self.Y_label[inds])    

def np_random_poisson_no_zeros(data4D_nonoise):
    data4D_noisy = 0*data4D_nonoise.copy()
    print('All patterns must have at least one electron', end = '')
    while (data4D_noisy.sum((2, 3)) == 0).sum() > 0:
        ne_ele_patterns = data4D_noisy.sum((2, 3)) == 0
        _data4D_noisy = np.random.poisson(
            data4D_nonoise[ne_ele_patterns]).astype('float32')
        data4D_noisy[ne_ele_patterns] = _data4D_noisy.copy()
        print(f', {(data4D_noisy.sum((2, 3)) == 0).sum()}', 
              end = '', flush = True)
    print(', done!')
    return data4D_noisy

class segmented_to_4D:
    def __init__(self, channel_based_data, detector_response):
        self.channel_based_data = channel_based_data
        self.detector_response = detector_response
        self.n_x, self.n_y, self.n_ch = channel_based_data.shape
        self.n_ch_det, self.n_r, self.n_c = detector_response.shape
        self.shape = (self.n_x, self.n_y, self.n_r, self.n_c)
        self.dtype = self.channel_based_data.dtype
        
        assert self.n_ch ==  self.n_ch_det, \
            'your detector response number of channels is different from data'

    def __getitem__(self, index):
        # Handle the case where index is a tuple of slices or integers
        if isinstance(index, tuple):
            row_index, col_index = index
            
            if isinstance(row_index, slice) or isinstance(col_index, slice):
                # Compute the actual slice ranges
                row_range = range(*row_index.indices(self.n_x)) \
                    if isinstance(row_index, slice) else range(self.n_x)
                col_range = range(*col_index.indices(self.n_y)) \
                    if isinstance(col_index, slice) else range(self.n_y)
                
                # Initialize the output array
                cbed_slices = np.zeros((len(row_range), len(col_range), self.n_r, self.n_c))
                
                force_print = False

                pbar = printprogress(self.n_ch, print_function=None)
                for segcnt in range(self.n_ch):
                    mask = self.detector_response[segcnt]
                    
                    # Apply mask and slice
                    data_slice = self.channel_based_data[row_index, col_index, segcnt]
                    cbed_slices += data_slice * mask
                    # np.tile(np.expand_dims(data_slice, -1), (1, 1, mask.sum()))
                    
                    ETA = pbar()
                    if (ETA > 120) & (pbar.in_print_function is None):
                        pbar = printprogress(self.n_ch - 1)
                
                return cbed_slices
            
            elif isinstance(row_index, int) and isinstance(col_index, int):
                # Handle single integer index
                row, col = row_index, col_index
                cbed = np.zeros((self.n_r, self.n_c))
                
                for segcnt in range(self.n_ch):
                    mask = self.detector_response[segcnt].copy()
                    ch_cbed = self.channel_based_data[row, col, segcnt].copy()
                    ch_cbed *= mask
                    cbed += ch_cbed.copy()
                
                return cbed
            
            else:
                raise IndexError("Index must be a tuple of slices or integers")
        
        else:
            raise IndexError("Index must be a tuple")

    def __len__(self):
        return self.n_x
    
    def __repr__(self):
        return (f"<ChannelTo4D: n_ch={self.n_ch}, n_x={self.n_x}," +
                f" n_y={self.n_y}, n_r={self.n_r}, n_c={self.n_c}>")
    
    def get_BF_weight_per_channel(self, BF_rad, max_rad):
        radius = BF_rad / max_rad * self.n_r / 2.0
        mask2d = mcemtools.annular_mask((self.n_r, self.n_c), radius = radius)
        
        w_BF = np.zeros(self.n_ch)
        w_DF = np.zeros(self.n_ch)
        for lblcnt in range(self.n_ch):
            w_BF[lblcnt] = ((self.detector_response[lblcnt]) * (mask2d == 1)).sum()\
                                               / (mask2d == 1).sum()
            w_DF[lblcnt] = ((self.detector_response[lblcnt]) * (mask2d == 0)).sum()\
                                               / (mask2d == 0).sum()
    
        return w_BF, w_DF, mask2d
    
    def get_stat_old(self, weights = None, normalize_for_com = True):
        data_by_ch, detector_response = self.channel_based_data , self.detector_response
        if weights is None:
            weights = np.ones(self.n_ch)
        weights_sum = weights.sum()

        stem = (data_by_ch * weights[None, None]).sum(-1)

        pacbed = np.zeros((self.n_r, self.n_c))
        for cnt in range(self.n_ch):
            pacbed += data_by_ch[..., cnt].mean() * weights[cnt] * detector_response[cnt]
        pacbed_com_x, pacbed_com_y = scipy.ndimage.center_of_mass(pacbed)

        if 0:
            data_by_ch = data_by_ch.copy()
            if normalize_for_com:
                data_by_ch_sum = np.expand_dims(data_by_ch.sum(-1), -1)
                data_by_ch_sum = np.tile(data_by_ch_sum, (1, 1, data_by_ch.shape[-1]))
                data_by_ch[data_by_ch_sum != 0] /= data_by_ch_sum[data_by_ch_sum != 0]
                data_by_ch[data_by_ch_sum == 0] = 0

            cent_x, cent_y = self.n_r//2, self.n_c//2
            com_x_ch = np.zeros(data_by_ch.shape)
            com_y_ch = np.zeros(data_by_ch.shape)
            for cnt in range(self.n_ch):
                mask_com_x, mask_com_y = scipy.ndimage.center_of_mass(detector_response[cnt])
                com_x_ch[..., cnt] = data_by_ch[..., cnt]*(mask_com_x - cent_x)
                com_y_ch[..., cnt] = data_by_ch[..., cnt]*(mask_com_y - cent_y)
            com_x = (com_x_ch * weights[None, None]).sum(-1)
            com_y = (com_y_ch * weights[None, None]).sum(-1)
        else:
            import torch
            n_x, n_y, n_ch = data_by_ch.shape
            label_CoM_data = torch.from_numpy(data_by_ch.copy())
            label_CoM_data /= label_CoM_data.sum(-1)[:, :, None]
            label_CoM_data = label_CoM_data.view(-1, n_ch)
            det_CoMs = mcemtools.analysis.CoM_detector(detector_response)
            com_x, com_y = mcemtools.analysis.CoM_channel_torch(label_CoM_data, det_CoMs)
            com_x = com_x.numpy().reshape(n_x, n_y)
            com_y = com_y.numpy().reshape(n_x, n_y)
            
        # if weights_sum:
        #     com_x = com_x / weights_sum
        #     com_y = com_y / weights_sum
        #     stem = stem / weights_sum

        return stem, pacbed, com_x, com_y, pacbed_com_x, pacbed_com_y
    
    def get_stat(self, normalize_for_com = True):
        data_by_ch, detector_response = self.channel_based_data , self.detector_response
        n_x, n_y, n_ch = data_by_ch.shape
        det_CoMs = mcemtools.analysis.CoM_detector(detector_response)

        stem = data_by_ch.sum(-1)

        pacbed = np.zeros((self.n_r, self.n_c))
        for cnt in range(self.n_ch):
            pacbed += data_by_ch[..., cnt].mean() * detector_response[cnt]
        pacbed_com_x, pacbed_com_y = scipy.ndimage.center_of_mass(pacbed)

        import torch
        label_CoM_data = torch.from_numpy(data_by_ch.copy())
        if normalize_for_com:
            label_CoM_data /= label_CoM_data.sum(-1)[:, :, None]
        label_CoM_data = label_CoM_data.reshape(-1, n_ch)
        com_x, com_y = mcemtools.analysis.CoM_channel_torch(label_CoM_data, det_CoMs)
        com_x = com_x.reshape(n_x, n_y).numpy()
        com_y = com_y.reshape(n_x, n_y).numpy()
            
        return stem, pacbed, com_x, com_y, pacbed_com_x, pacbed_com_y
    
    def filtered_by_kernel(self, coords, win_side, weights):
    
        coords += win_side
        coords_max = int(coords.max() + 1)
        kernel = np.zeros((coords_max, coords_max))
        for win_cnt_i, win_cnt_j in product(range(win_side), range(win_side)):
            kernel[coords[:, 0] - win_cnt_i, coords[:, 1] - win_cnt_j] = weights

        _, _, com_x, com_y, _, _ = self.get_stat()

        # com_x = -scipy.ndimage.rotate(com_x, -90)
        # com_y = -scipy.ndimage.rotate(com_y, -90)

        filtered_com_x = scipy.signal.convolve2d(com_x, kernel)
        filtered_com_y = scipy.signal.convolve2d(com_y, kernel)

        filtered_com_x = filtered_com_x[coords_max:-coords_max, coords_max:-coords_max]
        filtered_com_y = filtered_com_y[coords_max:-coords_max, coords_max:-coords_max]

        return filtered_com_x, filtered_com_y, kernel
    
def apply_detector_response(d4d, detector_response, verbose = False,
                            return_by_channle = True, segment_is_one_pixels = True):
    """
    Replace values in a multi-dimensional image based on a segmented labeled image.
    
    Parameters:
    ----------
    d4d : np.ndarray
        The multi-dimensional image array with shape (n_x, n_y, n_r, n_c),
        where each (n_r, n_c) slice is a single image.
    detector_response : np.ndarray of shape n_ch x n_r x n_c
        The area around the detector should be set to 0, and each segment
        should appear in a single channle with its artifacts.

    Returns:
    -------
    np.ndarray
        The modified image with each segment's values replaced by their sums.

    Raises:
    ------
    ValueError
        If detector_response does not match the last two dimensions of d4d.
    
    Notes:
    ------
    This function sums the values in each segment of d4d, defined by detector_response.
    Each segment (where detector_response == i) is replaced by the segment's sum in the
    modified d4d.
    """
    if detector_response.shape[1:] != d4d.shape[-2:]:
        raise ValueError("The shape of detector_response must match the last two dimensions of d4d.")

    
    if return_by_channle:
        data_by_ch = np.zeros(
            (d4d.shape[0], d4d.shape[1], len(detector_response)), dtype = d4d.dtype)
    else:
        modified_d4d = d4d.copy()

    if verbose: pbar = printprogress(d4d.shape[0] * d4d.shape[1])
    for i, j in np.ndindex(d4d.shape[:2]):
        segments_sum = d4d[None, i, j] * detector_response
        if return_by_channle:
            data_by_ch[i, j] = segments_sum.sum((1, 2))
        else:
            if segment_is_one_pixels:
                img_by_ch = segments_sum.sum((1, 2))
                modified_d4d[i, j] = (img_by_ch[:, None, None] * detector_response).sum(0)
            else:
                modified_d4d[i, j] = segments_sum.sum(0)
        if verbose: pbar()
                

    if return_by_channle:
        return data_by_ch
    else:
        return modified_d4d

def generate_indices(labels_shape, batch_size, method = 'class_based'):
    """
    Generate indices for sampling data while ensuring specific class coverage requirements.

    Parameters
    ----------
    labels_shape : tuple
        A tuple `(n_classes, n_sample_per_class)` where:
        - `n_classes` is the number of classes.
        - `n_sample_per_class` is the number of samples available for each class.

    batch_size : int
        The number of samples per batch. Must evenly divide `n_classes`.

    method : str, optional
        The method to generate indices. Options are:
        - `'random'`: Randomly shuffle all indices and group them into batches.
        - `'class_based'`: Ensures each batch contains a balanced distribution of class indices,
          and consecutive samples attempt to provide broad class coverage.
        Default is `'class_based'`.

    Returns
    -------
    samples : ndarray
        A 2D NumPy array of shape `(n_batches, batch_size)`, where `n_batches` is the total
        number of batches. Each row contains indices representing a batch of samples.

    Raises
    ------
    AssertionError
        If `n_classes` is not a multiple of `batch_size`.

    Notes
    -----
    - For the `'random'` method, indices are shuffled globally before grouping into batches.
    - For the `'class_based'` method, samples are shuffled within each class, and batches
      are generated such that each group of `batch_size` indices maintains balance across classes.

    Examples
    --------
    Generate indices with class-based sampling:
    >>> labels_shape = (52, 100)  # 52 classes, 100 samples per class
    >>> batch_size = 4
    >>> samples = generate_indices(labels_shape, batch_size, method='class_based')
    >>> samples.shape
    (1300, 4)  # Total batches: (52*100) / 4 = 1300

    Generate indices with random sampling:
    >>> samples = generate_indices(labels_shape, batch_size, method='random')
    >>> samples.shape
    (1300, 4)
    """
    n_classes, n_sample_per_class = labels_shape
    n_groups_of_classes = n_classes // batch_size
    assert n_classes // batch_size == n_classes / batch_size, \
        'n_classes must be a product of batch_size'
    total_points = n_classes * n_sample_per_class
    n_samples = total_points // batch_size
    indices = np.arange(total_points)
    
    if method == 'random':
        np.random.shuffle(indices)
        samples = indices.reshape((n_samples // batch_size, batch_size))
    elif method == 'class_based':
        print('class based shuffling of data')
        indices = indices.reshape(labels_shape)
        for inds_cnt , inds in enumerate(indices):
            np.random.shuffle(inds)
            indices[inds_cnt] = inds.copy()
        indices = indices.swapaxes(0, 1)
        samples = np.zeros((n_samples, batch_size), dtype=int)
        
        for sample_cnt in range(len(indices)):
            bunch_of_samples = indices[sample_cnt]
            np.random.shuffle(bunch_of_samples)
            for gcnt in range(n_groups_of_classes):
                if gcnt == 0:
                    samples[sample_cnt*n_groups_of_classes] = \
                        bunch_of_samples[:batch_size]
                elif gcnt == n_groups_of_classes - 1:
                    samples[sample_cnt*n_groups_of_classes + gcnt] = \
                        bunch_of_samples[-batch_size:]
                else:
                    samples[sample_cnt*n_groups_of_classes + gcnt] = \
                        bunch_of_samples[gcnt * batch_size: (gcnt + 1) * batch_size]
        
    return samples