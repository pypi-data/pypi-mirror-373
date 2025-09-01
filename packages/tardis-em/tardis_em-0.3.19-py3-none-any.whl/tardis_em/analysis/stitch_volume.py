from scipy import optimize
from scipy.ndimage import rotate, shift, zoom, affine_transform
import numpy as np

from tardis_em.utils.normalization import MeanStdNormalize, RescaleNormalize


class VolumeRidgeRegistration:
    def __init__(self, optimize_fn='mi', crop_volume=True, down_scale=6):
        assert optimize_fn in ['mi', 'mse', 'ncc'], "optimize_fn must be 'mi' or 'mse'"
        self.optimize_fn = optimize_fn
        self.crop_volume = crop_volume
        self.down_scale = down_scale
        self.mean_std = MeanStdNormalize()
        self.normalize = RescaleNormalize(clip_range=(1, 99))

    def volume_to_projection(self, img1, img2, method='sum'):
        assert method in ['sum', 'fraction_center', 'fraction_edge']

        if method == 'sum':
            img1 = np.sum(img1, axis=0)
            img2 = np.sum(img2, axis=0)
        elif method == 'fraction_center':
            bottom = int(img1.shape[0] * 0.05)
            top = int(img2.shape[0] * 0.05)

            img1 = np.sum(img1[:-bottom, ...], axis=0)
            img2 = np.sum(img2[top:, ...], axis=0)
        elif method == 'fraction_edge':
            bottom = int(img1.shape[0] * 0.05)
            top = int(img2.shape[0] * 0.05)

            img1 = np.sum(img1[bottom:, ...], axis=0)
            img2 = np.sum(img2[:-top, ...], axis=0)

        img1 = self.normalize(self.mean_std(img1)).astype(np.float32)
        img2 = self.normalize(self.mean_std(img2)).astype(np.float32)

        return img1, img2

    def stitch_volume(self, vol1, vol2, ang, ty, tx):
        # Convert angle to radians
        theta = np.deg2rad(ang)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        matrix = np.array([
            [1, 0, 0, 0],  # z unchanged
            [0, cos_theta, -sin_theta, ty],  # y' = cos θ y - sin θ x + shift_y
            [0, sin_theta, cos_theta, tx],  # x' = sin θ y + cos θ x + shift_x
            [0, 0, 0, 1]  # Homogeneous coordinate
        ])

        # Compute output shape to encompass rotated volume
        y, x = vol2.shape[1], vol2.shape[2]
        # Corners of the y-x plane after rotation
        corners = np.array([
            [0, 0], [0, y - 1], [x - 1, 0], [x - 1, y - 1]
        ])
        rot_corners = corners @ np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
        rot_corners += [tx, ty]
        min_xy = rot_corners.min(axis=0)
        max_xy = rot_corners.max(axis=0)
        if not self.crop_volume:
            out_shape = [vol2.shape[0],
                         int(np.ceil(max_xy[1] - min_xy[1] + 1)),
                         int(np.ceil(max_xy[0] - min_xy[0] + 1))]

            # Compute padding widths and update out_shape
            pad_widths = []
            for i, (dim1, dim_out) in enumerate(zip(vol1.shape, out_shape)):
                if dim1 < dim_out:
                    # Pad vol1 to match out_shape
                    before = (dim_out - dim1) // 2
                    after = dim_out - dim1 - before
                    pad_widths.append((before, after))
                else:
                    # Update out_shape to vol1's dimension
                    out_shape[i] = dim1
                    pad_widths.append((0, 0))

            # Apply padding in one step
            vol1 = np.pad(
                vol1,
                pad_width=pad_widths,
                mode='constant',
                constant_values=0
            )

        else:
            out_shape = vol1.shape

        # Adjust offset to keep content in positive coordinates
        offset = [0, -min_xy[1], -min_xy[0]]

        # Apply affine transform
        vol2 = affine_transform(
            vol2,
            matrix[:3, :3],  # 3x3 transformation matrix
            offset=offset,  # Translation to align output
            output_shape=out_shape,
            order=1,  # Linear interpolation (faster than cubic)
            mode='constant',
            cval=0
        )

        return np.concatenate((vol1, vol2), axis=0)

    @staticmethod
    def mean_squared_error(img1, img2):
        """Compute Mean Squared Error between two images."""
        if img1.shape != img2.shape:
            raise ValueError("Images must have the same dimensions for MSE")
        valid_mask = np.where(img2 != 0)
        img1 = img1.astype(float)[valid_mask]
        img2 = img2.astype(float)[valid_mask]

        return np.mean((img1 - img2) ** 2)

    @staticmethod
    def mutual_information(img1, img2, bins=64):
        """Compute Mutual Information between two images."""
        if img1.shape != img2.shape:
            raise ValueError("Images must have the same dimensions for MI")

        # Normalize images to [0, 1] for histogram
        img1 = img1.astype(float)
        img2 = img2.astype(float)
        valid_mask = np.where(img2 != 0)

        img1 = (img1 - np.min(img1)) / (np.max(img1) - np.min(img1) + 1e-10)
        img2 = (img2 - np.min(img2)) / (np.max(img2) - np.min(img2) + 1e-10)

        # Compute joint histogram
        hist_2d, x_edges, y_edges = np.histogram2d(
            img1[valid_mask].ravel(), img2[valid_mask].ravel(),
            bins=bins, range=[[0, 1], [0, 1]]
        )
        hist_2d = hist_2d / (np.sum(hist_2d) + 1e-10)  # Normalize to probability

        # Marginal histograms
        hist_1 = np.sum(hist_2d, axis=1)
        hist_2 = np.sum(hist_2d, axis=0)

        # Entropies
        H1 = -np.sum(hist_1 * np.log2(hist_1 + 1e-10))
        H2 = -np.sum(hist_2 * np.log2(hist_2 + 1e-10))
        H12 = -np.sum(hist_2d * np.log2(hist_2d + 1e-10))

        # Mutual Information
        return -(H1 + H2 - H12)

    @staticmethod
    def normalized_cross_correlation(img1, img2):
        """Compute Normalized Cross-Correlation between two images."""
        # Ensure images are same size
        if img1.shape != img2.shape:
            raise ValueError("Images must have the same dimensions for NCC")

        # Flatten images and normalize
        img1 = img1.astype(float)
        img2 = img2.astype(float)

        valid_mask = np.where(img2 != 0)

        # Subtract mean and compute standard deviation
        img1 = img1 - np.mean(img1)
        img2 = img2 - np.mean(img2)
        std1 = np.std(img1)
        std2 = np.std(img2)

        # Avoid division by zero
        if std1 == 0 or std2 == 0:
            return 0.0

        # Compute NCC
        return -(np.sum(img1[valid_mask] * img2[valid_mask]) / (std1 * std2 * img1[valid_mask].size))

    @staticmethod
    def apply_transform(img, angle, tx, ty, reshape=False):
        """Apply rotation and translation to an image without cropping."""
        # Rotate with reshape=True to accommodate full rotated image
        if not reshape:
            # Convert angle to radians
            theta = np.deg2rad(angle)
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)

            # Affine matrix for rotation + translation
            cy, cx = img.shape
            cy, cx = cx / 2, cy / 2

            T1 = np.array([[1, 0, -cx],
                           [0, 1, -cy],
                           [0, 0, 1]])
            R = np.array([[cos_theta, -sin_theta, 0],
                          [sin_theta, cos_theta, 0],
                          [0, 0, 1]])
            T2 = np.array([[1, 0, cx + tx],
                           [0, 1, cy + ty],
                           [0, 0, 1]])
            matrix = T2 @ R @ T1

            transformed = affine_transform(
                img,
                matrix[:2, :2],  # 2x2 rotation matrix
                offset=matrix[:2, 2],  # Combine offset and translation
                output_shape=img.shape,
                order=1,
                mode='constant',
                cval=0
            )
        else:
            transformed = rotate(img, angle, reshape=reshape, mode='constant', cval=0)
            # Calculate new canvas size to accommodate translation
            max_trans = (abs(ty), abs(tx))
            new_shape = (int(transformed.shape[0] + max_trans[0]), int(transformed.shape[1] + max_trans[1]))

            # Create a new canvas with sufficient size
            transformed = np.zeros(new_shape, dtype=img.dtype)

            # Place rotated image in the center of the canvas
            offset_y = (new_shape[0] - transformed.shape[0]) // 2
            offset_x = (new_shape[1] - transformed.shape[1]) // 2
            transformed[offset_y:offset_y + transformed.shape[0], offset_x:offset_x + transformed.shape[1]] = transformed

            # Apply translation
            transformed = shift(transformed, [ty, tx], mode='constant', cval=0)

            x_start = -int(tx) if tx < 0 else 0
            x_end = int(tx) if tx > 0 else transformed.shape[1]
            y_start = -int(ty) if ty < 0 else 0
            y_end = int(ty) if ty > 0 else transformed.shape[0]
            transformed = transformed[y_start:y_end, x_start:x_end]

        return transformed

    def objective_function(self, params, fixed_img, moving_img):
        """Objective function to minimize (negative NCC)."""
        angle, tx, ty = params
        transformed_img = self.apply_transform(moving_img, angle, tx, ty, reshape=False)

        if self.optimize_fn == 'mi':
            return self.mutual_information(fixed_img, transformed_img, 64)
        elif self.optimize_fn == 'mse':
            return self.mean_squared_error(fixed_img, transformed_img)
        else:
            return self.normalized_cross_correlation(fixed_img, transformed_img)

    def align_images(self, fixed_img, moving_img):
        fixed_small = zoom(fixed_img, 1/self.down_scale, order=1)
        moving_small = zoom(moving_img, 1/self.down_scale, order=1)

        """Align moving_img to fixed_img using intensity-based registration."""
        # Initial guess: no rotation, no translation
        initial_params = [0.0, 0.0, 0.0]  # [angle, tx, ty]

        # Define bounds for optimization
        bounds = [(-180, 180),
                  (-fixed_small.shape[1]//2, fixed_small.shape[1]//2),
                  (-fixed_small.shape[0]//2, fixed_small.shape[0]//2)]

        # Optimize transformation parameters
        result = optimize.minimize(
            self.objective_function,
            initial_params,
            args=(fixed_small, moving_small),
            method='Powell',
            bounds=bounds
        )

        # Extract optimal parameters
        opti_angle, opti_tx, opti_ty = result.x
        score = result.fun

        opti_tx /= 1/self.down_scale
        opti_ty /= 1/self.down_scale

        return opti_angle, opti_tx, opti_ty, score

    def __call__(self, fixed_vol, moving_vol, return_volume=False, proj_method='sum'):
        assert proj_method in ['sum', 'fraction_center', 'fraction_edge']
        fixed_proj, moving_proj = self.volume_to_projection(fixed_vol, moving_vol, 'fraction_center')
        opti_angle, opti_tx, opti_ty, score = self.align_images(fixed_proj, moving_proj)

        if return_volume:
            stitched_vol = self.stitch_volume(fixed_vol, moving_vol, opti_angle, opti_tx, opti_ty)

            return stitched_vol, opti_angle, opti_tx, opti_ty, score
        else:
            align_img = self.apply_transform(moving_proj, opti_angle, opti_tx, opti_ty, reshape=not self.crop_volume)

            return align_img, opti_angle, opti_tx, opti_ty, score
