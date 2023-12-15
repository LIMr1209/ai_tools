# cython: language_level=3
import torch as t
from torchvision.models import AlexNet, DenseNet, ResNet, Inception3, SqueezeNet
from efficientnet_pytorch import EfficientNet as ef
from flask import current_app
import torch.nn as nn


class BasicModule(nn.Module):
    def __init__(self):
        super(BasicModule, self).__init__()
        self.model_name = str(type(self))  # 默认名字


class AlexNet1(BasicModule):
    def __init__(self, NUM_CLASSES):
        super(AlexNet1, self).__init__()
        self.model_name = "AlexNet1"
        self.model = AlexNet(num_classes=NUM_CLASSES)

    def forward(self, x):
        return self.model(x)


class DenseNet161(BasicModule):
    def __init__(self, NUM_CLASSES):
        super(DenseNet161, self).__init__()
        self.model_name = "DenseNet161"
        self.model = DenseNet(
            num_init_features=96,
            growth_rate=48,
            block_config=(6, 12, 36, 24),
            num_classes=NUM_CLASSES,
        )

    def forward(self, x):
        return self.model(x)


class DenseNet201(BasicModule):
    def __init__(self, NUM_CLASSES):
        super(DenseNet201, self).__init__()
        self.model_name = "DenseNet201"
        self.model = DenseNet(
            num_init_features=64,
            growth_rate=32,
            block_config=(6, 12, 48, 32),
            num_classes=NUM_CLASSES,
        )

    def forward(self, x):
        return self.model(x)


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(
            planes, planes, kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class ResNet152(BasicModule):
    def __init__(self, NUM_CLASSES):
        super(ResNet152, self).__init__()
        self.model_name = "ResNet152"
        self.model = ResNet(Bottleneck, [3, 8, 36, 3], num_classes=NUM_CLASSES)

    def forward(self, x):
        return self.model(x)


class EfficientNet(BasicModule):
    def __init__(self, num_classes):
        super(EfficientNet, self).__init__()
        self.model_name = "EfficientNet"
        self.model = ef.from_name(
            "efficientnet-b7", override_params={"num_classes": num_classes}
        )

    def forward(self, x):
        return self.model(x)


class InceptionV3(BasicModule):
    def __init__(self, num_classes):
        super(InceptionV3, self).__init__()
        self.model_name = "InceptionV3"
        self.model = Inception3(num_classes=num_classes)

    def forward(self, x):
        return self.model(x)


class SqueezeNet1_1(BasicModule):
    def __init__(self, NUM_CLASSES):
        super(SqueezeNet1_1, self).__init__()
        self.model_name = "SqueezeNet1_1"
        self.model = SqueezeNet(version=1.1, num_classes=NUM_CLASSES)

    def forward(self, x):
        return self.model(x)
