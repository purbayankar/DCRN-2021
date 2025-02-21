import torch
import torch.nn as nn
import torch.nn.functional as F

class SSRN(nn.Module):

    def __init__(self, input_channels, patch_size, n_classes):
        super(SSRN, self).__init__()
        self.inplanes = 24
        self.kernel_dim = 1
        self.feature_dim = input_channels
        self.sz = patch_size
        # Convolution Layer 1 kernel_size = (1, 1, 7), stride = (1, 1, 2), output channels = 24
        self.conv1 = nn.Conv3d(1, 24, kernel_size= (7, 1, 1), stride=(2, 1, 1), bias=True)
        self.bn1 = nn.BatchNorm3d(24)
        self.activation1 = nn.ReLU()

        # Residual block 1
        self.conv2 = nn.Conv3d(24, 24, kernel_size= (7, 1, 1), stride= 1, padding= (3, 0, 0), padding_mode = 'replicate', bias= True)
        self.bn2 = nn.BatchNorm3d(24)
        self.activation2 = nn.ReLU()
        self.conv3 = nn.Conv3d(24, 24, kernel_size= (7, 1, 1), stride= 1, padding= (3, 0, 0), padding_mode = 'replicate', bias= True)
        self.bn3 = nn.BatchNorm3d(24)
        self.activation3 = nn.ReLU()
        # Finish

        # Convolution Layer 2 kernel_size = (1, 1, (self.feature_dim - 6) // 2), output channels = 128
        self.conv4 = nn.Conv3d(24, 128, kernel_size= (((self.feature_dim - 7) // 2 + 1), 1, 1), bias = True)
        self.bn5 = nn.BatchNorm3d(128)
        self.activation5 = nn.ReLU()
        
        # Convolution Layer 3 kernel_size = (3, 3, 128), output channels = 24
        self.conv5 = nn.Conv3d(1, 24, kernel_size= (128, 3, 3), bias = True)
        self.activation6 = nn.ReLU()
        self.bn6 = nn.BatchNorm3d(24)

        # Residual block 2
        self.conv6 = nn.Conv2d(24, 24, kernel_size= 3, stride= 1, padding= 1, padding_mode = 'replicate', bias= True)
        self.bn7 = nn.BatchNorm2d(24)
        self.activation7 = nn.ReLU()
        self.conv7 = nn.Conv2d(24, 24, kernel_size= 3, stride= 1, padding= 1, padding_mode = 'replicate', bias= True)
        self.bn8 = nn.BatchNorm2d(24)
        self.activation8 = nn.ReLU()
        self.conv8 = nn.Conv2d(24, 24, kernel_size= 1)
        # Finish

        # Average pooling kernel_size = (5, 5, 1)
        self.avgpool = nn.AvgPool2d((self.sz - 2, self.sz - 2))

        # Fully connected Layer
        self.fc1 = nn.Linear(in_features= 24, out_features= n_classes)
        self.activation10 = nn.Softmax(dim= 1)

        # parameters initialization
        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                torch.nn.init.kaiming_normal_(m.weight.data)
                m.bias.data.zero_()            
            elif isinstance(m, nn.BatchNorm3d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def forward(self, x, bounds=None):

        # Convolution layer 1
        x = self.conv1(x)
        x = self.activation1(self.bn1(x))

        # Residual layer 1
        residual = x
        x = self.conv2(x)
        x = self.activation2(self.bn2(x))
        x = self.conv3(x)
        x = residual + x
        x = self.activation3(self.bn3(x))

        # Convolution layer 2
        x = self.conv4(x)
        x = self.activation5(self.bn5(x))

        # Reshape from (batch_size, nb_channels, 1, length_x, length_y, 1) to (batch_size, 1, length_x, length_y, nb_channels)
        x = x.view((x.size(0), x.size(2), x.size(1), x.size(3), x.size(4)))

        # Convolution layer 3
        x = self.conv5(x)
        x = self.activation6(self.bn6(x))
        x = x.reshape(x.size(0),x.size(1), x.size(3), x.size(4))

        # Residual layer 2
        residual = x
        residual = self.conv8(residual)
        x = self.conv6(x)
        x = self.activation7(self.bn7(x))
        x = self.conv7(x)
        x = residual + x

        x = self.activation8(self.bn8(x))
        x = self.avgpool(x)
        x = x.reshape((x.size(0), -1))

        # Fully connected layer
        x = self.fc1(x)

        return x

class DCRN(nn.Module):

    def __init__(self, input_channels, patch_size, n_classes):
        super(DCRN, self).__init__()
        self.kernel_dim = 1
        self.feature_dim = input_channels
        self.sz = patch_size
        # Convolution Layer 1 kernel_size = (1, 1, 7), stride = (1, 1, 2), output channels = 24
        self.conv1 = nn.Conv3d(1, 24, kernel_size= (7, 1, 1), stride=(2, 1, 1), bias=True)
        self.bn1 = nn.BatchNorm3d(24)
        self.activation1 = nn.ReLU()

        # Residual block 1
        self.conv2 = nn.Conv3d(24, 24, kernel_size= (7, 1, 1), stride= 1, padding= (3, 0, 0), padding_mode = 'replicate', bias= True)
        self.bn2 = nn.BatchNorm3d(24)
        self.activation2 = nn.ReLU()
        self.conv3 = nn.Conv3d(24, 24, kernel_size= (7, 1, 1), stride= 1, padding= (3, 0, 0), padding_mode = 'replicate', bias= True)
        self.bn3 = nn.BatchNorm3d(24)
        self.activation3 = nn.ReLU()
        # Finish
        
        # Convolution Layer 2 kernel_size = (1, 1, (self.feature_dim - 6) // 2), output channels = 128
        self.conv4 = nn.Conv3d(24, 128, kernel_size= (((self.feature_dim - 7) // 2 + 1), 1, 1), bias = True)
        self.bn4 = nn.BatchNorm3d(128)
        self.activation4 = nn.ReLU()
        
        # Convolution layer for spatial information
        self.conv5 = nn.Conv3d(1, 24, (self.feature_dim, 1, 1))
        self.bn5 = nn.BatchNorm3d(24)
        self.activation5 = nn.ReLU()
        

        # Residual block 2
        self.conv6 = nn.Conv3d(24, 24, kernel_size= (1, 3, 3), stride= 1, padding= (0, 1, 1), padding_mode = 'replicate', bias= True)
        self.bn6 = nn.BatchNorm3d(24)
        self.activation6 = nn.ReLU()
        self.conv7 = nn.Conv3d(24, 24, kernel_size= (1, 3, 3), stride= 1, padding= (0, 1, 1), padding_mode = 'replicate', bias= True)
        self.bn7 = nn.BatchNorm3d(24)
        self.activation7 = nn.ReLU()
        self.conv8 = nn.Conv3d(24, 24, kernel_size= 1)
        # Finish
        
        # Combination shape
        self.inter_size = 128 + 24
        
        # Residual block 3
        self.conv9 = nn.Conv3d(self.inter_size, self.inter_size, kernel_size= (1, 3, 3), stride= 1, padding= (0, 1, 1), padding_mode = 'replicate', bias= True)
        self.bn9 = nn.BatchNorm3d(self.inter_size)
        self.activation9 = nn.ReLU()
        self.conv10 = nn.Conv3d(self.inter_size, self.inter_size, kernel_size= (1, 3, 3), stride= 1, padding= (0, 1, 1), padding_mode = 'replicate', bias= True)
        self.bn10 = nn.BatchNorm3d(self.inter_size)
        self.activation10 = nn.ReLU()

        # Average pooling kernel_size = (5, 5, 1)
        self.avgpool = nn.AvgPool3d((1, self.sz, self.sz))

        # Fully connected Layer
        self.fc1 = nn.Linear(in_features= self.inter_size, out_features= n_classes)

        # parameters initialization
        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                torch.nn.init.kaiming_normal_(m.weight.data)
                m.bias.data.zero_()            
            elif isinstance(m, nn.BatchNorm3d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def forward(self, x, bounds=None):
        # Convolution layer 1
        x1 = self.conv1(x)
        x1 = self.activation1(self.bn1(x1))
        # Residual layer 1
        residual = x1
        x1 = self.conv2(x1)
        x1 = self.activation2(self.bn2(x1))
        x1 = self.conv3(x1)
        x1 = residual + x1
        x1 = self.activation3(self.bn3(x1))

        # Convolution layer to combine rest 
        x1 = self.conv4(x1)
        x1 = self.activation4(self.bn4(x1))
        x1 = x1.reshape(x1.size(0),x1.size(1), x1.size(3), x1.size(4))
        
        x2 = self.conv5(x)
        x2 = self.activation5(self.bn5(x2))

        # Residual layer 2
        residual = x2
        residual = self.conv8(residual)
        x2 = self.conv6(x2)
        x2 = self.activation6(self.bn6(x2))
        x2 = self.conv7(x2)
        x2 = residual + x2

        x2 = self.activation7(self.bn7(x2))
        x2 = x2.reshape(x2.size(0),x2.size(1), x2.size(3), x2.size(4))
        
        # concat spatial and spectral information
        x = torch.cat((x1, x2), 1)        
        
        x = self.avgpool(x)
        x = x.reshape((x.size(0), -1))

        # Fully connected layer
        x = self.fc1(x)

        return x
    
class LiEtAl(nn.Module):
    """
    SPECTRAL–SPATIAL CLASSIFICATION OF HYPERSPECTRAL IMAGERY
            WITH 3D CONVOLUTIONAL NEURAL NETWORK
    Ying Li, Haokui Zhang and Qiang Shen
    MDPI Remote Sensing, 2017
    http://www.mdpi.com/2072-4292/9/1/67
    """
    @staticmethod
    def weight_init(m):
        if isinstance(m, nn.Linear) or isinstance(m, nn.Conv3d):
            nn.init.xavier_uniform_(m.weight.data)
            nn.init.constant_(m.bias.data, 0)

    def __init__(self, input_channels, n_classes, n_planes=2, patch_size=5):
        super(LiEtAl, self).__init__()
        self.input_channels = input_channels
        self.n_planes = n_planes
        self.patch_size = patch_size

        # The proposed 3D-CNN model has two 3D convolution layers (C1 and C2)
        # and a fully-connected layer (F1)
        # we fix the spatial size of the 3D convolution kernels to 3 × 3
        # while only slightly varying the spectral depth of the kernels
        # for the Pavia University and Indian Pines scenes, those in C1 and C2
        # were set to seven and three, respectively
        self.conv1 = nn.Conv3d(1, n_planes, (7, 3, 3), padding=(1, 0, 0))
        # the number of kernels in the second convolution layer is set to be
        # twice as many as that in the first convolution layer
        self.conv2 = nn.Conv3d(n_planes, 2 * n_planes,
                               (3, 3, 3), padding=(1, 0, 0))
        #self.dropout = nn.Dropout(p=0.5)
        self.features_size = self._get_final_flattened_size()

        self.fc = nn.Linear(self.features_size, n_classes)

        self.apply(self.weight_init)

    def _get_final_flattened_size(self):
        with torch.no_grad():
            x = torch.zeros((1, 1, self.input_channels,
                             self.patch_size, self.patch_size))
            x = self.conv1(x)
            x = self.conv2(x)
            _, t, c, w, h = x.size()
        return t * c * w * h

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, self.features_size)
        #x = self.dropout(x)
        x = self.fc(x)
        return x
    
############################################################### HetConv ###################################################
   
class conv_block(nn.Module):  # pytorch
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 padding,
                 use_1x1conv=False,
                 stride=1):
        super(conv_block, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(
                in_channels,
                out_channels,
                kernel_size=kernel_size,
                padding=padding,
                stride=stride), nn.ReLU())

        self.bn = nn.BatchNorm3d(out_channels)

    def forward(self, X):
        Y = F.relu(self.bn(self.conv(X)))
        return Y
    
  
class HetConv(nn.Module):
    def __init__(self, classes):
        super(HetConv, self).__init__()
        self.name = 'HetConv'

        self.conv_net1 = conv_block(1, 24, (1, 1, 7), (0, 0, 3))
        self.conv_net2 = conv_block(24, 24, (1, 1, 7), (0, 0, 3))
        self.conv_net3 = conv_block(24, 24, (1, 1, 7), (0, 0, 3))
        self.conv_net4 = conv_block(1, 24, (3, 3, 1), (1, 1, 0))
        self.conv_net5 = conv_block(24, 24, (3, 3, 1), (1, 1, 0))
        self.conv_net6 = conv_block(24, 24, (3, 3, 1), (1, 1, 0))

        self.avg_pooling = nn.AvgPool3d(kernel_size=(5, 5, 1))
        self.full_connection = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(6720, classes)  # ,
            # nn.Softmax()
        )

    def forward(self, X):
        x2 = self.conv_net1(X)
        x2_ = self.conv_net4(X)
        x2 = x2 + x2_
        x3 = self.conv_net2(x2)
        x3_ = self.conv_net5(x2)
        x3 = x3 + x3_
        x4 = self.conv_net3(x2)
        x4_ = self.conv_net6(x2)
        x4 = x4 + x4_
        x5 = self.avg_pooling(x4)
        x5 = x5.view(x5.size(0), -1)
        return self.full_connection(x5)
