"""
MIT License

Copyright (c) 2025 Sagar Gosai, Rodrigo Castro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse

import torch
import torch.nn as nn

import lightning.pytorch as ptl

from .custom_layers import Conv1dNorm, LinearNorm, GroupedLinear, BranchedLinear
from .loss_functions import add_criterion_specific_args
import nucleobench.models.malinois.model.utils as utils

from ..model import loss_functions

def get_padding(kernel_size):
    """
    Calculate padding values for convolutional layers.

    Args:
        kernel_size (int): Size of the convolutional kernel.

    Returns:
        list: Padding values for left and right sides of the kernel.
    """
    left = (kernel_size - 1) // 2
    right= kernel_size - 1 - left
    return [ max(0,x) for x in [left,right] ]

##################
#     Models     #
##################
        
class Basset(ptl.LightningModule):
    """
    Basset model architecture.

    Args:
        conv1_channels (int): Number of output channels in the first convolutional layer.
        conv1_kernel_size (int): Kernel size of the first convolutional layer.
        conv2_channels (int): Number of output channels in the second convolutional layer.
        conv2_kernel_size (int): Kernel size of the second convolutional layer.
        conv3_channels (int): Number of output channels in the third convolutional layer.
        conv3_kernel_size (int): Kernel size of the third convolutional layer.
        linear1_channels (int): Number of output channels in the first linear layer.
        linear2_channels (int): Number of output channels in the second linear layer.
        n_outputs (int): Number of output classes.
        activation (str): Activation function name.
        dropout_p (float): Dropout probability.
        use_batch_norm (bool): Whether to use batch normalization.
        use_weight_norm (bool): Whether to use weight normalization.
        loss_criterion (str): Loss criterion name.

    Methods:
        add_model_specific_args(parent_parser): Add model-specific arguments to the argument parser.
        add_conditional_args(parser, known_args): Add conditional arguments based on known arguments.
        process_args(grouped_args): Process grouped arguments and return model-specific arguments.
        encode(x): Encode input through the Basset model's encoding layers.
        decode(x): Decode encoded tensor through the Basset model's decoding layers.
        classify(x): Classify decoded tensor using the Basset model's classification layer.
        forward(x): Forward pass through the Basset model.
    """
    
    #####################
    # CLI staticmethods #
    #####################
    
    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Add model-specific arguments to the argument parser.

        Args:
            parent_parser (argparse.ArgumentParser): Parent argument parser.

        Returns:
            argparse.ArgumentParser: Argument parser with added model-specific arguments.
        """
        parser = argparse.ArgumentParser(parents=[parent_parser], add_help=False)
        group  = parser.add_argument_group('Model Module args')
        
        group.add_argument('--conv1_channels', type=int, default=300)
        group.add_argument('--conv1_kernel_size', type=int, default=19)
        
        group.add_argument('--conv2_channels', type=int, default=200)
        group.add_argument('--conv2_kernel_size', type=int, default=11)
        
        group.add_argument('--conv3_channels', type=int, default=200)
        group.add_argument('--conv3_kernel_size', type=int, default=7)
        
        group.add_argument('--linear1_channels', type=int, default=1000)
        group.add_argument('--linear2_channels', type=int, default=1000)
        group.add_argument('--n_outputs', type=int, default=280)
        
        group.add_argument('--dropout_p', type=float, default=0.3)
        group.add_argument('--use_batch_norm', type=utils.str2bool, default=True)
        group.add_argument('--use_weight_norm',type=utils.str2bool, default=False)
        
        group.add_argument('--loss_criterion',type=str, default='CrossEntropyLoss')
        
        return parser
    
    @staticmethod
    def add_conditional_args(parser, known_args):
        """
        Add conditional arguments based on known arguments.

        Args:
            parser (argparse.ArgumentParser): Argument parser.
            known_args (Namespace): Namespace of known arguments.

        Returns:
            argparse.ArgumentParser: Argument parser with added conditional arguments.
        """
        parser = add_criterion_specific_args(parser, known_args.loss_criterion)
        return parser

    @staticmethod
    def process_args(grouped_args):
        """
        Perform any required processessing of command line args required 
        before passing to the class constructor.

        Args:
            grouped_args (Namespace): Namespace of known arguments with 
            `'Model Module args'` key and conditionally added 
            `'Criterion args'` key.

        Returns:
            Namespace: A modified namespace that can be passed to the 
            associated class constructor.
        """
        model_args   = grouped_args['Model Module args']
        model_args.loss_args = vars(grouped_args['Criterion args'])
        return model_args

    ######################
    # Model construction #
    ######################
    
    def __init__(self, conv1_channels=300, conv1_kernel_size=19, 
                 conv2_channels=200, conv2_kernel_size=11, 
                 conv3_channels=200, conv3_kernel_size=7, 
                 linear1_channels=1000, linear2_channels=1000, 
                 n_outputs=280, activation='ReLU', 
                 dropout_p=0.3, use_batch_norm=True, use_weight_norm=False,
                 loss_criterion='CrossEntropyLoss', loss_args={}):
        """
        Initialize Basset model.

        Args:
            conv1_channels (int): Number of output channels in the first convolutional layer.
            conv1_kernel_size (int): Kernel size of the first convolutional layer.
            conv2_channels (int): Number of output channels in the second convolutional layer.
            conv2_kernel_size (int): Kernel size of the second convolutional layer.
            conv3_channels (int): Number of output channels in the third convolutional layer.
            conv3_kernel_size (int): Kernel size of the third convolutional layer.
            linear1_channels (int): Number of output channels in the first linear layer.
            linear2_channels (int): Number of output channels in the second linear layer.
            n_outputs (int): Number of output classes.
            activation (str): Activation function name.
            dropout_p (float): Dropout probability.
            use_batch_norm (bool): Whether to use batch normalization.
            use_weight_norm (bool): Whether to use weight normalization.
            loss_criterion (str): Loss criterion name.
            loss_args (dict): Dict of kwargs to construct loss with.
        """                                         
        super().__init__()        
        
        self.conv1_channels    = conv1_channels
        self.conv1_kernel_size = conv1_kernel_size
        self.conv1_pad = get_padding(conv1_kernel_size)
        
        self.conv2_channels    = conv2_channels
        self.conv2_kernel_size = conv2_kernel_size
        self.conv2_pad = get_padding(conv2_kernel_size)

        
        self.conv3_channels    = conv3_channels
        self.conv3_kernel_size = conv3_kernel_size
        self.conv3_pad = get_padding(conv3_kernel_size)
        
        self.linear1_channels  = linear1_channels
        self.linear2_channels  = linear2_channels
        self.n_outputs         = n_outputs
        
        self.activation        = activation
        
        self.dropout_p         = dropout_p
        self.use_batch_norm    = use_batch_norm
        self.use_weight_norm   = use_weight_norm
        
        self.loss_criterion    = loss_criterion
        self.loss_args         = loss_args
        
        self.pad1  = nn.ConstantPad1d(self.conv1_pad, 0.)
        self.conv1 = Conv1dNorm(4, 
                                self.conv1_channels, self.conv1_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad2  = nn.ConstantPad1d(self.conv2_pad, 0.)
        self.conv2 = Conv1dNorm(self.conv1_channels, 
                                self.conv2_channels, self.conv2_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad3  = nn.ConstantPad1d(self.conv3_pad, 0.)
        self.conv3 = Conv1dNorm(self.conv2_channels, 
                                self.conv3_channels, self.conv3_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        
        self.pad4 = nn.ConstantPad1d((1,1), 0.)

        self.maxpool_3 = nn.MaxPool1d(3, padding=0)
        self.maxpool_4 = nn.MaxPool1d(4, padding=0)
        
        self.linear1 = LinearNorm(self.conv3_channels*13, self.linear1_channels, 
                                  bias=True, 
                                  batch_norm=self.use_batch_norm, 
                                  weight_norm=self.use_weight_norm)
        self.linear2 = LinearNorm(self.linear1_channels, self.linear2_channels, 
                                  bias=True, 
                                  batch_norm=self.use_batch_norm, 
                                  weight_norm=self.use_weight_norm)
        self.output  = nn.Linear(self.linear2_channels, self.n_outputs)
        
        self.nonlin  = getattr(nn, self.activation)()                               
        
        self.dropout = nn.Dropout(p=self.dropout_p)
        
        self.criterion = getattr(loss_functions,self.loss_criterion) \
                         (**self.loss_args)
        
    ######################
    # Model computations #
    ######################
    
    def encode(self, x):
        """
        Encode input through the Basset model's encoding layers.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Encoded tensor.
        """
        hook = self.nonlin( self.conv1( self.pad1( x ) ) )
        hook = self.maxpool_3( hook )
        hook = self.nonlin( self.conv2( self.pad2( hook ) ) )
        hook = self.maxpool_4( hook )
        hook = self.nonlin( self.conv3( self.pad3( hook ) ) )
        hook = self.maxpool_4( self.pad4( hook ) )        
        hook = torch.flatten( hook, start_dim=1 )
        return hook
    
    def decode(self, x):
        """
        Decode encoded tensor through the Basset model's decoding layers.

        Args:
            x (torch.Tensor): Encoded tensor.

        Returns:
            torch.Tensor: Decoded tensor.
        """
        hook = self.dropout( self.nonlin( self.linear1( x ) ) )
        hook = self.dropout( self.nonlin( self.linear2( hook ) ) )
        return hook
    
    def classify(self, x):
        """
        Classify decoded tensor using the Basset model's classification layer.

        Args:
            x (torch.Tensor): Decoded tensor.

        Returns:
            torch.Tensor: Classification output tensor.
        """
        output = self.output( x )
        return output
        
    def forward(self, x):
        """
        Forward pass through the Basset model.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor.
        """
        encoded = self.encode(x)
        decoded = self.decode(encoded)
        output  = self.classify(decoded)
        return output

class BassetVL(ptl.LightningModule):
    """
    BassetVL (Variant of Basset with Variable Linear Layers) model architecture.

    Args:
        conv1_channels (int): Number of output channels in the first convolutional layer.
        conv1_kernel_size (int): Kernel size of the first convolutional layer.
        conv2_channels (int): Number of output channels in the second convolutional layer.
        conv2_kernel_size (int): Kernel size of the second convolutional layer.
        conv3_channels (int): Number of output channels in the third convolutional layer.
        conv3_kernel_size (int): Kernel size of the third convolutional layer.
        n_linear_layers (int): Number of linear layers.
        linear_channels (int): Number of output channels in linear layers.
        n_outputs (int): Number of output classes.
        activation (str): Activation function name.
        dropout_p (float): Dropout probability.
        use_batch_norm (bool): Whether to use batch normalization.
        use_weight_norm (bool): Whether to use weight normalization.
        loss_criterion (str): Loss criterion name.

    Methods:
        add_model_specific_args(parent_parser): Add model-specific arguments to the argument parser.
        add_conditional_args(parser, known_args): Add conditional arguments based on known arguments.
        process_args(grouped_args): Process grouped arguments to extract model-specific arguments.
        encode(x): Encode input through the BassetVL model's encoding layers.
        decode(x): Decode encoded tensor through the BassetVL model's decoding layers.
        classify(x): Classify decoded tensor using the BassetVL model's classification layer.
        forward(x): Forward pass through the BassetVL model.
    """
    
    #####################
    # CLI staticmethods #
    #####################
    
    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Add model-specific arguments to the argument parser.

        Args:
            parent_parser (argparse.ArgumentParser): Parent argument parser.

        Returns:
            argparse.ArgumentParser: Argument parser with added model-specific arguments.
        """
        parser = argparse.ArgumentParser(parents=[parent_parser], add_help=False)
        group  = parser.add_argument_group('Model Module args')
        
        group.add_argument('--input_len', type=int, default=600)

        group.add_argument('--conv1_channels', type=int, default=300)
        group.add_argument('--conv1_kernel_size', type=int, default=19)
        
        group.add_argument('--conv2_channels', type=int, default=200)
        group.add_argument('--conv2_kernel_size', type=int, default=11)
        
        group.add_argument('--conv3_channels', type=int, default=200)
        group.add_argument('--conv3_kernel_size', type=int, default=7)
        
        group.add_argument('--n_linear_layers', type=int, default=2)
        group.add_argument('--linear_channels', type=int, default=1000)
        group.add_argument('--linear_activation',type=str, default='ReLU')
        group.add_argument('--linear_dropout_p', type=float, default=0.3)

        group.add_argument('--n_outputs', type=int, default=280)

        group.add_argument('--use_batch_norm', type=utils.str2bool, default=True)
        group.add_argument('--use_weight_norm',type=utils.str2bool, default=False)
        
        group.add_argument('--loss_criterion',type=str, default='CrossEntropyLoss')
        
        return parser
    
    @staticmethod
    def add_conditional_args(parser, known_args):
        """
        Add conditional arguments based on known arguments.

        Args:
            parser (argparse.ArgumentParser): Argument parser.
            known_args (Namespace): Namespace of known arguments.

        Returns:
            argparse.ArgumentParser: Argument parser with added conditional arguments.
        """
        parser = add_criterion_specific_args(parser, known_args.loss_criterion)
        return parser

    @staticmethod
    def process_args(grouped_args):
        """
        Perform any required processessing of command line args required 
        before passing to the class constructor.

        Args:
            grouped_args (Namespace): Namespace of known arguments with 
            `'Model Module args'` key and conditionally added 
            `'Criterion args'` key.

        Returns:
            Namespace: A modified namespace that can be passed to the 
            associated class constructor.
        """
        model_args   = grouped_args['Model Module args']
        model_args.loss_args = vars(grouped_args['Criterion args'])
        return model_args

    ######################
    # Model construction #
    ######################
    
    def __init__(self, input_len=600,
                 conv1_channels=300, conv1_kernel_size=19, 
                 conv2_channels=200, conv2_kernel_size=11, 
                 conv3_channels=200, conv3_kernel_size=7, 
                 n_linear_layers=2, linear_channels=1000, 
                 linear_activation='ReLU', linear_dropout_p=0.3, 
                 n_outputs=280, 
                 use_batch_norm=True, use_weight_norm=False,
                 loss_criterion='MSELoss', loss_args={}):   
        """
        Initialize BassetVL model.

        Args:
            conv1_channels (int): Number of output channels in the first convolutional layer.
            conv1_kernel_size (int): Kernel size of the first convolutional layer.
            conv2_channels (int): Number of output channels in the second convolutional layer.
            conv2_kernel_size (int): Kernel size of the second convolutional layer.
            conv3_channels (int): Number of output channels in the third convolutional layer.
            conv3_kernel_size (int): Kernel size of the third convolutional layer.
            n_linear_layers (int): Number of linear layers.
            linear_channels (int): Number of output channels in linear layers.
            n_outputs (int): Number of output classes.
            linear_activation (str): Activation function name.
            linear_dropout_p (float): Dropout probability.
            use_batch_norm (bool): Whether to use batch normalization.
            use_weight_norm (bool): Whether to use weight normalization.
            loss_criterion (str): Loss criterion name.
        """                                             
        super().__init__()        
        
        self.input_len         = input_len
        
        self.conv1_channels    = conv1_channels
        self.conv1_kernel_size = conv1_kernel_size
        self.conv1_pad = get_padding(conv1_kernel_size)
        
        self.conv2_channels    = conv2_channels
        self.conv2_kernel_size = conv2_kernel_size
        self.conv2_pad = get_padding(conv2_kernel_size)

        
        self.conv3_channels    = conv3_channels
        self.conv3_kernel_size = conv3_kernel_size
        self.conv3_pad = get_padding(conv3_kernel_size)
        
        self.n_linear_layers   = n_linear_layers
        self.linear_channels   = linear_channels
        self.n_outputs         = n_outputs
        
        self.linear_activation = linear_activation        
        self.linear_dropout_p  = linear_dropout_p
        
        self.use_batch_norm    = use_batch_norm
        self.use_weight_norm   = use_weight_norm
        
        self.loss_criterion    = loss_criterion
        self.loss_args         = loss_args
        
        self.pad1  = nn.ConstantPad1d(self.conv1_pad, 0.)
        self.conv1 = Conv1dNorm(4, 
                                self.conv1_channels, self.conv1_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad2  = nn.ConstantPad1d(self.conv2_pad, 0.)
        self.conv2 = Conv1dNorm(self.conv1_channels, 
                                self.conv2_channels, self.conv2_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad3  = nn.ConstantPad1d(self.conv3_pad, 0.)
        self.conv3 = Conv1dNorm(self.conv2_channels, 
                                self.conv3_channels, self.conv3_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        
        self.pad4 = nn.ConstantPad1d((1,1), 0.)

        self.maxpool_3 = nn.MaxPool1d(3, padding=0)
        self.maxpool_4 = nn.MaxPool1d(4, padding=0)
        
        next_in_channels = self.conv3_channels * self.get_flatten_factor(self.input_len)
        
        for i in range(self.n_linear_layers):
            
            setattr(self, f'linear{i+1}', 
                    LinearNorm(next_in_channels, self.linear_channels, 
                               bias=True, 
                               batch_norm=self.use_batch_norm, 
                               weight_norm=self.use_weight_norm)
                   )
            next_in_channels = self.linear_channels

        self.output  = nn.Linear(next_in_channels, self.n_outputs)
        
        self.nonlin  = getattr(nn, self.linear_activation)()                               
        
        self.dropout = nn.Dropout(p=self.linear_dropout_p)
        
        self.criterion = getattr(loss_functions,self.loss_criterion) \
                         (**self.loss_args)
        
    def get_flatten_factor(self, input_len):
        
        hook = input_len
        assert hook % 3 == 0
        hook = hook // 3
        assert hook % 4 == 0
        hook = hook // 4
        assert (hook + 2) % 4 == 0
        
        return (hook + 2) // 4

    ######################
    # Model computations #
    ######################
    
    def encode(self, x):
        """
        Encode input through the BassetVL model's encoding layers.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Encoded tensor.
        """
        hook = self.nonlin( self.conv1( self.pad1( x ) ) )
        hook = self.maxpool_3( hook )
        hook = self.nonlin( self.conv2( self.pad2( hook ) ) )
        hook = self.maxpool_4( hook )
        hook = self.nonlin( self.conv3( self.pad3( hook ) ) )
        hook = self.maxpool_4( self.pad4( hook ) )        
        hook = torch.flatten( hook, start_dim=1 )
        return hook
    
    def decode(self, x):
        """
        Decode encoded tensor through the BassetVL model's decoding layers.

        Args:
            x (torch.Tensor): Encoded tensor.

        Returns:
            torch.Tensor: Decoded tensor.
        """
        hook = x
        for i in range(self.n_linear_layers):
            hook = self.dropout( 
                self.nonlin( 
                    getattr(self,f'linear{i+1}')(hook)
                )
            )
        return hook
    
    def classify(self, x):
        """
        Classify decoded tensor using the BassetVL model's classification layer.

        Args:
            x (torch.Tensor): Decoded tensor.

        Returns:
            torch.Tensor: Classification output tensor.
        """
        output = self.output( x )
        return output
        
    def forward(self, x):
        """
        Forward pass through the BassetVL model.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor.
        """
        encoded = self.encode(x)
        decoded = self.decode(encoded)
        output  = self.classify(decoded)
        return output

class BassetEntropyVL(ptl.LightningModule):
    """
    Deprecated, redundant to updated BassetVL. 
    A custom LightningModule implementing the Basset model with entropy-based loss and variation loss.

    Args:
        conv1_channels (int): Number of channels in the first convolutional layer.
        conv1_kernel_size (int): Kernel size of the first convolutional layer.
        conv2_channels (int): Number of channels in the second convolutional layer.
        conv2_kernel_size (int): Kernel size of the second convolutional layer.
        conv3_channels (int): Number of channels in the third convolutional layer.
        conv3_kernel_size (int): Kernel size of the third convolutional layer.
        n_linear_layers (int): Number of linear layers in the model.
        linear_channels (int): Number of channels in the linear layers.
        n_outputs (int): Number of output units.
        activation (str): Activation function to use.
        dropout_p (float): Dropout probability applied to hidden layers.
        use_batch_norm (bool): Whether to use batch normalization.
        use_weight_norm (bool): Whether to use weight normalization.
        criterion_reduction (str): Reduction method for the combined loss.
        mse_scale (float): Scale factor for the MSE loss.
        kl_scale (float): Scale factor for the KL loss.

    Methods:
        add_model_specific_args(parent_parser): Add model-specific arguments to the provided argparse ArgumentParser.
        add_conditional_args(parser, known_args): Add conditional model-specific arguments based on known arguments.
        process_args(grouped_args): Process grouped arguments and extract model-specific arguments.
        forward(x): Perform forward pass through the BassetEntropyVL model.
        encode(x): Encode input data through the convolutional layers.
        decode(x): Decode encoded data through the linear layers.
        classify(x): Generate model predictions from decoded data.

    Example:
        model = BassetEntropyVL(conv1_channels=300, conv1_kernel_size=19,
                                conv2_channels=200, conv2_kernel_size=11,
                                conv3_channels=200, conv3_kernel_size=7,
                                n_linear_layers=2, linear_channels=1000,
                                n_outputs=280, activation='ReLU',
                                dropout_p=0.3, use_batch_norm=True, use_weight_norm=False,
                                criterion_reduction='mean', mse_scale=1.0, kl_scale=1.0)
        output = model(input_tensor)
    """
    
    #####################
    # CLI staticmethods #
    #####################
    
    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Add model-specific arguments to the argument parser.
    
        Args:
            parent_parser (argparse.ArgumentParser): Parent argument parser.
    
        Returns:
            argparse.ArgumentParser: Argument parser with added model-specific arguments.
        """
        parser = argparse.ArgumentParser(parents=[parent_parser], add_help=False)
        group  = parser.add_argument_group('Model Module args')
        
        group.add_argument('--conv1_channels', type=int, default=300)
        group.add_argument('--conv1_kernel_size', type=int, default=19)
        
        group.add_argument('--conv2_channels', type=int, default=200)
        group.add_argument('--conv2_kernel_size', type=int, default=11)
        
        group.add_argument('--conv3_channels', type=int, default=200)
        group.add_argument('--conv3_kernel_size', type=int, default=7)
        
        group.add_argument('--n_linear_layers', type=int, default=2)
        group.add_argument('--linear_channels', type=int, default=1000)
        group.add_argument('--n_outputs', type=int, default=280)
        
        group.add_argument('--dropout_p', type=float, default=0.3)
        group.add_argument('--use_batch_norm', type=utils.str2bool, default=True)
        group.add_argument('--use_weight_norm',type=utils.str2bool, default=False)
        
        group.add_argument('--criterion_reduction', type=str, default='mean')
        group.add_argument('--mse_scale', type=float, default=1.0)
        group.add_argument('--kl_scale', type=float, default=1.0)
                
        return parser
    
    @staticmethod
    def add_conditional_args(parser, known_args):
        """
        Add conditional model-specific arguments based on known arguments.
    
        Args:
            parser (argparse.ArgumentParser): Argument parser to which conditional arguments will be added.
            known_args (Namespace): Namespace containing known arguments.
    
        Returns:
            argparse.ArgumentParser: Argument parser with added conditional arguments.
        """
        return parser

    @staticmethod
    def process_args(grouped_args):
        """
        Process grouped arguments and extract model-specific arguments.
    
        Args:
            grouped_args (dict): Dictionary of grouped arguments.
    
        Returns:
            dict: Model-specific arguments extracted from grouped_args.
        """
        model_args   = grouped_args['Model Module args']
        return model_args

    ######################
    # Model construction #
    ######################
    
    def __init__(self, conv1_channels=300, conv1_kernel_size=19, 
                 conv2_channels=200, conv2_kernel_size=11, 
                 conv3_channels=200, conv3_kernel_size=7, 
                 n_linear_layers=2, linear_channels=1000, 
                 n_outputs=280, activation='ReLU', 
                 dropout_p=0.3, use_batch_norm=True, use_weight_norm=False,
                 criterion_reduction='mean', mse_scale=1.0, kl_scale=1.0):
        """
        Initialize the BassetEntropyVL module.

        Args:
            conv1_channels (int): Number of channels in the first convolutional layer.
            conv1_kernel_size (int): Kernel size of the first convolutional layer.
            conv2_channels (int): Number of channels in the second convolutional layer.
            conv2_kernel_size (int): Kernel size of the second convolutional layer.
            conv3_channels (int): Number of channels in the third convolutional layer.
            conv3_kernel_size (int): Kernel size of the third convolutional layer.
            n_linear_layers (int): Number of linear layers in the model.
            linear_channels (int): Number of channels in the linear layers.
            n_outputs (int): Number of output units.
            activation (str): Activation function to use.
            dropout_p (float): Dropout probability applied to hidden layers.
            use_batch_norm (bool): Whether to use batch normalization.
            use_weight_norm (bool): Whether to use weight normalization.
            criterion_reduction (str): Reduction method for the combined loss.
            mse_scale (float): Scale factor for the MSE loss.
            kl_scale (float): Scale factor for the KL loss.

        Returns:
            None
        """                                            
        super().__init__()        
        
        self.conv1_channels    = conv1_channels
        self.conv1_kernel_size = conv1_kernel_size
        self.conv1_pad = get_padding(conv1_kernel_size)
        
        self.conv2_channels    = conv2_channels
        self.conv2_kernel_size = conv2_kernel_size
        self.conv2_pad = get_padding(conv2_kernel_size)

        
        self.conv3_channels    = conv3_channels
        self.conv3_kernel_size = conv3_kernel_size
        self.conv3_pad = get_padding(conv3_kernel_size)
        
        self.n_linear_layers   = n_linear_layers
        self.linear_channels   = linear_channels
        self.n_outputs         = n_outputs
        
        self.activation        = activation
        
        self.dropout_p         = dropout_p
        self.use_batch_norm    = use_batch_norm
        self.use_weight_norm   = use_weight_norm
        
        self.criterion_reduction=criterion_reduction
        self.mse_scale         = mse_scale
        self.kl_scale          = kl_scale
        
        self.pad1  = nn.ConstantPad1d(self.conv1_pad, 0.)
        self.conv1 = Conv1dNorm(4, 
                                self.conv1_channels, self.conv1_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad2  = nn.ConstantPad1d(self.conv2_pad, 0.)
        self.conv2 = Conv1dNorm(self.conv1_channels, 
                                self.conv2_channels, self.conv2_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad3  = nn.ConstantPad1d(self.conv3_pad, 0.)
        self.conv3 = Conv1dNorm(self.conv2_channels, 
                                self.conv3_channels, self.conv3_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        
        self.pad4 = nn.ConstantPad1d((1,1), 0.)

        self.maxpool_3 = nn.MaxPool1d(3, padding=0)
        self.maxpool_4 = nn.MaxPool1d(4, padding=0)
        
        next_in_channels = self.conv3_channels*13
        
        for i in range(self.n_linear_layers):
            
            setattr(self, f'linear{i+1}', 
                    LinearNorm(next_in_channels, self.linear_channels, 
                               bias=True, 
                               batch_norm=self.use_batch_norm, 
                               weight_norm=self.use_weight_norm)
                   )
            next_in_channels = self.linear_channels

        self.output  = nn.Linear(next_in_channels, self.n_outputs)
        
        self.nonlin  = getattr(nn, self.activation)()                               
        
        self.dropout = nn.Dropout(p=self.dropout_p)
        
        self.criterion = MSEKLmixed(reduction=self.criterion_reduction,
                                    mse_scale=self.mse_scale,
                                    kl_scale =self.kl_scale)
        
    ######################
    # Model computations #
    ######################
    
    def encode(self, x):
        """
        Encode input data through the convolutional layers.

        Args:
            x (Tensor): The input tensor.

        Returns:
            Tensor: Encoded tensor.
        """
        hook = self.nonlin( self.conv1( self.pad1( x ) ) )
        hook = self.maxpool_3( hook )
        hook = self.nonlin( self.conv2( self.pad2( hook ) ) )
        hook = self.maxpool_4( hook )
        hook = self.nonlin( self.conv3( self.pad3( hook ) ) )
        hook = self.maxpool_4( self.pad4( hook ) )        
        hook = torch.flatten( hook, start_dim=1 )
        return hook
    
    def decode(self, x):
        """
        Decode encoded data through the linear layers.

        Args:
            x (Tensor): The encoded tensor.

        Returns:
            Tensor: Decoded tensor.
        """
        hook = x
        for i in range(self.n_linear_layers):
            hook = self.dropout( 
                self.nonlin( 
                    getattr(self,f'linear{i+1}')(hook)
                )
            )
        return hook
    
    def classify(self, x):
        """
        Generate model predictions from decoded data.

        Args:
            x (Tensor): The decoded tensor.

        Returns:
            Tensor: Model predictions.
        """
        output = self.output( x )
        return output
        
    def forward(self, x):
        """
        Perform forward pass through the BassetEntropyVL model.

        Args:
            x (Tensor): The input tensor.

        Returns:
            Tensor: Model predictions.
        """
        encoded = self.encode(x)
        decoded = self.decode(encoded)
        output  = self.classify(decoded)
        return output

class BassetBranched(ptl.LightningModule):
    """
    A PyTorch Lightning module representing the BassetBranched model.

    Args:
        input_len (int): Fixed sequence length of inputs.
        conv1_channels (int): Number of channels for the first convolutional layer.
        conv1_kernel_size (int): Kernel size for the first convolutional layer.
        conv2_channels (int): Number of channels for the second convolutional layer.
        conv2_kernel_size (int): Kernel size for the second convolutional layer.
        conv3_channels (int): Number of channels for the third convolutional layer.
        conv3_kernel_size (int): Kernel size for the third convolutional layer.
        n_linear_layers (int): Number of linear (fully connected) layers.
        linear_channels (int): Number of channels in linear layers.
        linear_activation (str): Activation function for linear layers (default: 'ReLU').
        linear_dropout_p (float): Dropout probability for linear layers (default: 0.3).
        n_branched_layers (int): Number of branched linear layers.
        branched_channels (int): Number of output channels for branched layers.
        branched_activation (str): Activation function for branched layers (default: 'ReLU6').
        branched_dropout_p (float): Dropout probability for branched layers (default: 0.0).
        n_outputs (int): Number of output units.
        loss_criterion (str): Loss criterion class name (default: 'MSEKLmixed').
        criterion_reduction (str): Reduction type for loss criterion (default: 'mean').
        mse_scale (float): Scale factor for MSE loss component (default: 1.0).
        kl_scale (float): Scale factor for KL divergence loss component (default: 1.0).
        use_batch_norm (bool): Use batch normalization (default: True).
        use_weight_norm (bool): Use weight normalization (default: False).

    Methods:
        add_model_specific_args(parent_parser): Add model-specific arguments to the provided argparse ArgumentParser.
        add_conditional_args(parser, known_args): Add conditional model-specific arguments based on known arguments.
        process_args(grouped_args): Process grouped arguments and extract model-specific arguments.
        encode(x): Encode input data through the model's encoder layers.
        decode(x): Decode encoded data through the model's linear and branched layers.
        classify(x): Classify data using the output layer.
        forward(x): Forward pass through the entire model.

    """
    
    #####################
    # CLI staticmethods #
    #####################
    
    @staticmethod
    def add_model_specific_args(parent_parser):
        """
        Add model-specific arguments to the provided argparse ArgumentParser.

        Args:
            parent_parser (argparse.ArgumentParser): The parent ArgumentParser.

        Returns:
            argparse.ArgumentParser: The ArgumentParser with added model-specific arguments.
        """
        parser = argparse.ArgumentParser(parents=[parent_parser], add_help=False)
        group  = parser.add_argument_group('Model Module args')
        
        group.add_argument('--input_len', type=int, default=600)
        
        group.add_argument('--conv1_channels', type=int, default=300)
        group.add_argument('--conv1_kernel_size', type=int, default=19)
        
        group.add_argument('--conv2_channels', type=int, default=200)
        group.add_argument('--conv2_kernel_size', type=int, default=11)
        
        group.add_argument('--conv3_channels', type=int, default=200)
        group.add_argument('--conv3_kernel_size', type=int, default=7)
        
        group.add_argument('--n_linear_layers', type=int, default=2)
        group.add_argument('--linear_channels', type=int, default=1000)
        group.add_argument('--linear_activation',type=str, default='ReLU')
        group.add_argument('--linear_dropout_p', type=float, default=0.3)

        group.add_argument('--n_branched_layers', type=int, default=1)
        group.add_argument('--branched_channels', type=int, default=1000)
        group.add_argument('--branched_activation',type=str, default='ReLU')
        group.add_argument('--branched_dropout_p', type=float, default=0.3)

        group.add_argument('--n_outputs', type=int, default=280)
        
        group.add_argument('--use_batch_norm', type=utils.str2bool, default=True)
        group.add_argument('--use_weight_norm',type=utils.str2bool, default=False)
        
        group.add_argument('--loss_criterion', type=str, default='L1KLmixed')
                
        return parser
    
    @staticmethod
    def add_conditional_args(parser, known_args):
        """
        Add conditional arguments based on known arguments.

        Args:
            parser (argparse.ArgumentParser): Argument parser.
            known_args (Namespace): Namespace of known arguments.

        Returns:
            argparse.ArgumentParser: Argument parser with added conditional arguments.
        """
        parser = add_criterion_specific_args(parser, known_args.loss_criterion)
        return parser

    @staticmethod
    def process_args(grouped_args):
        """
        Perform any required processessing of command line args required 
        before passing to the class constructor.

        Args:
            grouped_args (Namespace): Namespace of known arguments with 
            `'Model Module args'` key and conditionally added 
            `'Criterion args'` key.

        Returns:
            Namespace: A modified namespace that can be passed to the 
            associated class constructor.
        """
        model_args   = grouped_args['Model Module args']
        model_args.loss_args = vars(grouped_args['Criterion args'])
        return model_args

    ######################
    # Model construction #
    ######################
    
    def __init__(self, input_len=600,
                 conv1_channels=300, conv1_kernel_size=19, 
                 conv2_channels=200, conv2_kernel_size=11, 
                 conv3_channels=200, conv3_kernel_size=7, 
                 n_linear_layers=2, linear_channels=1000, 
                 linear_activation='ReLU', linear_dropout_p=0.3, 
                 n_branched_layers=1, branched_channels=250, 
                 branched_activation='ReLU6', branched_dropout_p=0., 
                 n_outputs=280,
                 use_batch_norm=True, use_weight_norm=False, 
                 loss_criterion='L1KLmixed', loss_args={}):
        """
        Initialize the BassetBranched model.
    
        Args:
            conv1_channels (int): Number of channels for the first convolutional layer.
            conv1_kernel_size (int): Kernel size for the first convolutional layer.
            conv2_channels (int): Number of channels for the second convolutional layer.
            conv2_kernel_size (int): Kernel size for the second convolutional layer.
            conv3_channels (int): Number of channels for the third convolutional layer.
            conv3_kernel_size (int): Kernel size for the third convolutional layer.
            n_linear_layers (int): Number of linear (fully connected) layers.
            linear_channels (int): Number of channels in linear layers.
            linear_activation (str): Activation function for linear layers (default: 'ReLU').
            linear_dropout_p (float): Dropout probability for linear layers (default: 0.3).
            n_branched_layers (int): Number of branched linear layers.
            branched_channels (int): Number of output channels for branched layers.
            branched_activation (str): Activation function for branched layers (default: 'ReLU6').
            branched_dropout_p (float): Dropout probability for branched layers (default: 0.0).
            n_outputs (int): Number of output units.
            loss_criterion (str): Loss criterion class name (default: 'MSEKLmixed').
            loss_args (dict): Args to construct loss_criterion.
            use_batch_norm (bool): Use batch normalization (default: True).
            use_weight_norm (bool): Use weight normalization (default: False).
        """                                               
        super().__init__()        
        
        self.input_len         = input_len
        
        self.conv1_channels    = conv1_channels
        self.conv1_kernel_size = conv1_kernel_size
        self.conv1_pad = get_padding(conv1_kernel_size)
        
        self.conv2_channels    = conv2_channels
        self.conv2_kernel_size = conv2_kernel_size
        self.conv2_pad = get_padding(conv2_kernel_size)

        
        self.conv3_channels    = conv3_channels
        self.conv3_kernel_size = conv3_kernel_size
        self.conv3_pad = get_padding(conv3_kernel_size)
        
        self.n_linear_layers   = n_linear_layers
        self.linear_channels   = linear_channels
        self.linear_activation = linear_activation
        self.linear_dropout_p  = linear_dropout_p
        
        self.n_branched_layers = n_branched_layers
        self.branched_channels = branched_channels
        self.branched_activation = branched_activation
        self.branched_dropout_p= branched_dropout_p
        
        self.n_outputs         = n_outputs
        
        self.loss_criterion    = loss_criterion
        self.loss_args         = loss_args
        
        self.use_batch_norm    = use_batch_norm
        self.use_weight_norm   = use_weight_norm
        
        self.pad1  = nn.ConstantPad1d(self.conv1_pad, 0.)
        self.conv1 = Conv1dNorm(4, 
                                self.conv1_channels, self.conv1_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad2  = nn.ConstantPad1d(self.conv2_pad, 0.)
        self.conv2 = Conv1dNorm(self.conv1_channels, 
                                self.conv2_channels, self.conv2_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        self.pad3  = nn.ConstantPad1d(self.conv3_pad, 0.)
        self.conv3 = Conv1dNorm(self.conv2_channels, 
                                self.conv3_channels, self.conv3_kernel_size, 
                                stride=1, padding=0, dilation=1, groups=1, 
                                bias=True, 
                                batch_norm=self.use_batch_norm, 
                                weight_norm=self.use_weight_norm)
        
        self.pad4 = nn.ConstantPad1d((1,1), 0.)

        self.maxpool_3 = nn.MaxPool1d(3, padding=0)
        self.maxpool_4 = nn.MaxPool1d(4, padding=0)
        
        next_in_channels = self.conv3_channels * self.get_flatten_factor(self.input_len)
        
        for i in range(self.n_linear_layers):
            
            setattr(self, f'linear{i+1}', 
                    LinearNorm(next_in_channels, self.linear_channels, 
                               bias=True, 
                               batch_norm=self.use_batch_norm, 
                               weight_norm=self.use_weight_norm)
                   )
            next_in_channels = self.linear_channels

        self.branched = BranchedLinear(next_in_channels, self.branched_channels, 
                                       self.branched_channels, 
                                       self.n_outputs, self.n_branched_layers, 
                                       self.branched_activation, self.branched_dropout_p)
            
        self.output  = GroupedLinear(self.branched_channels, 1, self.n_outputs)
        
        self.nonlin  = getattr(nn, self.linear_activation)()                               
        
        self.dropout = nn.Dropout(p=self.linear_dropout_p)
        
        self.criterion = getattr(loss_functions,self.loss_criterion) \
                         (**self.loss_args)
    
    def get_flatten_factor(self, input_len):
        
        
        
        hook = input_len
        assert hook % 3 == 0
        hook = hook // 3
        assert hook % 4 == 0
        hook = hook // 4
        assert (hook + 2) % 4 == 0
        
        return (hook + 2) // 4
    
    ######################
    # Model computations #
    ######################
    
    def encode(self, x):
        """
        Encode input data through the model's encoder layers.

        Args:
            x (torch.Tensor): Input data tensor.

        Returns:
            torch.Tensor: Encoded representation of the input data.
        """
        hook = self.nonlin( self.conv1( self.pad1( x ) ) )
        hook = self.maxpool_3( hook )
        hook = self.nonlin( self.conv2( self.pad2( hook ) ) )
        hook = self.maxpool_4( hook )
        hook = self.nonlin( self.conv3( self.pad3( hook ) ) )
        hook = self.maxpool_4( self.pad4( hook ) )        
        hook = torch.flatten( hook, start_dim=1 )
        return hook
    
    def decode(self, x):
        """
        Decode encoded data through the model's linear and branched layers.

        Args:
            x (torch.Tensor): Encoded data tensor.

        Returns:
            torch.Tensor: Decoded representation of the input data.
        """
        hook = x
        for i in range(self.n_linear_layers):
            hook = self.dropout( 
                self.nonlin( 
                    getattr(self,f'linear{i+1}')(hook)
                )
            )
        hook = self.branched(hook)

        return hook
    
    def classify(self, x):
        """
        Classify data using the output layer.

        Args:
            x (torch.Tensor): Data tensor to be classified.

        Returns:
            torch.Tensor: Classified output tensor.
        """
        output = self.output( x )
        return output
        
    def forward(self, x):
        """
        Forward pass through the entire model.

        Args:
            x (torch.Tensor): Input data tensor.

        Returns:
            torch.Tensor: Model's output tensor.
        """
        encoded = self.encode(x)
        decoded = self.decode(encoded)
        output  = self.classify(decoded)
        return output