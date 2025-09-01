import torch
import torch.nn as nn


class LatentCovLoss(nn.Module):
    """
    Latent covariance loss class
    """
    # TODO: Simmulated Annealing. Not present by default in pytorch. Needs custom optimizer

    def __init__(self):
        super().__init__()

    def forward(self, input, _):
        """
        :param  input: is the latent space representation of the current batch
        """
        cov = torch.cov(torch.transpose(input, 0, 1), correction=1)
        cov_square = cov * cov  # elem wise mult
        # number of covariance entries (need to subract 1 to not take into account diagonal variance metrics)
        nbr_of_cov = input.shape[-1] * (input.shape[-1] - 1)
        cov_loss = (torch.sum(cov_square) -
                    torch.trace(cov_square)) / float(nbr_of_cov)
        return cov_loss


class MAEDistLoss(nn.Module):
    """
    Absolute Error between original and latent distances

    :param distances: batch of original and latent distances between twins
    :return: batch of absolute errors
    """

    def __init__(self):
        super().__init__()

    def forward(self, input, _):
        distances = input
        ae = torch.abs(distances[:, 0] - distances[:, 1])
        return torch.mean(ae)


class MALEDistLoss(nn.Module):
    """
    Absolute Error between logarithm of original and latent distances

    :param distances: batch of original and latent distances between twins
    :return: batch of absolute logarithmic errors
    """

    def __init__(self):
        super().__init__()

    def forward(self, input, _):
        distances = input
        ale = torch.abs(torch.log1p(
            distances[:, 0]) - torch.log1p(distances[:, 1]))
        return torch.mean(ale)


class MAPEDistLoss(nn.Module):
    """
    Absolute Percentage Error between original and latent distances

    :param distances: batch of original and latent distances between twins
    :return: batch of absolute percentage errors
    """

    def __init__(self):
        super().__init__()

    def forward(self, input, _):
        distances = input
        epsilon = 1e-8
        ape = torch.abs(
            (distances[:, 0] - distances[:, 1]) / (distances[:, 0] + epsilon))
        return torch.mean(ape)


class MSEDistLoss(nn.Module):
    """
    Squared Error between original and latent distances

    :param distances: batch of original and latent distances between twins
    :return: batch of squared errors
    """

    def __init__(self):
        super().__init__()

    def forward(self, input, _):
        distances = input
        se = torch.square(distances[:, 0] - distances[:, 1])
        return torch.mean(se)


class MSLEDistLoss(nn.Module):
    """
    Squared Error between logarithm of original and latent distances

    :param distances: batch of original and latent distances between twins
    :return: batch of squared logarithmic errors
    """

    def __init__(self):
        super().__init__()

    def forward(self, input, _):
        distances = input
        sle = torch.square(torch.log1p(
            distances[:, 0]) - torch.log1p(distances[:, 1]))
        return torch.mean(sle)


class CorrDistLoss(nn.Module):
    """
    Correlation loss between original and latent distances

    :param distances: batch of original and latent distances between twins
    :return: 1 - correlation coefficient
    """

    def __init__(self):
        super().__init__()

    def forward(self, input, _):
        distances = input

        # Calculate covariance matrix
        x = distances[:, 0]
        y = distances[:, 1]

        # Center the data
        x_centered = x - torch.mean(x)
        y_centered = y - torch.mean(y)

        # Calculate covariance and variances
        cov_xy = torch.mean(x_centered * y_centered)
        var_x = torch.mean(x_centered * x_centered)
        var_y = torch.mean(y_centered * y_centered)

        # Calculate correlation coefficient
        std_x = torch.sqrt(torch.abs(var_x))
        std_y = torch.sqrt(torch.abs(var_y))

        # Avoid division by zero
        epsilon = 1e-8
        corr = cov_xy / (std_x * std_y + epsilon)

        return 1 - corr
