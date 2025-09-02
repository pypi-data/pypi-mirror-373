import torch
import visdom
from tqdm import tqdm

from . import Model


class RandomLatent(Model):
    def __init__(self, latent_dim=100):
        super().__init__()
        self.latent_dim = latent_dim
        self.d_p = torch.nn.Parameter(torch.randn(latent_dim))

    def forward(self, batch_size=4):
        return torch.randn(batch_size, self.latent_dim).to(self.device)


class Generator(Model):
    def __init__(self, latent_dim=100, *layers):
        rand_layer = RandomLatent(latent_dim)
        super().__init__(*[rand_layer, *layers])
        self.latent_dim = rand_layer.latent_dim


def get_din(batch):
    return batch[-1]


class GAN(Model):
    def __init__(self, generator, discriminator):
        super().__init__()
        self.generator = generator
        self.discriminator = discriminator
        self.generator_optimizer = None
        self.discriminator_optimizer = None
        self.loss_function = torch.nn.BCELoss()

    def fit(
            self, data_loader, n_cretic=1, messages=None, get_din=get_din, bar=None,
            sample_internal=0, viz: visdom.Visdom = None
    ):
        if messages is None:
            messages = {}
            for loss_name in 'train_batch_losses_g, train_batch_losses_d, test_batch_losses_g, test_batch_losses_d'.replace(
                    ' ', '').split(','):
                messages[loss_name] = []
                if viz is not None:
                    viz.line([0], [0], win=loss_name, opts=dict(title=loss_name))

        if sample_internal > 0 and not ('example_sample' in messages.keys()):
            messages['example_sample'] = []

        #region training prepare
        if self.generator_optimizer is None:
            self.generator_optimizer = torch.optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        if self.discriminator_optimizer is None:
            self.discriminator_optimizer = torch.optim.Adam(self.discriminator.parameters(), lr=0.0002,
                                                            betas=(0.5, 0.999))
        self.loss_function = self.loss_function.to(self.device)
        #endregion

        for batch in data_loader:
            step = bar.n
            bar.update(1)

            #region din
            din = get_din(batch).to(self.device)
            batch_size = din.size(0)
            #endregion

            #region labels
            real_label = torch.zeros(batch_size, 1).to(self.device)
            fake_label = torch.ones(batch_size, 1).to(self.device)
            #endregion

            #region train discriminator
            real_judge = self.discriminator(din)
            real_loss = self.loss_function(real_judge, real_label)

            fake = self.generator(batch_size)
            fake_judge = self.discriminator(fake)
            fake_loss = self.loss_function(fake_judge, fake_label)

            train_batch_loss_d = real_loss + fake_loss

            self.discriminator_optimizer.zero_grad()
            train_batch_loss_d.backward()
            self.discriminator_optimizer.step()

            messages['train_batch_losses_d'].append(train_batch_loss_d.item())
            try:
                if viz is not None:
                    viz.line([train_batch_loss_d.item()], [step], win='train_batch_losses_d', update='append')
            except:
                pass
            #endregion

            #region train generator
            if step % n_cretic == 0:
                generate_result = self.generator(batch_size)
                generate_judge = self.discriminator(generate_result)
                generate_loss = self.loss_function(generate_judge, real_label)

                self.generator_optimizer.zero_grad()
                generate_loss.backward()
                self.generator_optimizer.step()

                messages['train_batch_losses_g'].append(generate_loss.item())
                try:
                    if viz is not None:
                        viz.line([generate_loss.item()], [step], win='train_batch_losses_g', update='append')
                except:
                    pass
                if step % sample_internal == 0:
                    messages['example_sample'].append(generate_result[0].detach().cpu())
                    try:
                        if viz is not None:
                            viz.image(messages['example_sample'][-1], win=f'example_sample{step}')
                    except:
                        pass
            #endregion

        return messages


class PGGLoss(torch.nn.Module):
    def forward(self, p1, p2):
        samples, fake, D_net, lambd = p2
        eps = torch.rand(samples.size(0), 1, 1, 1)
        eps = eps.expand_as(samples)
        x_hat = eps * samples + (1 - eps) * fake.detach()
        x_hat.requires_grad = True
        px_hat = D_net(x_hat)
        grad = torch.autograd.grad(
            outputs=px_hat.sum(),
            inputs=x_hat,
            create_graph=True
        )[0]
        grad_norm = grad.view(samples.size(0), -1).norm(2, dim=1)
        gradient_penalty = lambd * ((grad_norm - 1) ** 2).mean()

        return gradient_penalty

class ProgressiveGAN(GAN):
    """
    need generator and discriminator with depth differed output
    """
    depth_iter_num = 0

    def __init__(self, generator, discriminator):
        super().__init__(generator, discriminator)

        self.loss_function = torch.nn.L1Loss()

    def fit(
            self, data_loader, n_cretic=1, messages=None, get_din=get_din, bar=None,
            sample_internal=0, viz: visdom.Visdom = None, grow=False
    ):
        def resize(img):
            img = get_din(img)
            assert len(img.size()) == 4
            return torch.nn.functional.interpolate(img, size=2 ** (self.discriminator.depth + 1))

        if grow:
            self.grow()
        r = super().fit(data_loader, n_cretic, messages, resize, bar, sample_internal, viz)

        self.depth_iter_num += len(data_loader.dataset)

        return r

    def grow(self):
        self.generator.layer2.growing_net(self.depth_iter_num)
        self.discriminator.growing_net(self.depth_iter_num)
