import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

import torch
import torch.nn.init as init

import gpytorch
from gpytorch.means import ConstantMean
from gpytorch.distributions import MultivariateNormal
from gpytorch.mlls import ExactMarginalLogLikelihood
from gpytorch.models import ApproximateGP
from gpytorch.variational import VariationalStrategy, CholeskyVariationalDistribution
from gpytorch.kernels import ScaleKernel, RBFKernel

from sklearn.cluster import KMeans


class SVGPRegressionModel(ApproximateGP):
    def __init__(self, train_x, train_y, likelihood, inducing_points):
        num_inducing = inducing_points.size(0)
        variational_distribution = CholeskyVariationalDistribution(num_inducing)
        variational_strategy = VariationalStrategy(
            self,
            inducing_points,
            variational_distribution,
            learn_inducing_locations=True
        )
        ApproximateGP.__init__(self, variational_strategy)
        
        self.mean_module = ConstantMean()
        self.covar_module = ScaleKernel(RBFKernel())
        self.inducing_points = inducing_points
        
        if likelihood is None:
            likelihood = gpytorch.likelihoods.GaussianLikelihood()

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        latent_pred = MultivariateNormal(mean_x, covar_x)
        return latent_pred

def Appro_GP(x1, x2, y2, n_intro = 500, num_epochs = 1000, lr = 0.01):
    kmeans = KMeans(n_clusters=n_intro, random_state=42)
    kmeans.fit(x2)
    inducing_points = torch.tensor(kmeans.cluster_centers_).float()

    likelihoods2 = []
    models2 = []
    for i in range(y2.size(1)):
        likelihood = gpytorch.likelihoods.GaussianLikelihood()
        model = SVGPRegressionModel(x2, y2[:, i], likelihood, inducing_points)
        likelihoods2.append(likelihood)
        models2.append(model)
    
    for model, likelihood, y in zip(models2, likelihoods2, y2.transpose(0,1)):
        model.train()
        likelihood.train()
        optimizer = torch.optim.Adam(model.parameters(), lr = lr)
        mll = gpytorch.mlls.VariationalELBO(likelihood,model,len(y))
        
        for epoch in range(num_epochs):
            optimizer.zero_grad()
            output = model(x2)
            loss = -mll(output, y)
            loss.backward()
            optimizer.step()
            
    for model, likelihood in zip(models2, likelihoods2):
        model.eval()
        likelihood.eval()

    with torch.no_grad():
        predictions = torch.cat([model(x1).mean.unsqueeze(1) for model in models2], dim=1)
    
    return(predictions)


class MultiOutputGaussianProcessRegressor(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood):
        super(MultiOutputGaussianProcessRegressor, self).__init__(train_x, train_y, likelihood)
        self.mean_module = ConstantMean()
        self.covar_module = RBFKernel()

    def forward(self, x):
        mean = self.mean_module(x)
        covar = self.covar_module(x)
        return MultivariateNormal(mean, covar)


def Exact_GP(x1, x2, y2, num_epochs = 1000, lr = 0.01):
    likelihoods2 = []
    models2 = []
    
    for i in range(y2.size(1)):
        likelihood = gpytorch.likelihoods.GaussianLikelihood()
        model = MultiOutputGaussianProcessRegressor(x2, y2[:, i], likelihood)
        likelihoods2.append(likelihood)
        models2.append(model) 
        
    for model, likelihood, y in zip(models2, likelihoods2, y2.transpose(0,1)):
        model.train()
        likelihood.train()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        mll = ExactMarginalLogLikelihood(likelihood, model)
        
        for epoch in range(num_epochs):
            optimizer.zero_grad()
            output = model(x2)
            loss = -mll(output, y)
            loss.backward()
            optimizer.step()
            
    for model, likelihood in zip(models2, likelihoods2):
        model.eval()
        likelihood.eval()

    with torch.no_grad():
        predictions = torch.cat([model(x1).mean.unsqueeze(1) for model in models2], dim=1)
    return(predictions)